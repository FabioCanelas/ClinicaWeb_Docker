"""
Aplicación principal de Flask para el Sistema de Gestión Clínica
Configura la aplicación, base de datos y blueprints principales
"""

from flask import Flask
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
from .extensions import db, login_manager, limiter, csrf  # ✅ import desde extensions con CSRF
from .auth.routes import auth_bp
from .security.wsgi_middleware import SecurityHeadersMiddleware  # 🔒 TC17: WSGI middleware

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
    
    # 🔒 SECURITY: Configuración segura de cookies de sesión (TC10)
    app.config.update(
        SESSION_COOKIE_SECURE=os.environ.get('HTTPS_ENABLED', 'False').lower() == 'true',  # Solo HTTPS en producción
        SESSION_COOKIE_HTTPONLY=True,       # Prevenir acceso via JavaScript
        SESSION_COOKIE_SAMESITE='Lax',      # Prevenir ataques CSRF
        PERMANENT_SESSION_LIFETIME=1800,    # 30 minutos timeout
        SESSION_COOKIE_PATH='/',            # Limitar scope de cookies
        WTF_CSRF_TIME_LIMIT=1800           # CSRF token timeout (30 min)
    )

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)  # ✅ Inicializar rate limiter
    csrf.init_app(app)  # 🔒 TC31: Inicializar protección CSRF
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

    # 🔒 SECURITY TC16: Middleware de validación de sesiones
    @app.before_request
    def validate_session_before_request():
        """
        Valida la integridad de la sesión en cada request
        Previene uso de sesiones manipuladas o comprometidas
        """
        from flask_login import current_user
        from flask import session, request, redirect, url_for
        
        # Skip validation para rutas públicas
        if request.endpoint in ['auth.login', 'main.index', 'static']:
            return
        
        # Verificar si la sesión fue invalidada
        if session.get('_invalidated'):
            session.clear()
            if current_user.is_authenticated:
                from flask_login import logout_user
                logout_user()
            return redirect(url_for('auth.login'))
        
        # Validar consistencia para usuarios autenticados
        if current_user.is_authenticated:
            session_user_id = session.get('_user_id')
            if session_user_id and session_user_id != current_user.id:
                # Session manipulada detectada
                session.clear()
                from flask_login import logout_user
                logout_user()
                return redirect(url_for('auth.login'))

    @app.after_request
    def add_security_headers(response):
        """
        🔒 SECURITY TC17: Headers de seguridad HTTP comprehensivos
        Protege contra múltiples vectores de ataque y oculta información del servidor
        """
        # Headers de cache (ya existentes)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        
        # 🔒 TC17: HEADERS DE SEGURIDAD CRÍTICOS
        
        # Protección contra clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # HSTS - Forzar HTTPS (en producción)
        if app.config.get('HTTPS_ENABLED', False) or os.environ.get('HTTPS_ENABLED', 'False').lower() == 'true':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Protección XSS básica del navegador
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Prevenir MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Content Security Policy (CSP) - Política permisiva para desarrollo
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Permitir scripts inline
            "style-src 'self' 'unsafe-inline'; "  # Permitir estilos inline
            "img-src 'self' data: blob:; "  # Permitir imágenes
            "font-src 'self' data:; "  # Permitir fuentes
            "connect-src 'self'; "
            "frame-ancestors 'self'; "
            "form-action 'self'; "
            "base-uri 'self'; "
            "object-src 'none'"  # Bloquear objetos por seguridad
        )
        # Content Security Policy (CSP) - Temporalmente más permisivo para desarrollo
        # response.headers['Content-Security-Policy'] = csp_policy  # Comentado temporalmente
        
        # Política de referrer
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Controlar permisos de APIs del navegador
        response.headers['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'accelerometer=(), gyroscope=(), magnetometer=(), '
            'usb=(), bluetooth=()'
        )
        
        # Prevenir políticas cross-domain
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
        
        # 🔒 TC17: OCULTAR INFORMACIÓN DEL SERVIDOR
        
        # Forzar header Server genérico (esto sobreescribe cualquier header previo)
        response.headers['Server'] = 'nginx'
        
        # Remover headers que expongan tecnologías específicas
        response.headers.pop('X-Powered-By', None)
        response.headers.pop('X-AspNet-Version', None)
        response.headers.pop('X-AspNetMvc-Version', None)
        response.headers.pop('X-Generator', None)
        
        # Headers de sesión existentes (TC16)
        response.headers['X-Session-Security'] = 'protected'
        
        # Header para identificar que las protecciones están activas
        response.headers['X-Security-Headers'] = 'enabled'
        
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

    # 🔒 TC17: Aplicar middleware WSGI para headers de seguridad avanzados
    app.wsgi_app = SecurityHeadersMiddleware(app.wsgi_app)

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
