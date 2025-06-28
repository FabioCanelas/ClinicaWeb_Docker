"""
Rutas de autenticación del sistema
Maneja login, logout y verificación de credenciales
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
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