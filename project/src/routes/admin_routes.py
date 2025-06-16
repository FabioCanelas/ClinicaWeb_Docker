"""
Rutas del panel de administración
Maneja todas las funcionalidades exclusivas para administradores
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from models.models import Usuario, Rol, Paciente, Especialidad, Expediente
from app import db

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
    total_pacientes = Paciente.query.filter_by(estado=True).count()
    total_expedientes = Expediente.query.count()
    total_especialidades = Especialidad.query.count()
    
    # Expedientes recientes
    expedientes_recientes = Expediente.query.order_by(Expediente.fecha_creacion.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_doctores=total_doctores,
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
    doctores = Usuario.query.join(Rol).filter(Rol.nombre == 'doctor').all()
    return render_template('admin/doctores.html', doctores=doctores)

@admin_bp.route('/doctores/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_doctor():
    """
    Formulario para registrar un nuevo doctor
    GET: Muestra el formulario
    POST: Procesa y guarda el nuevo doctor
    """
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario')
        contrasena = request.form.get('contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        
        # Validaciones
        if not nombre_usuario or not contrasena or not confirmar_contrasena:
            flash('Todos los campos son obligatorios.', 'error')
            return render_template('admin/nuevo_doctor.html')
        
        if contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('admin/nuevo_doctor.html')
        
        if len(contrasena) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('admin/nuevo_doctor.html')
        
        # Verificar que el nombre de usuario no exista
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash('El nombre de usuario ya existe.', 'error')
            return render_template('admin/nuevo_doctor.html')
        
        # Crear nuevo doctor
        rol_doctor = Rol.query.filter_by(nombre='doctor').first()
        nuevo_doctor = Usuario(
            nombre_usuario=nombre_usuario,
            contrasena=generate_password_hash(contrasena),
            rol_id=rol_doctor.id
        )
        
        try:
            db.session.add(nuevo_doctor)
            db.session.commit()
            flash(f'Doctor {nombre_usuario} registrado exitosamente.', 'success')
            return redirect(url_for('admin.listar_doctores'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el doctor. Intente nuevamente.', 'error')
    
    return render_template('admin/nuevo_doctor.html')

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