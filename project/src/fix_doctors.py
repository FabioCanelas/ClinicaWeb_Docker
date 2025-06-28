"""
Script para corregir cualquier problema con los roles de doctor en la base de datos
"""

from project.src.extensions import db
from project.src.models.models import Usuario, Rol, Especialidad
from project.src.app import create_app
import sys

def fix_doctor_roles():
    """
    Corrige los roles de doctores en la base de datos
    """
    print("Iniciando corrección de roles de doctores...")
    
    # Obtener el rol de doctor
    doctor_role = Rol.query.filter_by(nombre='doctor').first()
    
    if not doctor_role:
        print("Error: El rol de doctor no existe en la base de datos.")
        return
    
    print(f"Rol de doctor encontrado: ID={doctor_role.id}")
    
    # Obtener todos los usuarios que tienen el método is_doctor() pero su rol_id no coincide
    inconsistent_doctors = []
    all_users = Usuario.query.all()
    
    for user in all_users:
        # Si tiene matrícula profesional pero no tiene el rol de doctor
        if user.matricula_profesional and user.rol_id != doctor_role.id:
            print(f"Usuario inconsistente: {user.nombre_usuario} tiene matrícula profesional pero no el rol de doctor")
            user.rol_id = doctor_role.id
            inconsistent_doctors.append(user.nombre_usuario)
    
    # Guardar cambios
    if inconsistent_doctors:
        try:
            db.session.commit()
            print(f"Se corrigieron {len(inconsistent_doctors)} usuarios con roles inconsistentes:")
            for doctor in inconsistent_doctors:
                print(f"- {doctor}")
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar cambios: {str(e)}")
    else:
        print("No se encontraron usuarios con roles inconsistentes.")
    
    # Verificar usuarios con el rol de doctor
    doctors = Usuario.query.filter_by(rol_id=doctor_role.id).all()
    print(f"Total de doctores en la base de datos: {len(doctors)}")
    
    # Listar doctores
    print("\nListado de doctores:")
    for i, doctor in enumerate(doctors, 1):
        print(f"{i}. {doctor.nombre_completo} (Usuario: {doctor.nombre_usuario})")
        print(f"   - ID: {doctor.id}")
        print(f"   - Carnet: {doctor.carnet_identidad}")
        print(f"   - Matrícula: {doctor.matricula_profesional}")
        print(f"   - Especialidades: {[e.nombre for e in doctor.especialidades]}")
        print("")

if __name__ == "__main__":
    # Crear la aplicación y contexto
    app = create_app()
    with app.app_context():
        fix_doctor_roles()
