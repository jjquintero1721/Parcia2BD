from extensions import db

class Ubicacion(db.Model):
    __tablename__ = 'ubicaciones'
    
    ubicacion_id = db.Column(db.Integer, primary_key=True)
    ciudad = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(50), default='Colombia', nullable=False)
    codigo_postal = db.Column(db.String(20))
    
    # Relationships
    rangos_ip = db.relationship('RangoIP', backref='ubicacion', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ubicacion {self.ciudad}, {self.departamento}>'


class RangoIP(db.Model):
    __tablename__ = 'rangos_ip'
    
    rango_id = db.Column(db.Integer, primary_key=True)
    ip_inicio = db.Column(db.String(45), nullable=False)
    ip_fin = db.Column(db.String(45), nullable=False)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.ubicacion_id'), nullable=False)
    
    def __repr__(self):
        return f'<RangoIP {self.ip_inicio} - {self.ip_fin}>'