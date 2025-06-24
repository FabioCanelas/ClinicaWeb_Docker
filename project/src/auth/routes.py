"""
Rutas de autenticación del sistema
Maneja login, logout y verificación de credenciales
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..models.models import Usuario

# Blueprint para rutas de autenticación
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Maneja el proceso de inicio de sesión
    GET: Muestra el formulario de login
    POST: Procesa las credenciales y autentica al usuario
    """
    # Siempre limpiar la sesión al entrar al login
    logout_user()
    
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
            error = 'Por favor complete todos los campos.'
            return render_template('auth/login.html', error=error)
        
        # Validar requisitos de contraseña
        import re
        if not re.search(r'[A-Z]', contrasena):
            error = 'La contraseña debe contener al menos una letra mayúscula.'
            return render_template('auth/login.html', error=error)
        if not re.search(r'[^A-Za-z0-9]', contrasena):
            error = 'La contraseña debe contener al menos un carácter especial.'
            return render_template('auth/login.html', error=error)
        
        # Buscar usuario en la base de datos
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        if not usuario:
            error = 'El nombre de usuario no existe.'
            return render_template('auth/login.html', error=error)
        elif not check_password_hash(usuario.contrasena, contrasena):
            error = 'Contraseña incorrecta.'
            return render_template('auth/login.html', error=error)
        
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

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Muestra el dashboard del usuario
    Redirige a la página de login si el usuario no está autenticado
    """
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('auth/dashboard.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Solo administradores pueden acceder
    if not current_user.is_admin():
        return redirect(url_for('auth.login'))

    from ..models.models import Rol
    error = None
    success = None
    roles = Rol.query.filter(Rol.nombre.in_(['administrador', 'doctor'])).all()
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario')
        contrasena = request.form.get('contrasena')
        contrasena2 = request.form.get('contrasena2')
        rol_nombre = request.form.get('rol')
        nombre_completo = request.form.get('nombre_completo')
        
        # Validaciones básicas
        if not nombre_usuario or not contrasena or not contrasena2 or not rol_nombre or not nombre_completo:
            error = 'Por favor complete todos los campos.'
        elif contrasena != contrasena2:
            error = 'Las contraseñas no coinciden.'
        else:
            import re
            if not re.search(r'[A-Z]', contrasena):
                error = 'La contraseña debe contener al menos una letra mayúscula.'
            elif not re.search(r'[^A-Za-z0-9]', contrasena):
                error = 'La contraseña debe contener al menos un carácter especial.'
            elif Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
                error = 'El nombre de usuario ya existe.'
            elif rol_nombre not in ['administrador', 'doctor']:
                error = 'Rol inválido.'
        
        if not error:
            rol = Rol.query.filter_by(nombre=rol_nombre).first()
            # Si se intenta crear un superadmin desde el formulario, bloquearlo
            if rol_nombre == 'administrador' and nombre_usuario == 'admin':
                error = 'No se puede crear otro superadministrador.'
            else:
                nuevo_usuario = Usuario(
                    nombre_usuario=nombre_usuario,
                    nombre_completo=nombre_completo,
                    contrasena=generate_password_hash(contrasena),
                    rol_id=rol.id
                )
                from ..extensions import db
                db.session.add(nuevo_usuario)
                db.session.commit()
                success = f'Usuario {nombre_usuario} registrado exitosamente como {rol_nombre}.'
    return render_template('auth/register.html', error=error, success=success, roles=roles)