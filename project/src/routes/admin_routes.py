"""
Rutas del panel de administración
Maneja todas las funcionalidades exclusivas para administradores
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from ..models.models import Usuario, Rol, Paciente, Especialidad, Expediente
from ..extensions import db

# Blueprint para rutas de administración
admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """
    Decorador que requiere permisos de administrador
    Verifica que el usuario actual sea administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    """
    Decorador que requiere permisos de superadministrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superadmin():
            flash('Acceso denegado. Solo el superadministrador puede realizar esta acción.', 'error')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """
    Dashboard principal del administrador
    Muestra estadísticas generales del sistema
    """
    # Obtener estadísticas para el dashboard
    total_doctores = Usuario.query.join(Rol).filter(Rol.nombre == 'doctor').count()
    total_administradores = Usuario.query.join(Rol).filter(Rol.nombre == 'administrador').count()
    total_pacientes = Paciente.query.filter_by(estado=True).count()
    total_expedientes = Expediente.query.count()
    total_especialidades = Especialidad.query.count()
    
    # Expedientes recientes
    expedientes_recientes = Expediente.query.order_by(Expediente.fecha_creacion.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_doctores=total_doctores,
                         total_administradores=total_administradores,
                         total_pacientes=total_pacientes,
                         total_expedientes=total_expedientes,
                         total_especialidades=total_especialidades,
                         expedientes_recientes=expedientes_recientes)

@admin_bp.route('/doctores')
@login_required
@admin_required
def listar_doctores():
    """
    Lista todos los doctores registrados en el sistema
    Permite ver, editar y gestionar cuentas de doctores
    """
    # Obtenemos todos los doctores de forma más directa y eficiente
    rol_doctor = Rol.query.filter_by(nombre='doctor').first()
    if rol_doctor:
        # Usamos un join con eager loading para cargar las relaciones en una sola consulta
        doctores = (Usuario.query
                   .filter_by(rol_id=rol_doctor.id)
                   .options(db.joinedload(Usuario.especialidades))
                   .options(db.joinedload(Usuario.expedientes))
                   .options(db.joinedload(Usuario.rol))
                   .all())
        print(f"Doctores encontrados: {len(doctores)}")
        for doc in doctores:
            print(f"Doctor ID: {doc.id}, Nombre: {doc.nombre_completo}, CI: {doc.carnet_identidad}, MP: {doc.matricula_profesional}")
    else:
        doctores = []
        print("No se encontró el rol de doctor")
    
    return render_template('admin/doctores.html', doctores=doctores)

@admin_bp.route('/doctores/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_doctor():
    from ..models.models import Especialidad
    especialidades = Especialidad.query.all()
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario', '').strip()
        nombre_completo = request.form.get('nombre_completo', '').strip()
        contrasena = request.form.get('contrasena', '')
        confirmar_contrasena = request.form.get('confirmar_contrasena', '')
        carnet_identidad = request.form.get('carnet_identidad', '').strip()
        matricula_profesional = request.form.get('matricula_profesional', '').strip()
        especialidades_ids = request.form.getlist('especialidades')
        
        # Validaciones básicas
        if not nombre_usuario or not nombre_completo or not contrasena or not confirmar_contrasena or not especialidades_ids or not carnet_identidad or not matricula_profesional:
            flash('Todos los campos son obligatorios, incluyendo carnet, matrícula profesional y especialidades.', 'error')
            return render_template('admin/nuevo_doctor.html', especialidades=especialidades)
        
        # Verificar si hay espacios en el nombre de usuario
        if ' ' in nombre_usuario:
            flash('El nombre de usuario no puede contener espacios.', 'error')
            return render_template('admin/nuevo_doctor.html', especialidades=especialidades)
            
        # Eliminar cualquier espacio y formato especial para nombres de usuario de doctores
        nombre_usuario = nombre_usuario.replace(' ', '')
        if not nombre_usuario.startswith('dr.'):
            nombre_usuario = 'dr.' + nombre_usuario
        
        if contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('admin/nuevo_doctor.html', especialidades=especialidades)
            
        import re
        if len(contrasena) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'error')
            return render_template('admin/nuevo_doctor.html', especialidades=especialidades)
        if not re.search(r'[A-Z]', contrasena):
            flash('La contraseña debe contener al menos una letra mayúscula.', 'error')
            return render_template('admin/nuevo_doctor.html', especialidades=especialidades)
        if not re.search(r'[^A-Za-z0-9]', contrasena):
            flash('La contraseña debe contener al menos un carácter especial.', 'error')
            return render_template('admin/nuevo_doctor.html', especialidades=especialidades)
            
        # Verificar si el nombre de usuario ya existe (después de formatear con el prefijo)
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash('El nombre de usuario ya existe.', 'error')
            return render_template('admin/nuevo_doctor.html', especialidades=especialidades)
        # Validar que el carnet de identidad no esté duplicado
        if Usuario.query.filter_by(carnet_identidad=carnet_identidad).first():
            flash(f'Ya existe un usuario registrado con el carnet {carnet_identidad}.', 'error')
            return render_template('admin/nuevo_doctor.html', especialidades=especialidades)
        # Validar que la matrícula profesional no esté duplicada
        if Usuario.query.filter_by(matricula_profesional=matricula_profesional).first():
            flash(f'Ya existe un doctor registrado con la matrícula profesional {matricula_profesional}.', 'error')
            return render_template('admin/nuevo_doctor.html', especialidades=especialidades)
        rol_doctor = Rol.query.filter_by(nombre='doctor').first()
        especialidades_objs = Especialidad.query.filter(Especialidad.id.in_(especialidades_ids)).all()
        nuevo_doctor = Usuario(
            nombre_usuario=nombre_usuario,
            nombre_completo=nombre_completo,
            contrasena=generate_password_hash(contrasena),
            rol_id=rol_doctor.id,
            carnet_identidad=carnet_identidad,
            matricula_profesional=matricula_profesional,
            especialidades=especialidades_objs
        )
        try:
            db.session.add(nuevo_doctor)
            db.session.commit()
            flash(f'Doctor {nombre_completo} registrado exitosamente con usuario {nombre_usuario}.', 'success')
            return redirect(url_for('admin.listar_doctores'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el doctor. Intente nuevamente.', 'error')
    return render_template('admin/nuevo_doctor.html', especialidades=especialidades)

@admin_bp.route('/administradores')
@login_required
@superadmin_required
def listar_administradores():
    """
    Lista todos los administradores registrados en el sistema
    Solo accesible para el superadministrador
    """
    # Obtenemos todos los administradores
    rol_admin = Rol.query.filter_by(nombre='administrador').first()
    if rol_admin:
        administradores = (Usuario.query
                          .filter_by(rol_id=rol_admin.id)
                          .options(db.joinedload(Usuario.rol))
                          .order_by(Usuario.nombre_completo)
                          .all())
        print(f"Administradores encontrados: {len(administradores)}")
        for admin in administradores:
            print(f"Admin ID: {admin.id}, Nombre: {admin.nombre_completo}, Usuario: {admin.nombre_usuario}")
    else:
        administradores = []
        print("No se encontró el rol de administrador")
    
    return render_template('admin/administradores.html', administradores=administradores)

@admin_bp.route('/administradores/toggle_estado/<int:admin_id>', methods=['POST'])
@login_required
@superadmin_required
def toggle_estado_administrador(admin_id):
    """
    Activa o desactiva un administrador
    Solo accesible para el superadministrador
    """
    try:
        administrador = Usuario.query.get_or_404(admin_id)
        
        # Verificar que sea un administrador
        if not administrador.is_admin():
            flash('El usuario especificado no es un administrador.', 'error')
            return redirect(url_for('admin.listar_administradores'))
        
        # No permitir desactivar al superadmin
        if administrador.is_superadmin():
            flash('No se puede desactivar al superadministrador.', 'error')
            return redirect(url_for('admin.listar_administradores'))
        
        # Cambiar estado
        administrador.estado = not administrador.estado
        db.session.commit()
        
        estado_texto = "activado" if administrador.estado else "desactivado"
        flash(f'Administrador {administrador.nombre_completo} {estado_texto} exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error al cambiar el estado del administrador.', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('admin.listar_administradores'))

@admin_bp.route('/administradores/resetear_password/<int:admin_id>', methods=['POST'])
@login_required
@superadmin_required
def resetear_password_administrador(admin_id):
    """
    Resetea la contraseña de un administrador
    Solo accesible para el superadministrador
    """
    try:
        administrador = Usuario.query.get_or_404(admin_id)
        
        # Verificar que sea un administrador
        if not administrador.is_admin():
            flash('El usuario especificado no es un administrador.', 'error')
            return redirect(url_for('admin.listar_administradores'))
        
        # No permitir resetear password del superadmin
        if administrador.is_superadmin():
            flash('No se puede resetear la contraseña del superadministrador.', 'error')
            return redirect(url_for('admin.listar_administradores'))
        
        # Generar nueva contraseña temporal
        nueva_password = f"Admin{administrador.carnet_identidad}*"
        administrador.contrasena = generate_password_hash(nueva_password)
        administrador.cambiar_contrasena = True  # Forzar cambio en el próximo login
        
        db.session.commit()
        
        flash(f'✅ Contraseña reseteada exitosamente para {administrador.nombre_completo}', 'success')
        flash(f'🔑 CONTRASEÑA TEMPORAL: {nueva_password}', 'info')
        flash(f'⚠️ El usuario debe cambiar esta contraseña en su próximo inicio de sesión', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash('Error al resetear la contraseña del administrador.', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('admin.listar_administradores'))

@admin_bp.route('/especialidades')
@login_required
@admin_required
def listar_especialidades():
    """
    Lista todas las especialidades médicas
    Permite gestionar el catálogo de especialidades
    """
    especialidades = Especialidad.query.all()
    return render_template('admin/especialidades.html', especialidades=especialidades)

@admin_bp.route('/especialidades/nueva', methods=['POST'])
@login_required
@admin_required
def nueva_especialidad():
    """
    Crea una nueva especialidad médica via AJAX
    Devuelve respuesta JSON para actualización dinámica
    """
    nombre = request.form.get('nombre')
    
    if not nombre:
        return jsonify({'success': False, 'message': 'El nombre es obligatorio'})
    
    if Especialidad.query.filter_by(nombre=nombre).first():
        return jsonify({'success': False, 'message': 'La especialidad ya existe'})
    
    try:
        nueva_esp = Especialidad(nombre=nombre)
        db.session.add(nueva_esp)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Especialidad creada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al crear la especialidad'})

@admin_bp.route('/reportes')
@login_required
@admin_required
def reportes():
    """
    Página de reportes y estadísticas avanzadas
    Muestra métricas detalladas del sistema
    """
    # Consultas por especialidad
    consultas_por_especialidad = db.session.query(
        Especialidad.nombre,
        db.func.count(Expediente.id).label('total')
    ).join(Expediente).group_by(Especialidad.nombre).all()
    
    # Consultas por doctor
    consultas_por_doctor = db.session.query(
        Usuario.nombre_usuario,
        db.func.count(Expediente.id).label('total')
    ).join(Expediente).group_by(Usuario.nombre_usuario).all()
    
    return render_template('admin/reportes.html',
                         consultas_por_especialidad=consultas_por_especialidad,
                         consultas_por_doctor=consultas_por_doctor)

@admin_bp.route('/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
@login_required
@superadmin_required
def eliminar_usuario(usuario_id):
    """
    Elimina un usuario del sistema
    Solo puede ser ejecutada por el superadministrador
    """
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # No permitir eliminar al superadmin
        if usuario.is_superadmin():
            flash('No se puede eliminar al superadministrador.', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Verificar si es administrador para redirigir correctamente
        es_admin = usuario.is_admin()
        nombre_usuario = usuario.nombre_completo
        
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuario {nombre_usuario} eliminado exitosamente.', 'success')
        
        # Redirigir según el tipo de usuario eliminado
        if es_admin:
            return redirect(url_for('admin.listar_administradores'))
        else:
            return redirect(url_for('admin.listar_doctores'))
            
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el usuario.', 'error')
        print(f"Error eliminando usuario: {e}")
        return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(usuario_id):
    """
    Edita un usuario del sistema
    Administradores pueden editar doctores, superadmin puede editar todos incluido a sí mismo
    """
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # Verificaciones de permisos
    if not current_user.is_superadmin():
        # Administradores normales solo pueden editar doctores o a sí mismos
        if not usuario.is_doctor() and usuario.id != current_user.id:
            flash('No tiene permisos para editar este usuario.', 'error')
            return redirect(url_for('admin.dashboard'))
    
    if request.method == 'GET':
        # Cargar especialidades si es doctor
        especialidades = []
        if usuario.is_doctor():
            especialidades = Especialidad.query.all()
        
        return render_template('admin/editar_usuario.html', 
                             usuario=usuario, 
                             especialidades=especialidades)
    
    # POST - Procesar edición
    try:
        nombre_completo = request.form.get('nombre_completo', '').strip()
        carnet_identidad = request.form.get('carnet_identidad', '').strip()
        nueva_contrasena = request.form.get('nueva_contrasena', '').strip()
        confirmar_contrasena = request.form.get('confirmar_contrasena', '').strip()
        
        # Validaciones básicas
        if not nombre_completo:
            flash('El nombre completo es obligatorio.', 'error')
            return redirect(request.url)
        
        if not carnet_identidad:
            flash('El carnet de identidad es obligatorio.', 'error')
            return redirect(request.url)
        
        # Verificar duplicados de carnet (excluyendo el usuario actual)
        carnet_existente = Usuario.query.filter(
            Usuario.carnet_identidad == carnet_identidad,
            Usuario.id != usuario_id
        ).first()
        if carnet_existente:
            flash(f'Ya existe otro usuario con el carnet {carnet_identidad}.', 'error')
            return redirect(request.url)
        
        # Actualizar campos básicos
        usuario.nombre_completo = nombre_completo
        usuario.carnet_identidad = carnet_identidad
        
        # Validar y actualizar contraseña si se proporcionó
        if nueva_contrasena:
            if nueva_contrasena != confirmar_contrasena:
                flash('Las contraseñas no coinciden.', 'error')
                return redirect(request.url)
            
            # Validaciones de contraseña
            import re
            if len(nueva_contrasena) < 8:
                flash('La contraseña debe tener al menos 8 caracteres.', 'error')
                return redirect(request.url)
            if not re.search(r'[A-Z]', nueva_contrasena):
                flash('La contraseña debe contener al menos una letra mayúscula.', 'error')
                return redirect(request.url)
            if not re.search(r'[^A-Za-z0-9]', nueva_contrasena):
                flash('La contraseña debe contener al menos un carácter especial.', 'error')
                return redirect(request.url)
            
            usuario.contrasena = generate_password_hash(nueva_contrasena)
            usuario.cambiar_contrasena = False  # No forzar cambio si la establece manualmente
        
        # Para doctores, actualizar matrícula profesional y especialidades
        if usuario.is_doctor():
            matricula_profesional = request.form.get('matricula_profesional', '').strip()
            if matricula_profesional:
                # Verificar duplicados de matrícula (excluyendo el usuario actual)
                matricula_existente = Usuario.query.filter(
                    Usuario.matricula_profesional == matricula_profesional,
                    Usuario.id != usuario_id
                ).first()
                if matricula_existente:
                    flash(f'Ya existe otro doctor con la matrícula {matricula_profesional}.', 'error')
                    return redirect(request.url)
                
                usuario.matricula_profesional = matricula_profesional
            
            # Actualizar especialidades
            especialidades_ids = request.form.getlist('especialidades')
            if especialidades_ids:
                especialidades_objs = Especialidad.query.filter(Especialidad.id.in_(especialidades_ids)).all()
                usuario.especialidades = especialidades_objs
        
        db.session.commit()
        flash(f'Usuario {usuario.nombre_completo} actualizado exitosamente.', 'success')
        
        # Redirigir según el tipo de usuario
        if usuario.is_admin():
            return redirect(url_for('admin.listar_administradores'))
        else:
            return redirect(url_for('admin.listar_doctores'))
            
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar el usuario.', 'error')
        print(f"Error editando usuario: {e}")
        return redirect(request.url)

@admin_bp.route('/perfil/cambiar_contrasena', methods=['GET', 'POST'])
@login_required
@admin_required
def cambiar_contrasena_propia():
    """
    Permite a cualquier administrador (incluido superadmin) cambiar su propia contraseña
    """
    if request.method == 'GET':
        return render_template('admin/cambiar_contrasena.html')
    
    # POST - Procesar cambio de contraseña
    try:
        contrasena_actual = request.form.get('contrasena_actual', '')
        nueva_contrasena = request.form.get('nueva_contrasena', '')
        confirmar_contrasena = request.form.get('confirmar_contrasena', '')
        
        # Validar contraseña actual (excepto para superadmin en emergencia)
        if not check_password_hash(current_user.contrasena, contrasena_actual):
            # Verificación especial para superadmin si olvidó su contraseña
            codigo_emergencia = request.form.get('codigo_emergencia', '')
            if current_user.is_superadmin() and codigo_emergencia:
                # Código de emergencia: combinación de carnet + nombre de usuario
                codigo_esperado = f"{current_user.carnet_identidad}{current_user.nombre_usuario}".lower()
                if codigo_emergencia.lower() != codigo_esperado:
                    flash('Código de emergencia incorrecto.', 'error')
                    return redirect(request.url)
            else:
                flash('La contraseña actual es incorrecta.', 'error')
                return redirect(request.url)
        
        # Validar nueva contraseña
        if nueva_contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(request.url)
        
        # Validaciones de seguridad
        import re
        if len(nueva_contrasena) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'error')
            return redirect(request.url)
        if not re.search(r'[A-Z]', nueva_contrasena):
            flash('La contraseña debe contener al menos una letra mayúscula.', 'error')
            return redirect(request.url)
        if not re.search(r'[^A-Za-z0-9]', nueva_contrasena):
            flash('La contraseña debe contener al menos un carácter especial.', 'error')
            return redirect(request.url)
        
        # Actualizar contraseña
        current_user.contrasena = generate_password_hash(nueva_contrasena)
        current_user.cambiar_contrasena = False
        
        db.session.commit()
        flash('Contraseña actualizada exitosamente.', 'success')
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('Error al cambiar la contraseña.', 'error')
        print(f"Error cambiando contraseña: {e}")
        return redirect(request.url)

@admin_bp.route('/doctores/resetear_password/<int:doctor_id>', methods=['POST'])
@login_required
@admin_required
def resetear_password_doctor(doctor_id):
    """
    Resetea la contraseña de un doctor
    Accesible para cualquier administrador
    """
    try:
        doctor = Usuario.query.get_or_404(doctor_id)
        
        # Verificar que sea un doctor
        if not doctor.rol.nombre == 'doctor':
            flash('El usuario especificado no es un doctor.', 'error')
            return redirect(url_for('admin.listar_doctores'))
        
        # Generar nueva contraseña temporal
        nueva_password = f"Dr{doctor.carnet_identidad}*"
        doctor.contrasena = generate_password_hash(nueva_password)
        doctor.cambiar_contrasena = True  # Forzar cambio en el próximo login
        
        db.session.commit()
        
        flash(f'✅ Contraseña reseteada exitosamente para Dr. {doctor.nombre_completo}', 'success')
        flash(f'🔑 CONTRASEÑA TEMPORAL: {nueva_password}', 'info')
        flash(f'⚠️ El doctor debe cambiar esta contraseña en su próximo inicio de sesión', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash('Error al resetear la contraseña del doctor.', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('admin.listar_doctores'))

