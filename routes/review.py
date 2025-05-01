from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.producto import Producto
from models.resena import Resena
from models.ubicacion import Ubicacion
from forms.review import ReviewForm
from extensions import db
import socket

review_bp = Blueprint('review', __name__)

@review_bp.route('/crear/<int:producto_id>', methods=['GET', 'POST'])
@login_required
def create(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    
    # Check if user already reviewed this product
    existing_review = Resena.query.filter_by(
        producto_id=producto_id,
        usuario_id=current_user.usuario_id
    ).first()
    
    if existing_review:
        flash('Ya has escrito una reseña para este producto', 'warning')
        return redirect(url_for('product.detail', producto_id=producto_id))
    
    form = ReviewForm()
    
    # Populate city choices for the dropdown
    form.ciudad_declarada.choices = [
        (ciudad.ciudad, ciudad.ciudad) 
        for ciudad in Ubicacion.query.with_entities(Ubicacion.ciudad).distinct()
    ]
    
    if form.validate_on_submit():
        try:
            # Get client IP
            client_ip = request.remote_addr
            
            resena = Resena(
                producto_id=producto_id,
                usuario_id=current_user.usuario_id,
                contenido=form.contenido.data,
                calificacion=form.calificacion.data,
                ciudad_declarada=form.ciudad_declarada.data,
                ip_capturada=client_ip,
                estado='pendiente'
            )
            
            db.session.add(resena)
            db.session.commit()
            
            # Verify IP location match (would call stored procedure in production)
            # resena.verificar_coincidencia_ip()
            
            flash('Tu reseña ha sido enviada y está pendiente de aprobación', 'success')
            return redirect(url_for('product.detail', producto_id=producto_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la reseña: {str(e)}', 'danger')
    
    return render_template('reviews/create.html', form=form, producto=producto)

@review_bp.route('/editar/<int:resena_id>', methods=['GET', 'POST'])
@login_required
def edit(resena_id):
    resena = Resena.query.get_or_404(resena_id)
    
    # Make sure user owns this review
    if resena.usuario_id != current_user.usuario_id:
        flash('No tienes permiso para editar esta reseña', 'danger')
        return redirect(url_for('product.detail', producto_id=resena.producto_id))
    
    # Only allow editing of pending or approved reviews
    if resena.estado == 'rechazada':
        flash('No puedes editar una reseña que ha sido rechazada', 'warning')
        return redirect(url_for('product.detail', producto_id=resena.producto_id))
    
    form = ReviewForm()
    
    # Populate city choices for the dropdown
    form.ciudad_declarada.choices = [
        (ciudad.ciudad, ciudad.ciudad) 
        for ciudad in Ubicacion.query.with_entities(Ubicacion.ciudad).distinct()
    ]
    
    if request.method == 'GET':
        form.contenido.data = resena.contenido
        form.calificacion.data = float(resena.calificacion)
        form.ciudad_declarada.data = resena.ciudad_declarada
    
    if form.validate_on_submit():
        try:
            resena.contenido = form.contenido.data
            resena.calificacion = form.calificacion.data
            resena.ciudad_declarada = form.ciudad_declarada.data
            resena.estado = 'pendiente'  # Reset to pending when edited
            
            # Get client IP
            client_ip = request.remote_addr
            resena.ip_capturada = client_ip
            
            db.session.commit()
            
            # Verify IP location match (would call stored procedure in production)
            # resena.verificar_coincidencia_ip()
            
            flash('Tu reseña ha sido actualizada y está pendiente de aprobación', 'success')
            return redirect(url_for('product.detail', producto_id=resena.producto_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la reseña: {str(e)}', 'danger')
    
    producto = Producto.query.get(resena.producto_id)
    return render_template('reviews/edit.html', form=form, resena=resena, producto=producto)

@review_bp.route('/eliminar/<int:resena_id>', methods=['POST'])
@login_required
def delete(resena_id):
    resena = Resena.query.get_or_404(resena_id)
    
    # Make sure user owns this review
    if resena.usuario_id != current_user.usuario_id:
        flash('No tienes permiso para eliminar esta reseña', 'danger')
        return redirect(url_for('product.detail', producto_id=resena.producto_id))
    
    producto_id = resena.producto_id
    
    try:
        db.session.delete(resena)
        db.session.commit()
        flash('Tu reseña ha sido eliminada', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la reseña: {str(e)}', 'danger')
    
    return redirect(url_for('product.detail', producto_id=producto_id))

@review_bp.route('/mis-resenas')
@login_required
def my_reviews():
    page = request.args.get('page', 1, type=int)
    
    resenas = Resena.query.filter_by(
        usuario_id=current_user.usuario_id
    ).order_by(
        Resena.fecha_creacion.desc()
    ).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    return render_template('reviews/my_reviews.html', resenas=resenas)

@review_bp.route('/actualizar-calificacion/<int:resena_id>', methods=['POST'])
@login_required
def update_rating(resena_id):
    resena = Resena.query.get_or_404(resena_id)
    
    # Make sure user owns this review
    if resena.usuario_id != current_user.usuario_id:
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    # Get new rating
    try:
        new_rating = float(request.form.get('calificacion', 0))
        if new_rating < 0.5 or new_rating > 5 or (new_rating * 2) != round(new_rating * 2):
            return jsonify({'success': False, 'message': 'Calificación inválida'})
        
        # Update rating (would call stored procedure in production)
        resena.calificacion = new_rating
        resena.estado = 'pendiente'  # Reset to pending when edited
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Calificación actualizada',
            'estrellas': resena.estrellas_texto()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})