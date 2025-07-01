"""
Script de verificación para la funcionalidad de gestión de administradores
Ejecutar para verificar que todas las funcionalidades estén correctamente implementadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extensions import db
from src.app import create_app
from src.models.models import Usuario, Rol

def verificar_implementacion():
    """
    Verifica que la implementación de gestión de administradores esté completa
    """
    app = create_app()
    
    with app.app_context():
        print("🔍 Verificando implementación de gestión de administradores...\n")
        
        # 1. Verificar campos del modelo Usuario
        print("1. Verificando campos del modelo Usuario:")
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('usuarios')]
        
        campos_requeridos = ['estado', 'fecha_creacion', 'ultimo_acceso', 'cambiar_contrasena']
        for campo in campos_requeridos:
            if campo in columns:
                print(f"   ✅ Campo '{campo}' presente")
            else:
                print(f"   ❌ Campo '{campo}' faltante")
        
        # 2. Verificar roles
        print("\n2. Verificando roles del sistema:")
        rol_admin = Rol.query.filter_by(nombre='administrador').first()
        rol_doctor = Rol.query.filter_by(nombre='doctor').first()
        
        if rol_admin:
            print(f"   ✅ Rol 'administrador' existe (ID: {rol_admin.id})")
        else:
            print("   ❌ Rol 'administrador' no existe")
            
        if rol_doctor:
            print(f"   ✅ Rol 'doctor' existe (ID: {rol_doctor.id})")
        else:
            print("   ❌ Rol 'doctor' no existe")
        
        # 3. Verificar administradores existentes
        print("\n3. Verificando administradores en el sistema:")
        if rol_admin:
            administradores = Usuario.query.filter_by(rol_id=rol_admin.id).all()
            print(f"   📊 Total de administradores: {len(administradores)}")
            
            superadmins = [admin for admin in administradores if admin.superadmin]
            print(f"   👑 Superadministradores: {len(superadmins)}")
            
            for admin in administradores:
                estado = "Activo" if getattr(admin, 'estado', True) else "Inactivo"
                tipo = "SUPERADMIN" if admin.superadmin else "ADMIN"
                print(f"   - {admin.nombre_completo} ({admin.nombre_usuario}) [{tipo}] - {estado}")
        
        # 4. Verificar archivos de plantillas
        print("\n4. Verificando archivos de plantillas:")
        template_path = os.path.join(os.path.dirname(__file__), 'src', 'templates', 'admin', 'administradores.html')
        if os.path.exists(template_path):
            print("   ✅ Plantilla 'administradores.html' existe")
        else:
            print("   ❌ Plantilla 'administradores.html' no encontrada")
        
        # 5. Verificar rutas (importación)
        print("\n5. Verificando importación de rutas:")
        try:
            from src.routes.admin_routes import listar_administradores, toggle_estado_administrador, resetear_password_administrador
            print("   ✅ Rutas de administradores importadas correctamente")
        except ImportError as e:
            print(f"   ❌ Error importando rutas: {e}")
        
        # 6. Verificar métodos del modelo Usuario
        print("\n6. Verificando métodos del modelo Usuario:")
        try:
            usuario_ejemplo = Usuario.query.first()
            if usuario_ejemplo:
                if hasattr(usuario_ejemplo, 'is_admin'):
                    print("   ✅ Método 'is_admin()' disponible")
                if hasattr(usuario_ejemplo, 'is_superadmin'):
                    print("   ✅ Método 'is_superadmin()' disponible")
        except Exception as e:
            print(f"   ⚠️  Error verificando métodos: {e}")
        
        print("\n🎉 Verificación completada!")
        
        # Sugerencias
        print("\n💡 Próximos pasos recomendados:")
        print("   1. Ejecutar 'python migrate_db.py' si faltan campos")
        print("   2. Verificar que el superadministrador esté configurado")
        print("   3. Probar la funcionalidad desde la interfaz web")
        print("   4. Revisar logs de la aplicación para errores")

def crear_superadmin_demo():
    """
    Crea un superadministrador de demostración si no existe
    """
    app = create_app()
    
    with app.app_context():
        from werkzeug.security import generate_password_hash
        
        # Buscar si ya existe un superadmin
        superadmin_existente = Usuario.query.filter_by(superadmin=True).first()
        
        if superadmin_existente:
            print(f"✅ Ya existe un superadministrador: {superadmin_existente.nombre_usuario}")
            return
        
        # Crear rol administrador si no existe
        rol_admin = Rol.query.filter_by(nombre='administrador').first()
        if not rol_admin:
            rol_admin = Rol(nombre='administrador')
            db.session.add(rol_admin)
            db.session.commit()
            print("✅ Rol 'administrador' creado")
        
        # Crear superadministrador
        superadmin = Usuario(
            nombre_usuario='admin.super',
            contrasena=generate_password_hash('SuperAdmin2024*'),
            rol_id=rol_admin.id,
            superadmin=True,
            nombre_completo='Superadministrador del Sistema',
            carnet_identidad='SUPER001',
            estado=True,
            cambiar_contrasena=False
        )
        
        try:
            db.session.add(superadmin)
            db.session.commit()
            print("✅ Superadministrador creado exitosamente:")
            print("   👤 Usuario: admin.super")
            print("   🔑 Contraseña: SuperAdmin2024*")
            print("   ⚠️  Cambie la contraseña después del primer login")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creando superadministrador: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Verificar implementación de gestión de administradores')
    parser.add_argument('--crear-superadmin', action='store_true', 
                       help='Crear superadministrador de demostración')
    
    args = parser.parse_args()
    
    if args.crear_superadmin:
        print("🚀 Creando superadministrador de demostración...")
        crear_superadmin_demo()
    else:
        verificar_implementacion()
