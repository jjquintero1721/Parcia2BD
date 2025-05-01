from extensions import db
from datetime import datetime
from sqlalchemy.orm import validates

class Resena(db.Model):
    __tablename__ = 'resenas'
    
    resena_id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    calificacion = db.Column(db.Numeric(2, 1), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ciudad_declarada = db.Column(db.String(100), nullable=False)
    ip_capturada = db.Column(db.String(45), nullable=False)
    coincide_ubicacion = db.Column(db.Boolean, default=False)
    estado = db.Column(db.Enum('aprobada', 'pendiente', 'rechazada'), default='pendiente')
    
    @validates('calificacion')
    def validate_calificacion(self, key, calificacion):
        # Ensure rating is between 0.5 and 5 in 0.5 increments
        if calificacion < 0.5 or calificacion > 5 or (calificacion * 2) != round(calificacion * 2):
            raise ValueError("La calificación debe estar entre 0.5 y 5 en incrementos de 0.5")
        return calificacion
    
    def estrellas_texto(self):
        """Convert numerical rating to star symbols"""
        rating_map = {
            5.0: '★★★★★',
            4.5: '★★★★½',
            4.0: '★★★★☆',
            3.5: '★★★½☆',
            3.0: '★★★☆☆',
            2.5: '★★½☆☆',
            2.0: '★★☆☆☆',
            1.5: '★½☆☆☆',
            1.0: '★☆☆☆☆',
            0.5: '½☆☆☆☆'
        }
        return rating_map.get(float(self.calificacion), '☆☆☆☆☆')
    
    def verificar_coincidencia_ip(self):
        """Check if the IP matches the declared location"""
        # This would call the stored procedure in a real implementation
        # For now, we'll leave it as a placeholder
        pass
    
    def __repr__(self):
        return f'<Resena {self.resena_id} - {self.calificacion}>'


class Like(db.Model):
    __tablename__ = 'likes'
    
    like_id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)
    tipo = db.Column(db.Enum('like', 'dislike'), default='like', nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Like {self.tipo} for producto_id={self.producto_id}>'