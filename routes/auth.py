from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from forms.auth import LoginForm, RegisterForm
from models.user import Usuario
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Email o contraseña incorrectos', 'danger')
            return redirect(url_for('auth.login'))
        
        if user.estado != 'activo':
            flash('Tu cuenta está desactivada. Contacta al administrador.', 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        # Update last access time
        user.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
            
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = Usuario(
            nombre=form.nombre.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('¡Te has registrado exitosamente! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar usuario. Intenta nuevamente.', 'danger')
    
    return render_template('auth/register.html', title='Registro', form=form)

@auth_bp.route('/profile')
@login_required
def profile():
    from models.resena import Resena
    
    return render_template('auth/profile.html', title='Mi Perfil')

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    from forms.auth import ProfileForm
    
    form = ProfileForm()
    if request.method == 'GET':
        form.nombre.data = current_user.nombre
        form.email.data = current_user.email
    
    if form.validate_on_submit():
        current_user.nombre = form.nombre.data
        
        # If email changed, check it doesn't exist
        if form.email.data != current_user.email:
            if Usuario.query.filter_by(email=form.email.data).first():
                flash('Este email ya está en uso', 'danger')
                return redirect(url_for('auth.edit_profile'))
            current_user.email = form.email.data
        
        # Change password if provided
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
            
        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/edit_profile.html', title='Editar Perfil', form=form)