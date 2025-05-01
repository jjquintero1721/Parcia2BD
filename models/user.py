from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    usuario_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    estado = db.Column(db.Enum('activo', 'inactivo'), default='activo')
    
    # Relationships
    resenas = db.relationship('Resena', backref='autor', lazy='dynamic')
    likes = db.relationship('Like', backref='usuario', lazy='dynamic')
    
    def get_id(self):
        return str(self.usuario_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.nombre}>'