"""
Rutas de autenticación del sistema
Maneja login, logout y verificación de credenciales con protección contra fuerza bruta
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import urlparse, urljoin
import secrets
import os
from ..models.models import Usuario
from ..extensions import limiter, db
from ..security.security_manager import SecurityManager

# Blueprint para rutas de autenticación
auth_bp = Blueprint('auth', __name__)

def regenerate_session():
    """
    🔒 SECURITY TC16: Regenera el Session ID de forma segura
    Previene ataques de Session Fixation
    """
    # Preservar datos críticos antes de regenerar
    preserved_data = {}
    csrf_token = session.get('_csrf_token')
    
    # Limpiar session actual
    session.clear()
    
    # Regenerar Session ID
    session.permanent = True
    
    # Restaurar datos críticos si existen
    if csrf_token:
        session['_csrf_token'] = csrf_token
    
    # Agregar timestamp de creación para tracking
    session['_session_created'] = secrets.token_hex(16)
    session['_session_regenerated'] = True

def invalidate_session_completely():
    """
    🔒 SECURITY TC16: Invalidación completa de sesión
    Elimina todos los datos de sesión del servidor y cliente
    """
    # Limpiar todos los datos de sesión
    session.clear()
    
    # Marcar para eliminación de cookie
    session.permanent = False
    
    # Regenerar para eliminar rastros
    session['_invalidated'] = True
    
    return True

def validate_session_integrity():
    """
    🔒 SECURITY TC16: Valida la integridad de la sesión actual
    Detecta sessions manipuladas o comprometidas
    """
    # Verificar si la sesión fue invalidada
    if session.get('_invalidated'):
        return False
    
    # Verificar consistencia de datos de autenticación
    if current_user.is_authenticated:
        session_user_id = session.get('_user_id')
        if session_user_id and session_user_id != current_user.id:
            # Inconsistencia detectada - posible manipulación
            return False
    
    return True

def is_safe_url(target):
    """
    Valida que la URL de redirección sea segura (solo rutas internas)
    Previene ataques de Open Redirect
    """
    if not target:
        return False
    
    # Parsear la URL objetivo
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    # Verificar que sea el mismo esquema y host
    return (test_url.scheme in ('http', 'https') and 
            ref_url.netloc == test_url.netloc)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("30 per minute")  # Rate limiting aumentado para desarrollo
def login():
    """
    Maneja el proceso de inicio de sesión con protección contra fuerza bruta
    GET: Muestra el formulario de login
    POST: Procesa las credenciales y autentica al usuario
    """
    # 🔒 SECURITY TC16: Regenerar Session ID al acceder al login (prevenir fixation)
    if request.method == 'GET':
        regenerate_session()
    
    # ✅ FIXED: Verificar primero si ya está autenticado
    if current_user.is_authenticated:
        # 🎨 UX MEJORADO: Mensaje estético para usuario ya autenticado
        next_page = request.args.get('next')
        
        # Determinar dashboard de destino
        if current_user.is_admin():
            dashboard_name = "Panel de Administración"
            dashboard_url = url_for('admin.dashboard')
            user_role = "Administrador"
            icon_class = "bi-shield-check"
        else:
            dashboard_name = "Panel Médico"
            dashboard_url = url_for('doctor.dashboard')
            user_role = "Doctor"
            icon_class = "bi-person-heart"
        
        # 🔒 SECURITY: Validar redirección para usuarios ya autenticados
        if next_page and is_safe_url(next_page):
            final_url = next_page
            dashboard_name = "página solicitada"
        else:
            final_url = dashboard_url
        
        # Mostrar página con mensaje estético y redirección automática
        return render_template('auth/login.html', 
                             already_authenticated=True,
                             user_name=current_user.nombre_completo,
                             user_role=user_role,
                             dashboard_name=dashboard_name,
                             dashboard_url=final_url,
                             icon_class=icon_class)
    
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario')
        contrasena = request.form.get('contrasena')
        remember = True if request.form.get('remember') else False
        
        # Validar datos del formulario
        if not nombre_usuario or not contrasena:
            error = 'Por favor complete todos los campos.'
            return render_template('auth/login.html', error=error)
        
        # 🔒 SECURITY: Verificar si la cuenta/IP está bloqueada
        ip_address = SecurityManager.get_client_ip()
        is_locked, lock_message = SecurityManager.is_account_locked(nombre_usuario, ip_address)
        
        if is_locked:
            SecurityManager.log_login_attempt(nombre_usuario, success=False)
            error = f'🔒 Acceso bloqueado: {lock_message}'
            return render_template('auth/login.html', error=error)
        
        # 🔒 SECURITY: Obtener estado de seguridad
        security_status = SecurityManager.get_security_status(nombre_usuario)
        
        # Advertir si quedan pocos intentos
        if security_status['remaining_attempts'] <= 2 and security_status['failed_attempts'] > 0:
            flash(f'⚠️ Advertencia: Solo quedan {security_status["remaining_attempts"]} intentos antes del bloqueo', 'warning')
        
        # Validar requisitos de contraseña (solo para feedback, no para seguridad)
        import re
        if not re.search(r'[A-Z]', contrasena):
            error = 'La contraseña debe contener al menos una letra mayúscula.'
            SecurityManager.log_login_attempt(nombre_usuario, success=False)
            return render_template('auth/login.html', error=error)
        if not re.search(r'[^A-Za-z0-9]', contrasena):
            error = 'La contraseña debe contener al menos un carácter especial.'
            SecurityManager.log_login_attempt(nombre_usuario, success=False)
            return render_template('auth/login.html', error=error)
        
        # Buscar usuario en la base de datos
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        if not usuario:
            error = 'El nombre de usuario no existe.'
            SecurityManager.log_login_attempt(nombre_usuario, success=False)
            return render_template('auth/login.html', error=error)
        elif not check_password_hash(usuario.contrasena, contrasena):
            error = 'Contraseña incorrecta.'
            SecurityManager.log_login_attempt(nombre_usuario, success=False)
            
            # Obtener estado actualizado después del fallo
            updated_status = SecurityManager.get_security_status(nombre_usuario)
            if updated_status['remaining_attempts'] > 0:
                error += f' Te quedan {updated_status["remaining_attempts"]} intentos.'
            
            return render_template('auth/login.html', error=error)
        
        # ✅ LOGIN EXITOSO
        # 🔒 SECURITY TC16: Regenerar Session ID después del login exitoso
        regenerate_session()
        
        # 🔒 SECURITY: Registrar intento exitoso
        SecurityManager.log_login_attempt(nombre_usuario, success=True)
        
        # Autenticar usuario
        login_user(usuario, remember=remember)
        
        # 🔒 SECURITY TC16: Marcar sesión como autenticada de forma segura
        session['_user_authenticated'] = True
        session['_user_id'] = usuario.id
        session['_login_timestamp'] = secrets.token_hex(8)  # Timestamp único
        
        # Limpiar registros antiguos (limpieza ocasional)
        if hash(nombre_usuario) % 100 == 0:  # 1% de probabilidad
            SecurityManager.cleanup_old_records()
        
        # 🔒 SECURITY: Redirigir según el rol del usuario con validación anti-Open Redirect
        next_page = request.args.get('next')
        if next_page and is_safe_url(next_page):
            return redirect(next_page)
        elif usuario.is_admin():
            flash(f'✅ Bienvenido, Administrador {usuario.nombre_usuario}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash(f'✅ Bienvenido, Dr. {usuario.nombre_usuario}!', 'success')
            return redirect(url_for('doctor.dashboard'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    🔒 SECURITY TC16: Cierra la sesión del usuario con invalidación completa
    Previene persistencia de sesión post-logout
    """
    nombre_usuario = current_user.nombre_usuario
    
    # 🔒 SECURITY TC16: Invalidación completa de sesión (server-side)
    invalidate_session_completely()
    
    # Logout de Flask-Login
    logout_user()
    
    # 🔒 SECURITY TC16: Regenerar Session ID después del logout
    regenerate_session()
    
    # Log del evento de logout
    SecurityManager.log_login_attempt(f"LOGOUT_{nombre_usuario}", success=True)
    
    flash(f'Sesión cerrada exitosamente. ¡Hasta luego, {nombre_usuario}!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """
    ✅ FIXED TC12: Redirige al dashboard apropiado según el rol del usuario
    Esta ruta ya no es redundante, ahora actúa como un router inteligente
    """
    # Redirigir al dashboard específico según el rol
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('doctor.dashboard'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Solo administradores pueden acceder
    if not current_user.is_admin():
        return redirect(url_for('auth.login'))

    from ..models.models import Rol, Especialidad
    error = None
    success = None
    
    # Determinar qué roles mostrar según el tipo de administrador
    if current_user.is_superadmin():
        # El superadmin puede registrar ambos roles
        roles = Rol.query.filter(Rol.nombre.in_(['administrador', 'doctor'])).all()
    else:
        # Administradores normales solo pueden registrar doctores
        roles = Rol.query.filter(Rol.nombre == 'doctor').all()
    
    # Obtener todas las especialidades para los doctores
    especialidades = Especialidad.query.all()
        
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario', '').strip()
        contrasena = request.form.get('contrasena', '')
        contrasena2 = request.form.get('contrasena2', '')
        rol_nombre = request.form.get('rol', '')
        nombre_completo = request.form.get('nombre_completo', '').strip()
        # Nuevos campos para doctores
        carnet_identidad = request.form.get('carnet_identidad', '').strip()
        matricula_profesional = request.form.get('matricula_profesional', '').strip()
        # Obtener las especialidades seleccionadas (solo para doctores)
        especialidades_ids = request.form.getlist('especialidades')
        
        # Verificar si hay espacios en el nombre de usuario
        if ' ' in nombre_usuario:
            error = 'El nombre de usuario no puede contener espacios.'
        else:
            # Eliminar cualquier espacio y aplicar formato al nombre de usuario según el rol
            nombre_usuario = nombre_usuario.replace(' ', '')
            if rol_nombre == 'doctor' and not nombre_usuario.startswith('dr.'):
                nombre_usuario = 'dr.' + nombre_usuario
            elif rol_nombre == 'administrador' and not nombre_usuario.startswith('admin.'):
                nombre_usuario = 'admin.' + nombre_usuario
        
        # Validaciones básicas
        if not nombre_usuario or not contrasena or not contrasena2 or not rol_nombre or not nombre_completo or not carnet_identidad:
            error = 'Por favor complete todos los campos.'
        elif contrasena != contrasena2:
            error = 'Las contraseñas no coinciden.'
        # Validar campo de matrícula profesional si el rol es doctor
        elif rol_nombre == 'doctor' and not matricula_profesional:
            error = 'Para doctores, debe ingresar la matrícula profesional.'
        # Validar que se haya seleccionado al menos una especialidad para doctores
        elif rol_nombre == 'doctor' and not especialidades_ids:
            error = 'Para doctores, debe seleccionar al menos una especialidad.'
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
            # Verificar que administradores normales no puedan crear otros administradores
            elif rol_nombre == 'administrador' and not current_user.is_superadmin():
                error = 'Solo el superadministrador puede crear otros administradores.'
            # Verificar que no exista otro usuario con el mismo carnet
            elif Usuario.query.filter_by(carnet_identidad=carnet_identidad).first():
                error = f'Ya existe un usuario registrado con el carnet {carnet_identidad}.'
            # Verificar matrícula profesional duplicada para doctores
            elif rol_nombre == 'doctor' and matricula_profesional and Usuario.query.filter_by(matricula_profesional=matricula_profesional).first():
                error = f'Ya existe un doctor registrado con la matrícula profesional {matricula_profesional}.'
        
        if not error:
            rol = Rol.query.filter_by(nombre=rol_nombre).first()
            if not rol:
                error = 'Error al obtener el rol.'
            else:
                # Si se intenta crear un superadmin desde el formulario, bloquearlo
                if rol_nombre == 'administrador' and nombre_usuario == 'admin.superadmin':
                    error = 'No se puede crear otro superadministrador.'
                else:
                    # Crear objeto usuario con los datos básicos
                    nuevo_usuario = Usuario(
                        nombre_usuario=nombre_usuario,
                        nombre_completo=nombre_completo,
                        contrasena=generate_password_hash(contrasena),
                        rol_id=rol.id,
                        carnet_identidad=carnet_identidad  # Carnet para todos los usuarios
                    )
                    
                    # Si es doctor, agregar el campo de matrícula profesional y especialidades
                    if rol_nombre == 'doctor':
                        nuevo_usuario.matricula_profesional = matricula_profesional
                        # Asignar especialidades si es doctor
                        if especialidades_ids:
                            especialidades_objs = Especialidad.query.filter(Especialidad.id.in_(especialidades_ids)).all()
                            nuevo_usuario.especialidades = especialidades_objs
                        
                        # Verificación de seguridad: asegurarse de que el rol_id sea correcto
                        doctor_role = Rol.query.filter_by(nombre='doctor').first()
                        if doctor_role:
                            nuevo_usuario.rol_id = doctor_role.id
                            print(f"Asignando rol de doctor con ID {doctor_role.id} al usuario {nombre_usuario}")
                
                from ..extensions import db
                db.session.add(nuevo_usuario)
                db.session.commit()
                success = f'Usuario {nombre_completo} registrado exitosamente como {rol_nombre} con usuario {nombre_usuario}.'
    return render_template('auth/register.html', error=error, success=success, roles=roles, especialidades=especialidades)

@auth_bp.route('/security/status')
@login_required
def security_status():
    """
    Muestra el estado de seguridad del sistema (solo para administradores)
    """
    if not current_user.is_admin():
        flash('Acceso denegado. Solo administradores pueden ver esta información.', 'error')
        return redirect(url_for('auth.login'))
    
    from ..models.models import LoginAttempt, AccountLock
    from datetime import datetime, timedelta
    
    # Estadísticas de los últimos 7 días
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Intentos totales
    total_attempts = LoginAttempt.query.filter(LoginAttempt.timestamp > week_ago).count()
    failed_attempts = LoginAttempt.query.filter(
        LoginAttempt.timestamp > week_ago,
        LoginAttempt.success == False
    ).count()
    successful_attempts = total_attempts - failed_attempts
    
    # Cuentas bloqueadas actualmente
    active_locks = AccountLock.query.filter(AccountLock.unlock_at > datetime.utcnow()).all()
    
    # IPs más activas
    top_ips = db.session.query(
        LoginAttempt.ip_address, 
        db.func.count(LoginAttempt.id).label('count')
    ).filter(
        LoginAttempt.timestamp > week_ago
    ).group_by(LoginAttempt.ip_address).order_by(
        db.func.count(LoginAttempt.id).desc()
    ).limit(10).all()
    
    return render_template('auth/security_status.html', 
                         total_attempts=total_attempts,
                         failed_attempts=failed_attempts,
                         successful_attempts=successful_attempts,
                         active_locks=active_locks,
                         top_ips=top_ips)

@auth_bp.route('/security/unlock', methods=['POST'])
@login_required
def unlock_account():
    """
    Desbloquea una cuenta (solo para administradores)
    """
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    username = request.form.get('username')
    ip_address = request.form.get('ip_address')
    
    if not username and not ip_address:
        return jsonify({'success': False, 'message': 'Debe especificar username o IP'})
    
    from ..models.models import AccountLock
    
    # Desbloquear por username
    if username:
        AccountLock.query.filter_by(username=username).delete()
    
    # Desbloquear por IP
    if ip_address:
        AccountLock.query.filter_by(ip_address=ip_address).delete()
    
    try:
        db.session.commit()
        SecurityManager.log_login_attempt(f"UNLOCK_{username or ip_address}", success=True)
        return jsonify({'success': True, 'message': 'Cuenta desbloqueada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al desbloquear: {str(e)}'})

@auth_bp.route('/check_username')
def check_username():
    """
    Verifica si un nombre de usuario está disponible
    Devuelve respuesta en formato JSON para uso en peticiones AJAX
    """
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'available': False, 'message': 'Nombre de usuario no proporcionado'})
    
    # Verificar si hay espacios en el nombre de usuario
    if ' ' in username:
        return jsonify({'available': False, 'message': 'El nombre de usuario no debe contener espacios'})
    
    # Verificar si el nombre de usuario ya existe
    usuario_existente = Usuario.query.filter_by(nombre_usuario=username).first()
    
    return jsonify({
        'available': not usuario_existente,
        'message': 'Disponible' if not usuario_existente else 'No disponible'
    })