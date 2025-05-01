from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func, desc
from models.producto import Producto, ProductoImagen
from models.categoria import Categoria
from models.resena import Resena, Like
from forms.product import SearchForm
from extensions import db

product_bp = Blueprint('product', __name__)

@product_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    categoria_id = request.args.get('categoria', None, type=int)
    
    query = Producto.query.filter_by(estado='activo')
    
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
        
    productos = query.order_by(Producto.fecha_publicacion.desc()).paginate(
        page=page, 
        per_page=current_app.config['PRODUCTS_PER_PAGE'], 
        error_out=False
    )
    
    categorias = Categoria.query.filter_by(estado='activa').all()
    
    return render_template(
        'products/index.html',
        productos=productos,
        categorias=categorias,
        categoria_actual=categoria_id
    )

@product_bp.route('/<int:producto_id>')
def detail(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    imagenes = ProductoImagen.query.filter_by(producto_id=producto_id).order_by(
        ProductoImagen.es_principal.desc(),
        ProductoImagen.orden.asc()
    ).all()
    
    page = request.args.get('page', 1, type=int)
    resenas = Resena.query.filter_by(
        producto_id=producto_id,
        estado='aprobada'
    ).order_by(
        Resena.fecha_creacion.desc()
    ).paginate(
        page=page,
        per_page=current_app.config['REVIEWS_PER_PAGE'],
        error_out=False
    )
    
    # Get distribution of ratings
    rating_distribution = db.session.query(
        Resena.calificacion,
        func.count(Resena.resena_id)
    ).filter(
        Resena.producto_id == producto_id,
        Resena.estado == 'aprobada'
    ).group_by(
        Resena.calificacion
    ).order_by(
        desc(Resena.calificacion)
    ).all()
    
    # Check if current user has liked this product
    user_like = None
    if current_user.is_authenticated:
        user_like = Like.query.filter_by(
            producto_id=producto_id,
            usuario_id=current_user.usuario_id
        ).first()
    
    # Get total likes/dislikes
    likes_count = Like.query.filter_by(
        producto_id=producto_id,
        tipo='like'
    ).count()
    
    dislikes_count = Like.query.filter_by(
        producto_id=producto_id,
        tipo='dislike'
    ).count()
    
    return render_template(
        'products/detail.html',
        producto=producto,
        imagenes=imagenes,
        resenas=resenas,
        rating_distribution=rating_distribution,
        user_like=user_like,
        likes_count=likes_count,
        dislikes_count=dislikes_count
    )

@product_bp.route('/<int:producto_id>/like', methods=['POST'])
@login_required
def like_product(producto_id):
    tipo = request.form.get('tipo', 'like')
    if tipo not in ['like', 'dislike']:
        tipo = 'like'
    
    # Check if product exists
    producto = Producto.query.get_or_404(producto_id)
    
    # Check if user already liked/disliked this product
    existing_like = Like.query.filter_by(
        producto_id=producto_id,
        usuario_id=current_user.usuario_id
    ).first()
    
    if existing_like:
        if existing_like.tipo == tipo:
            # Remove the like if clicking the same button
            db.session.delete(existing_like)
            db.session.commit()
            return jsonify({'status': 'removed'})
        else:
            # Change like type if different
            existing_like.tipo = tipo
            db.session.commit()
            return jsonify({'status': 'changed', 'tipo': tipo})
    else:
        # Create new like
        new_like = Like(
            producto_id=producto_id,
            usuario_id=current_user.usuario_id,
            tipo=tipo
        )
        db.session.add(new_like)
        db.session.commit()
        return jsonify({'status': 'added', 'tipo': tipo})

@product_bp.route('/populares')
def popular():
    # Get popular products (most likes and best ratings)
    page = request.args.get('page', 1, type=int)
    
    # Subquery to count likes per product
    likes_subq = db.session.query(
        Like.producto_id,
        func.count(Like.like_id).label('likes_count')
    ).filter(
        Like.tipo == 'like'
    ).group_by(
        Like.producto_id
    ).subquery()
    
    # Subquery to get average rating per product
    ratings_subq = db.session.query(
        Resena.producto_id,
        func.avg(Resena.calificacion).label('avg_rating'),
        func.count(Resena.resena_id).label('reviews_count')
    ).filter(
        Resena.estado == 'aprobada'
    ).group_by(
        Resena.producto_id
    ).subquery()
    
    # Join products with these subqueries
    query = db.session.query(
        Producto,
        func.coalesce(likes_subq.c.likes_count, 0).label('likes_count'),
        func.coalesce(ratings_subq.c.avg_rating, 0).label('avg_rating'),
        func.coalesce(ratings_subq.c.reviews_count, 0).label('reviews_count')
    ).outerjoin(
        likes_subq,
        Producto.producto_id == likes_subq.c.producto_id
    ).outerjoin(
        ratings_subq,
        Producto.producto_id == ratings_subq.c.producto_id
    ).filter(
        Producto.estado == 'activo'
    )
    
    # Calculate a popularity score
    # 60% rating + 40% likes with min 3 reviews
    productos = query.filter(
        func.coalesce(ratings_subq.c.reviews_count, 0) >= 3
    ).order_by(
        (0.6 * func.coalesce(ratings_subq.c.avg_rating, 0) / 5 + 
         0.4 * func.coalesce(likes_subq.c.likes_count, 0) / 10).desc()
    ).paginate(
        page=page,
        per_page=current_app.config['PRODUCTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('products/popular.html', productos=productos)

@product_bp.route('/mejores')
def best_rated():
    # Get best rated products (with min 5 reviews)
    page = request.args.get('page', 1, type=int)
    min_reviews = int(request.args.get('min_reviews', 5))
    
    # Call the stored procedure (simulated here with SQLAlchemy)
    best_products = db.session.query(
        Producto.producto_id,
        Producto.nombre.label('nombre_producto'),
        Producto.descripcion,
        Producto.imagen_url,
        func.count(Resena.resena_id).label('total_resenas'),
        func.avg(Resena.calificacion).label('promedio_estrellas'),
        func.round(func.avg(Resena.calificacion) * 2) / 2
    ).join(
        Resena, Producto.producto_id == Resena.producto_id
    ).filter(
        Resena.estado == 'aprobada',
        Producto.estado == 'activo'
    ).group_by(
        Producto.producto_id,
        Producto.nombre,
        Producto.descripcion,
        Producto.imagen_url
    ).having(
        func.count(Resena.resena_id) >= min_reviews
    ).order_by(
        func.avg(Resena.calificacion).desc(),
        func.count(Resena.resena_id).desc()
    ).paginate(
        page=page,
        per_page=current_app.config['PRODUCTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template(
        'products/best_rated.html',
        productos=best_products,
        min_reviews=min_reviews
    )