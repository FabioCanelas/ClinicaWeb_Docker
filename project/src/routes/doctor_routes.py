"""
Rutas del panel de doctores
Maneja todas las funcionalidades para médicos
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, date
from ..models.models import Usuario, Paciente, Especialidad, Expediente
from ..extensions import db
from datetime import datetime, date
import json

# Blueprint para rutas de doctores
doctor_bp = Blueprint('doctor', __name__)

def doctor_required(f):
    """
    Decorador que requiere permisos de doctor
    Verifica que el usuario actual sea doctor únicamente
    Los administradores tienen sus propias rutas y no necesitan acceso a funcionalidades de doctores
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_doctor():
            flash('Acceso denegado. Se requieren permisos de doctor.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@doctor_bp.route('/dashboard')
@login_required
@doctor_required
def dashboard():
    """
    Dashboard principal del doctor
    Muestra resumen de actividades y consultas recientes
    """
    # Estadísticas del doctor
    mis_consultas = Expediente.query.filter_by(doctor_id=current_user.id).count()
    consultas_hoy = Expediente.query.filter(
        Expediente.doctor_id == current_user.id,
        Expediente.fecha_consulta == date.today()
    ).count()
    
    # Consultas recientes del doctor
    consultas_recientes = Expediente.query.filter_by(doctor_id=current_user.id)\
                                         .order_by(Expediente.fecha_creacion.desc())\
                                         .limit(5).all()
    
    # Total de pacientes únicos atendidos
    pacientes_atendidos = db.session.query(Expediente.paciente_carnet)\
                                   .filter_by(doctor_id=current_user.id)\
                                   .distinct().count()
    
    return render_template('doctor/dashboard.html',
                         mis_consultas=mis_consultas,
                         consultas_hoy=consultas_hoy,
                         consultas_recientes=consultas_recientes,
                         pacientes_atendidos=pacientes_atendidos)

@doctor_bp.route('/pacientes')
@login_required
@doctor_required
def listar_pacientes():
    """
    Lista todos los pacientes activos
    Permite buscar y filtrar pacientes
    """
    busqueda = request.args.get('busqueda', '')
    
    # Utilizar joinedload para cargar relaciones en una sola consulta (mejora rendimiento)
    if busqueda:
        pacientes = Paciente.query.options(
            db.joinedload(Paciente.expedientes).joinedload(Expediente.especialidad),
            db.joinedload(Paciente.expedientes).joinedload(Expediente.doctor)
        ).filter(
            db.or_(
                Paciente.carnet.contains(busqueda),
                Paciente.nombres.contains(busqueda),
                Paciente.apellidos.contains(busqueda)
            ),
            Paciente.estado == True
        ).all()
    else:
        pacientes = Paciente.query.options(
            db.joinedload(Paciente.expedientes).joinedload(Expediente.especialidad),
            db.joinedload(Paciente.expedientes).joinedload(Expediente.doctor)
        ).filter_by(estado=True).all()
    
    # Registro para depuración
    print(f"Pacientes encontrados: {len(pacientes)}")
    
    return render_template('doctor/pacientes.html', pacientes=pacientes, busqueda=busqueda)

@doctor_bp.route('/pacientes/nuevo', methods=['GET', 'POST'])
@login_required
@doctor_required
def nuevo_paciente():
    """
    Formulario para registrar un nuevo paciente
    GET: Muestra el formulario
    POST: Procesa y guarda el nuevo paciente
    🔒 TC28: Validación de lógica de negocio - Verificar que existan doctores
    """
    # 🔒 TC28: VALIDACIÓN CRÍTICA DE LÓGICA DE NEGOCIO
    # Verificar que existan doctores registrados antes de permitir crear pacientes
    doctores_activos = Usuario.query.filter(
        Usuario.rol_id == 2,  # rol_id=2 para doctores
        Usuario.estado == True
    ).count()
    
    if doctores_activos == 0:
        flash('❌ No hay doctores registrados en el sistema. Es necesario registrar al menos un doctor antes de gestionar pacientes.', 'error')
        return redirect(url_for('admin.listar_doctores'))  # Redirigir a gestión de doctores
    
    if request.method == 'POST':
        carnet = request.form.get('carnet')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        genero = request.form.get('genero')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        
        # Validaciones
        if not all([carnet, nombres, apellidos, fecha_nacimiento]):
            flash('Los campos carnet, nombres, apellidos y fecha de nacimiento son obligatorios.', 'error')
            return render_template('doctor/nuevo_paciente.html')
        
        # Verificar que el carnet no exista
        if Paciente.query.filter_by(carnet=carnet).first():
            flash('Ya existe un paciente con ese número de carnet.', 'error')
            return render_template('doctor/nuevo_paciente.html')
        
        # Verificar email único si se proporciona
        if email and Paciente.query.filter_by(email=email).first():
            flash('Ya existe un paciente con ese email.', 'error')
            return render_template('doctor/nuevo_paciente.html')
        
        # 🔒 TC30: VALIDACIÓN Y SANITIZACIÓN DE EMAIL
        # Validar formato de email y prevenir XSS
        if email:
            import re
            from html import escape
            
            # Validación de formato email RFC 5322 simplificada
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                flash('El formato del email no es válido.', 'error')
                return render_template('doctor/nuevo_paciente.html')
            
            # Sanitizar email para prevenir XSS
            email = escape(email.strip())
            
            # Validación adicional de longitud
            if len(email) > 100:
                flash('El email es demasiado largo (máximo 100 caracteres).', 'error')
                return render_template('doctor/nuevo_paciente.html')
            
        # Validar que el teléfono tenga exactamente 8 dígitos si se proporciona
        if telefono:
            import re
            if not re.match(r'^\d{8}$', telefono):
                flash('El número de teléfono debe tener exactamente 8 dígitos numéricos.', 'error')
                return render_template('doctor/nuevo_paciente.html')
        
        try:
            # Convertir fecha de nacimiento
            fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            
            nuevo_paciente = Paciente(
                carnet=carnet,
                nombres=nombres,
                apellidos=apellidos,
                fecha_nacimiento=fecha_nac,
                genero=genero,
                direccion=direccion,
                telefono=telefono,
                email=email if email else None
            )
            
            db.session.add(nuevo_paciente)
            db.session.commit()
            flash(f'Paciente {nombres} {apellidos} registrado exitosamente.', 'success')
            return redirect(url_for('doctor.listar_pacientes'))
            
        except ValueError:
            flash('Fecha de nacimiento inválida.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el paciente. Intente nuevamente.', 'error')
    
    return render_template('doctor/nuevo_paciente.html')

@doctor_bp.route('/consultas')
@login_required
@doctor_required
def listar_consultas():
    """
    Lista todas las consultas del doctor actual
    Permite filtrar por fecha y paciente
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    paciente_carnet = request.args.get('paciente')
    
    consultas = Expediente.query.filter_by(doctor_id=current_user.id)
    
    if fecha_inicio:
        consultas = consultas.filter(Expediente.fecha_consulta >= fecha_inicio)
    if fecha_fin:
        consultas = consultas.filter(Expediente.fecha_consulta <= fecha_fin)
    if paciente_carnet:
        consultas = consultas.filter_by(paciente_carnet=paciente_carnet)
    
    consultas = consultas.order_by(Expediente.fecha_consulta.desc()).all()
    
    return render_template('doctor/consultas.html', consultas=consultas)

@doctor_bp.route('/consultas/nueva', methods=['GET', 'POST'])
@login_required
@doctor_required
def nueva_consulta():
    """
    Formulario para registrar una nueva consulta
    GET: Muestra el formulario con pacientes y especialidades
    POST: Procesa y guarda la nueva consulta
    """
    # Obtener todos los pacientes activos
    pacientes = Paciente.query.filter_by(estado=True).all()
    
    # Para doctores: mostrar solo las especialidades asociadas a él
    # Para administradores: mostrar todas las especialidades
    if current_user.is_doctor():
        especialidades = current_user.especialidades
    else:
        especialidades = Especialidad.query.all()
    
    if request.method == 'POST':
        paciente_carnet = request.form.get('paciente_carnet')
        especialidad_id = request.form.get('especialidad_id')
        tipo_consulta = request.form.get('tipo_consulta')
        fecha_consulta = request.form.get('fecha_consulta')
        resumen_clinico = request.form.get('resumen_clinico')
        
        # Datos adicionales de la consulta (síntomas, diagnóstico, etc.)
        sintomas = request.form.get('sintomas')
        diagnostico = request.form.get('diagnostico')
        tratamiento = request.form.get('tratamiento')
        observaciones = request.form.get('observaciones')
        
        # Validaciones
        if not all([paciente_carnet, especialidad_id, tipo_consulta, fecha_consulta]):
            flash('Todos los campos marcados son obligatorios.', 'error')
            return render_template('doctor/nueva_consulta.html', 
                                 pacientes=pacientes, especialidades=especialidades)
        
        try:
            # Crear datos estructurados de la consulta
            datos_consulta = {
                'sintomas': sintomas,
                'diagnostico': diagnostico,
                'tratamiento': tratamiento,
                'observaciones': observaciones
            }
            
            nueva_consulta = Expediente(
                paciente_carnet=paciente_carnet,
                especialidad_id=int(especialidad_id),
                doctor_id=current_user.id,
                tipo_consulta=tipo_consulta,
                fecha_consulta=datetime.strptime(fecha_consulta, '%Y-%m-%d').date(),
                resumen_clinico=resumen_clinico,
                datos_consulta=datos_consulta
            )
            
            db.session.add(nueva_consulta)
            db.session.commit()
            flash('Consulta registrada exitosamente.', 'success')
            return redirect(url_for('doctor.listar_consultas'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar la consulta. Intente nuevamente.', 'error')
    hoy = date.today().isoformat()
    # Agregar mensaje de depuración para verificar datos
    print(f"Pacientes disponibles: {len(pacientes)}")
    print(f"Especialidades disponibles: {len(especialidades)}")
    return render_template('doctor/nueva_consulta.html', pacientes=pacientes, especialidades=especialidades, hoy=hoy)

@doctor_bp.route('/expediente/<carnet>')
@login_required
@doctor_required
def ver_expediente(carnet):
    """
    Muestra el expediente completo de un paciente
    Incluye historial de consultas y datos personales
    """
    paciente = Paciente.query.get_or_404(carnet)
    expedientes = Expediente.query.filter_by(paciente_carnet=carnet)\
                                  .order_by(Expediente.fecha_consulta.desc()).all()
    
    return render_template('doctor/expediente.html', paciente=paciente, expedientes=expedientes)