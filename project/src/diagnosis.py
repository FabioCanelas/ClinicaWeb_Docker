"""
Archivo temporal para diagnóstico de problemas en la aplicación
"""
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from .models.models import Usuario, Rol
from functools import wraps

diagnosis_bp = Blueprint('diagnosis', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({"error": "Acceso denegado"})
        return f(*args, **kwargs)
    return decorated_function

@diagnosis_bp.route('/diagnostic/users')
@login_required
@admin_required
def diagnostic_users():
    """
    Ruta de diagnóstico para verificar todos los usuarios y sus roles
    """
    users = []
    all_users = Usuario.query.all()
    
    for user in all_users:
        user_data = {
            "id": user.id,
            "nombre_usuario": user.nombre_usuario,
            "nombre_completo": user.nombre_completo,
            "rol_id": user.rol_id,
            "rol_nombre": user.rol.nombre if user.rol else "Sin rol",
            "superadmin": user.superadmin,
            "carnet_identidad": user.carnet_identidad,
            "matricula_profesional": user.matricula_profesional,
            "es_doctor": user.is_doctor(),
            "es_admin": user.is_admin(),
            "especialidades": [esp.nombre for esp in user.especialidades] if hasattr(user, 'especialidades') else []
        }
        users.append(user_data)
    
    roles = []
    all_roles = Rol.query.all()
    
    for rol in all_roles:
        rol_data = {
            "id": rol.id,
            "nombre": rol.nombre,
            "usuarios_count": len(rol.usuarios)
        }
        roles.append(rol_data)
    
    # Revisar si hay doctores que no se están filtrando correctamente
    doctor_role = Rol.query.filter_by(nombre='doctor').first()
    doctors_by_role = Usuario.query.filter_by(rol_id=doctor_role.id).all() if doctor_role else []
    doctors_by_method = Usuario.query.filter(Usuario.is_doctor()).all()
    doctors_by_join = Usuario.query.join(Rol).filter(Rol.nombre == 'doctor').all()
    
    return jsonify({
        "users": users,
        "roles": roles,
        "doctor_role_id": doctor_role.id if doctor_role else None,
        "doctors_by_role_count": len(doctors_by_role),
        "doctors_by_method_count": len(doctors_by_method),
        "doctors_by_join_count": len(doctors_by_join),
        "doctors_by_role": [d.nombre_usuario for d in doctors_by_role],
        "doctors_by_join": [d.nombre_usuario for d in doctors_by_join]
    })
