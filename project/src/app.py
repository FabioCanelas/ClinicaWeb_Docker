"""
Aplicación principal de Flask para el Sistema de Gestión Clínica
Configura la aplicación, base de datos y blueprints principales
"""

from flask import Flask
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
from .extensions import db, login_manager  # ✅ import desde extensions
from .auth.routes import auth_bp

load_dotenv()  # Cargar variables desde .env

def create_app():
    """
    Factory function para crear la aplicación Flask
    Configura la base de datos, autenticación y blueprints
    """
    app = Flask(__name__)

    # Configuración de la aplicación
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-secreta-desarrollo')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
        'mysql+pymysql://root@localhost/clinicabd')  # Ajusta tu contraseña si corresponde
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'

    # Importar modelos para que SQLAlchemy los reconozca
    from .models.models import Usuario, Rol, Paciente, Especialidad, Expediente

    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar blueprints
    from .auth.routes import auth_bp
    from .routes.main_routes import main_bp
    from .routes.admin_routes import admin_bp
    from .routes.doctor_routes import doctor_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')

    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    # Crear tablas si no existen con manejo de errores
    with app.app_context():
        import time
        import sqlalchemy.exc
        
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                db.create_all()
                crear_datos_iniciales()
                print("Base de datos inicializada correctamente")
                break
            except sqlalchemy.exc.OperationalError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Error al conectar a la base de datos después de {max_retries} intentos: {str(e)}")
                    raise
                print(f"Error al conectar a la base de datos. Reintentando en 5 segundos... ({retry_count}/{max_retries})")
                time.sleep(5)

    return app


def crear_datos_iniciales():
    """
    Crea datos iniciales necesarios para el funcionamiento del sistema
    Incluye roles básicos y usuario administrador
    """
    from .models.models import Usuario, Rol, Especialidad
    import sqlalchemy.exc

    try:
        # Crear roles si no existen
        admin_rol = Rol.query.filter_by(nombre='administrador').first()
        if not admin_rol:
            admin_rol = Rol(nombre='administrador')
            doctor_rol = Rol(nombre='doctor')
            db.session.add_all([admin_rol, doctor_rol])
            db.session.commit()
            print("Roles creados correctamente.")
        else:
            print("Roles ya existentes.")

        # Crear usuario administrador si no existe
        if not Usuario.query.filter_by(nombre_usuario='admin.superadmin').first():
            admin_user = Usuario(
                nombre_usuario='admin.superadmin',
                nombre_completo='Administrador General',
                contrasena=generate_password_hash('Superadmin@123'),
                rol_id=admin_rol.id,
                superadmin=True,
                carnet_identidad='1234567'  # Agregando un valor por defecto
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario superadmin creado correctamente.")
        else:
            print("Usuario superadmin ya existe.")

        # Crear especialidades básicas si no existen
        especialidades_basicas = [
            'Medicina General', 'Cardiología', 'Pediatría', 
            'Ginecología', 'Dermatología', 'Neurología'
        ]

        for esp_nombre in especialidades_basicas:
            if not Especialidad.query.filter_by(nombre=esp_nombre).first():
                especialidad = Especialidad(nombre=esp_nombre)
                db.session.add(especialidad)
        
        db.session.commit()
        print("Datos iniciales creados correctamente.")
        
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print(f"Error de integridad en la base de datos: {str(e)}")
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear datos iniciales: {str(e)}")


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
