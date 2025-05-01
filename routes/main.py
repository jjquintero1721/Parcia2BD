from flask import Blueprint, render_template, request, current_app
from models.producto import Producto
from models.categoria import Categoria
from models.resena import Resena
from extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    productos = Producto.query.filter_by(estado='activo').order_by(
        Producto.fecha_publicacion.desc()
    ).paginate(
        page=page, 
        per_page=current_app.config['PRODUCTS_PER_PAGE'], 
        error_out=False
    )
    
    categorias = Categoria.query.filter_by(estado='activa').all()
    
    # Get featured products (highest rated with at least 3 reviews)
    destacados_subq = db.session.query(
        Resena.producto_id,
        db.func.avg(Resena.calificacion).label('avg_rating'),
        db.func.count(Resena.resena_id).label('review_count')
    ).filter(
        Resena.estado == 'aprobada'
    ).group_by(
        Resena.producto_id
    ).having(
        db.func.count(Resena.resena_id) >= 3
    ).subquery()
    
    productos_destacados = db.session.query(
        Producto
    ).join(
        destacados_subq, 
        Producto.producto_id == destacados_subq.c.producto_id
    ).filter(
        Producto.estado == 'activo'
    ).order_by(
        destacados_subq.c.avg_rating.desc(),
        destacados_subq.c.review_count.desc()
    ).limit(6).all()
    
    return render_template(
        'home.html', 
        productos=productos,
        categorias=categorias,
        productos_destacados=productos_destacados
    )

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return render_template('search.html', productos=None, query=query)
    
    productos = Producto.query.filter(
        Producto.estado == 'activo',
        db.or_(
            Producto.nombre.ilike(f'%{query}%'),
            Producto.descripcion.ilike(f'%{query}%')
        )
    ).order_by(
        Producto.fecha_publicacion.desc()
    ).paginate(
        page=page, 
        per_page=current_app.config['PRODUCTS_PER_PAGE'], 
        error_out=False
    )
    
    return render_template('search.html', productos=productos, query=query)