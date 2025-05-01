from extensions import db
from datetime import datetime

class Producto(db.Model):
    __tablename__ = 'productos'
    
    producto_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.categoria_id'))
    ficha_tecnica = db.Column(db.Text)
    imagen_url = db.Column(db.String(255))
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.Enum('activo', 'inactivo'), default='activo')
    
    # Relationships
    imagenes = db.relationship('ProductoImagen', backref='producto', lazy='dynamic', cascade='all, delete-orphan')
    resenas = db.relationship('Resena', backref='producto', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='producto', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def promedio_calificacion(self):
        resenas_aprobadas = [r for r in self.resenas if r.estado == 'aprobada']
        if not resenas_aprobadas:
            return 0
        return sum(r.calificacion for r in resenas_aprobadas) / len(resenas_aprobadas)
    
    @property
    def total_resenas(self):
        return self.resenas.filter_by(estado='aprobada').count()
    
    @property
    def imagen_principal(self):
        principal = self.imagenes.filter_by(es_principal=True).first()
        if principal:
            return principal.url_imagen
        return self.imagen_url or '/static/img/no-image.jpg'
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'


class ProductoImagen(db.Model):
    __tablename__ = 'producto_imagenes'
    
    imagen_id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=False)
    url_imagen = db.Column(db.String(255), nullable=False)
    titulo = db.Column(db.String(100))
    es_principal = db.Column(db.Boolean, default=False)
    orden = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductoImagen {self.titulo or "Sin título"}>'