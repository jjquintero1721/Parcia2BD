from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models.user import Usuario
from models.producto import Producto, ProductoImagen
from models.categoria import Categoria
from models.resena import Resena
from models.ubicacion import Ubicacion, RangoIP
from forms.admin import (
    ProductForm, CategoryForm, ReviewApprovalForm, 
    ImageUploadForm, UserForm, UbicacionForm, RangoIPForm
)
from extensions import db

admin_bp = Blueprint('admin', __name__)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is an admin (change this based on your user model)
        if not current_user.is_authenticated or current_user.email != 'admin@example.com':
            flash('Acceso denegado: se requiere privilegios de administrador', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    # Dashboard stats
    total_productos = Producto.query.count()
    total_usuarios = Usuario.query.count()
    total_resenas = Resena.query.count()
    resenas_pendientes = Resena.query.filter_by(estado='pendiente').count()
    
    # Recent activities
    recent_products = Producto.query.order_by(Producto.fecha_publicacion.desc()).limit(5).all()
    recent_reviews = Resena.query.order_by(Resena.fecha_creacion.desc()).limit(5).all()
    recent_users = Usuario.query.order_by(Usuario.fecha_registro.desc()).limit(5).all()
    
    return render_template(
        'admin/index.html',
        total_productos=total_productos,
        total_usuarios=total_usuarios,
        total_resenas=total_resenas,
        resenas_pendientes=resenas_pendientes,
        recent_products=recent_products,
        recent_reviews=recent_reviews,
        recent_users=recent_users
    )

# Product management
@admin_bp.route('/productos')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    productos = Producto.query.order_by(Producto.fecha_publicacion.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/products/index.html', productos=productos)

@admin_bp.route('/productos/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def create_product():
    form = ProductForm()
    
    # Populate category choices
    form.categoria_id.choices = [
        (c.categoria_id, c.nombre) 
        for c in Categoria.query.filter_by(estado='activa').all()
    ]
    
    if form.validate_on_submit():
        # Handle image upload
        imagen_url = None
        if form.imagen.data:
            filename = secure_filename(form.imagen.data.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'productos', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            form.imagen.data.save(file_path)
            imagen_url = '/static/uploads/productos/' + filename
        
        producto = Producto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            categoria_id=form.categoria_id.data,
            ficha_tecnica=form.ficha_tecnica.data,
            imagen_url=imagen_url,
            estado=form.estado.data
        )
        
        db.session.add(producto)
        db.session.commit()
        
        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/products/create.html', form=form)

@admin_bp.route('/productos/<int:producto_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    form = ProductForm()
    
    # Populate category choices
    form.categoria_id.choices = [
        (c.categoria_id, c.nombre) 
        for c in Categoria.query.filter_by(estado='activa').all()
    ]
    
    if request.method == 'GET':
        form.nombre.data = producto.nombre
        form.descripcion.data = producto.descripcion
        form.categoria_id.data = producto.categoria_id
        form.ficha_tecnica.data = producto.ficha_tecnica
        form.estado.data = producto.estado
    
    if form.validate_on_submit():
        # Handle image upload
        if form.imagen.data:
            filename = secure_filename(form.imagen.data.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'productos', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            form.imagen.data.save(file_path)
            producto.imagen_url = '/static/uploads/productos/' + filename
        
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.categoria_id = form.categoria_id.data
        producto.ficha_tecnica = form.ficha_tecnica.data
        producto.estado = form.estado.data
        
        db.session.commit()
        
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/products/edit.html', form=form, producto=producto)

@admin_bp.route('/productos/<int:producto_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete_product(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar producto: {str(e)}', 'danger')
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/productos/<int:producto_id>/imagenes', methods=['GET', 'POST'])
@login_required
@admin_required
def product_images(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    imagenes = ProductoImagen.query.filter_by(producto_id=producto_id).order_by(
        ProductoImagen.es_principal.desc(),
        ProductoImagen.orden.asc()
    ).all()
    
    form = ImageUploadForm()
    
    if form.validate_on_submit():
        # Handle image upload
        if form.imagen.data:
            filename = secure_filename(form.imagen.data.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'productos', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            form.imagen.data.save(file_path)
            
            # Create new image
            imagen = ProductoImagen(
                producto_id=producto_id,
                url_imagen='/static/uploads/productos/' + filename,
                titulo=form.titulo.data,
                es_principal=form.es_principal.data,
                orden=form.orden.data
            )
            
            # If this is set as principal, remove principal flag from others
            if form.es_principal.data:
                ProductoImagen.query.filter_by(
                    producto_id=producto_id, 
                    es_principal=True
                ).update({'es_principal': False})
            
            db.session.add(imagen)
            db.session.commit()
            
            flash('Imagen agregada exitosamente', 'success')
            return redirect(url_for('admin.product_images', producto_id=producto_id))
    
    return render_template(
        'admin/products/images.html',
        producto=producto,
        imagenes=imagenes,
        form=form
    )

@admin_bp.route('/productos/imagenes/<int:imagen_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete_image(imagen_id):
    imagen = ProductoImagen.query.get_or_404(imagen_id)
    producto_id = imagen.producto_id
    
    try:
        db.session.delete(imagen)
        db.session.commit()
        flash('Imagen eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar imagen: {str(e)}', 'danger')
    
    return redirect(url_for('admin.product_images', producto_id=producto_id))

# Category management
@admin_bp.route('/categorias')
@login_required
@admin_required
def categories():
    categorias = Categoria.query.all()
    return render_template('admin/categories/index.html', categorias=categorias)

@admin_bp.route('/categorias/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def create_category():
    form = CategoryForm()
    
    if form.validate_on_submit():
        categoria = Categoria(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            estado=form.estado.data
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        flash('Categoría creada exitosamente', 'success')
        return redirect(url_for('admin.categories'))
        
    return render_template('admin/categories/create.html', form=form)

@admin_bp.route('/categorias/<int:categoria_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    form = CategoryForm()
    
    if request.method == 'GET':
        form.nombre.data = categoria.nombre
        form.descripcion.data = categoria.descripcion
        form.estado.data = categoria.estado
    
    if form.validate_on_submit():
        categoria.nombre = form.nombre.data
        categoria.descripcion = form.descripcion.data
        categoria.estado = form.estado.data
        
        db.session.commit()
        
        flash('Categoría actualizada exitosamente', 'success')
        return redirect(url_for('admin.categories'))
        
    return render_template('admin/categories/edit.html', form=form, categoria=categoria)

# Review management
@admin_bp.route('/resenas')
@login_required
@admin_required
def reviews():
    estado = request.args.get('estado', 'pendiente')
    page = request.args.get('page', 1, type=int)
    
    resenas = Resena.query.filter_by(estado=estado).order_by(
        Resena.fecha_creacion.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/reviews/index.html', resenas=resenas, estado_actual=estado)

@admin_bp.route('/resenas/<int:resena_id>/revisar', methods=['GET', 'POST'])
@login_required
@admin_required
def review_approval(resena_id):
    resena = Resena.query.get_or_404(resena_id)
    producto = Producto.query.get(resena.producto_id)
    usuario = Usuario.query.get(resena.usuario_id)
    
    form = ReviewApprovalForm()
    
    if request.method == 'GET':
        form.estado.data = resena.estado
    
    if form.validate_on_submit():
        resena.estado = form.estado.data
        
        # If the review is approved and IP verification not done yet, do it
        if form.estado.data == 'aprobada' and not resena.coincide_ubicacion:
            # This would call the stored procedure in production
            # resena.verificar_coincidencia_ip()
            pass
        
        db.session.commit()
        
        flash('Estado de la reseña actualizado', 'success')
        return redirect(url_for('admin.reviews', estado=resena.estado))
    
    return render_template(
        'admin/reviews/approval.html',
        resena=resena,
        producto=producto,
        usuario=usuario,
        form=form
    )

# User management
@admin_bp.route('/usuarios')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users/index.html', usuarios=usuarios)

@admin_bp.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UserForm()
    
    if request.method == 'GET':
        form.nombre.data = usuario.nombre
        form.email.data = usuario.email
        form.estado.data = usuario.estado
    
    if form.validate_on_submit():
        usuario.nombre = form.nombre.data
        
        # If email changed, check if it already exists
        if form.email.data != usuario.email:
            if Usuario.query.filter_by(email=form.email.data).first():
                flash('Este email ya está en uso', 'danger')
                return redirect(url_for('admin.edit_user', usuario_id=usuario_id))
            usuario.email = form.email.data
        
        usuario.estado = form.estado.data
        
        # Update password if provided
        if form.password.data:
            usuario.set_password(form.password.data)
        
        db.session.commit()
        
        flash('Usuario actualizado exitosamente', 'success')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/users/edit.html', form=form, usuario=usuario)

# Statistics
@admin_bp.route('/estadisticas')
@login_required
@admin_required
def statistics():
    # Get statistics for reviews by category (would call stored procedure in production)
    stats = db.session.query(
        Categoria.nombre.label('categoria'),
        db.func.count(db.distinct(Producto.producto_id)).label('total_productos'),
        db.func.count(Resena.resena_id).label('total_resenas'),
        db.func.avg(Resena.calificacion).label('calificacion_promedio'),
        db.func.count(db.distinct(Resena.usuario_id)).label('total_usuarios_distintos')
    ).outerjoin(
        Producto, Categoria.categoria_id == Producto.categoria_id
    ).outerjoin(
        Resena, Producto.producto_id == Resena.producto_id
    ).group_by(
        Categoria.categoria_id
    ).order_by(
        db.func.count(Resena.resena_id).desc()
    ).all()
    
    return render_template('admin/statistics.html', stats=stats)

# Location management
@admin_bp.route('/ubicaciones')
@login_required
@admin_required
def locations():
    ubicaciones = Ubicacion.query.all()
    return render_template('admin/locations/index.html', ubicaciones=ubicaciones)

@admin_bp.route('/ubicaciones/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def create_location():
    form = UbicacionForm()
    
    if form.validate_on_submit():
        ubicacion = Ubicacion(
            ciudad=form.ciudad.data,
            departamento=form.departamento.data,
            pais=form.pais.data,
            codigo_postal=form.codigo_postal.data
        )
        
        db.session.add(ubicacion)
        db.session.commit()
        
        flash('Ubicación creada exitosamente', 'success')
        return redirect(url_for('admin.locations'))
        
    return render_template('admin/locations/create.html', form=form)

@admin_bp.route('/ubicaciones/<int:ubicacion_id>/rangos_ip')
@login_required
@admin_required
def ip_ranges(ubicacion_id):
    ubicacion = Ubicacion.query.get_or_404(ubicacion_id)
    rangos = RangoIP.query.filter_by(ubicacion_id=ubicacion_id).all()
    
    return render_template(
        'admin/locations/ip_ranges.html',
        ubicacion=ubicacion,
        rangos=rangos
    )

@admin_bp.route('/ubicaciones/<int:ubicacion_id>/rangos_ip/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def create_ip_range(ubicacion_id):
    ubicacion = Ubicacion.query.get_or_404(ubicacion_id)
    form = RangoIPForm()
    
    if form.validate_on_submit():
        rango = RangoIP(
            ip_inicio=form.ip_inicio.data,
            ip_fin=form.ip_fin.data,
            ubicacion_id=ubicacion_id
        )
        
        db.session.add(rango)
        db.session.commit()
        
        flash('Rango IP creado exitosamente', 'success')
        return redirect(url_for('admin.ip_ranges', ubicacion_id=ubicacion_id))
        
    return render_template(
        'admin/locations/create_ip_range.html',
        form=form,
        ubicacion=ubicacion
    )