from extensions import db
from datetime import datetime

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    categoria_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.Enum('activa', 'inactiva'), default='activa')
    
    # Relationships
    productos = db.relationship('Producto', backref='categoria', lazy='dynamic')
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'