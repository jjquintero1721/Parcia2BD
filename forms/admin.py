from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, IntegerField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange, ValidationError
import re

class ProductForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=100)])
    descripcion = TextAreaField('Descripción', validators=[Length(max=2000)])
    categoria_id = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    ficha_tecnica = TextAreaField('Ficha Técnica', validators=[Length(max=2000)])
    imagen = FileField('Imagen Principal', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Solo se permiten imágenes (jpg, jpeg, png)')
    ])
    estado = SelectField('Estado', choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')])
    submit = SubmitField('Guardar Producto')

class CategoryForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    descripcion = TextAreaField('Descripción', validators=[Length(max=1000)])
    estado = SelectField('Estado', choices=[('activa', 'Activa'), ('inactiva', 'Inactiva')])
    submit = SubmitField('Guardar Categoría')

class ImageUploadForm(FlaskForm):
    titulo = StringField('Título', validators=[Length(max=100)])
    imagen = FileField('Imagen', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Solo se permiten imágenes (jpg, jpeg, png)')
    ])
    es_principal = BooleanField('Imagen Principal')
    orden = IntegerField('Orden', default=0)
    submit = SubmitField('Subir Imagen')

class ReviewApprovalForm(FlaskForm):
    estado = SelectField('Estado', choices=[
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobar'),
        ('rechazada', 'Rechazar')
    ])
    submit = SubmitField('Actualizar Estado')

class UserForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Nueva Contraseña (dejar en blanco para mantener la actual)', validators=[Optional()])
    estado = SelectField('Estado', choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')])
    submit = SubmitField('Actualizar Usuario')

class UbicacionForm(FlaskForm):
    ciudad = StringField('Ciudad', validators=[DataRequired(), Length(max=100)])
    departamento = StringField('Departamento', validators=[DataRequired(), Length(max=100)])
    pais = StringField('País', validators=[DataRequired(), Length(max=50)], default='Colombia')
    codigo_postal = StringField('Código Postal', validators=[Length(max=20)])
    submit = SubmitField('Guardar Ubicación')

class RangoIPForm(FlaskForm):
    ip_inicio = StringField('IP Inicio', validators=[DataRequired()])
    ip_fin = StringField('IP Fin', validators=[DataRequired()])
    submit = SubmitField('Guardar Rango IP')
    
    def validate_ip_inicio(self, field):
        # Validate IPv4 format
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(pattern, field.data)
        if not match:
            raise ValidationError('Formato de IP inválido. Use el formato: xxx.xxx.xxx.xxx')
        
        # Validate each octet
        for octet in match.groups():
            if int(octet) > 255:
                raise ValidationError('Cada número de la IP debe estar entre 0 y 255.')
    
    def validate_ip_fin(self, field):
        # Use the same validation as for ip_inicio
        self.validate_ip_inicio(field)
        
        # Additional validation: ip_fin should be greater than ip_inicio
        # This would require converting the IPs to integers and comparing them
        # This is a simplified check that assumes properly formatted IPs
        ip_inicio_parts = self.ip_inicio.data.split('.')
        ip_fin_parts = field.data.split('.')
        
        for i in range(4):
            if int(ip_inicio_parts[i]) < int(ip_fin_parts[i]):
                return
            if int(ip_inicio_parts[i]) > int(ip_fin_parts[i]):
                raise ValidationError('La IP fin debe ser mayor que la IP inicio.')