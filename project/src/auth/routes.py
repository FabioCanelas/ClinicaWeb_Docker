"""
Rutas de autenticación del sistema
Maneja login, logout y verificación de credenciales
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models.models import Usuario

# Blueprint para rutas de autenticación
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Maneja el proceso de inicio de sesión
    GET: Muestra el formulario de login
    POST: Procesa las credenciales y autentica al usuario
    """
    # Si el usuario ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('doctor.dashboard'))
    
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario')
        contrasena = request.form.get('contrasena')
        remember = True if request.form.get('remember') else False
        
        # Validar datos del formulario
        if not nombre_usuario or not contrasena:
            flash('Por favor complete todos los campos.', 'error')
            return render_template('auth/login.html')
        
        # Buscar usuario en la base de datos
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        # Verificar credenciales
        if not usuario or not check_password_hash(usuario.contrasena, contrasena):
            flash('Credenciales incorrectas. Intente nuevamente.', 'error')
            return render_template('auth/login.html')
        
        # Autenticar usuario
        login_user(usuario, remember=remember)
        
        # Redirigir según el rol del usuario
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        elif usuario.is_admin():
            flash(f'Bienvenido, Administrador {usuario.nombre_usuario}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash(f'Bienvenido, Dr. {usuario.nombre_usuario}!', 'success')
            return redirect(url_for('doctor.dashboard'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Cierra la sesión del usuario actual
    Redirige a la página de login con mensaje de confirmación
    """
    nombre_usuario = current_user.nombre_usuario
    logout_user()
    flash(f'Sesión cerrada exitosamente. ¡Hasta luego, {nombre_usuario}!', 'info')
    return redirect(url_for('auth.login'))