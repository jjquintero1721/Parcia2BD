from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import Usuario

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres.')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir.')
    ])
    submit = SubmitField('Registrarse')
    
    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado. Por favor, usa otro.')

class ProfileForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    current_password = PasswordField('Contraseña actual')
    new_password = PasswordField('Nueva contraseña', validators=[
        Length(min=0, max=50)  # Min 0 allows empty field (no password change)
    ])
    confirm_password = PasswordField('Confirmar nueva contraseña', validators=[
        EqualTo('new_password', message='Las contraseñas deben coincidir.')
    ])
    submit = SubmitField('Actualizar Perfil')
    
    def validate_current_password(self, current_password):
        # Only validate if the user is trying to change their password
        if self.new_password.data:
            # This validation will need current_user from flask_login
            # Handle this in the route
            pass