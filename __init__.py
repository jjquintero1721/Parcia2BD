# __init__.py
from flask import Flask
import os
from config import Config
from extensions import db, login_manager
from datetime import datetime


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    
    # Asegurar que el directorio de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Registrar blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.product import product_bp
    from routes.review import review_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(product_bp, url_prefix='/productos')
    app.register_blueprint(review_bp, url_prefix='/resenas')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Crear tablas de la base de datos si no existen
    with app.app_context():
        db.create_all()
        
    @app.context_processor
    def inject_now():
        return {'current_year': datetime.utcnow().year}
    
    return app

# Al final de la función create_app, antes de return app
    
    # Registrar filtros personalizados
    @app.template_filter('date')
    def date_filter(date):
        """Filtro para formatear fechas"""
        if date is None:
            return ""
        return date.strftime('%d-%m-%Y')
    
    return app