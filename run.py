import os
from dotenv import load_dotenv
from project.src.app import create_app

# Cargar variables de entorno desde .env
load_dotenv()

if __name__ == '__main__':
    # Crear la aplicación Flask
    app = create_app()
    
    # Configuración para desarrollo
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    # Forzar host a 0.0.0.0 para Docker
    host = '0.0.0.0'
    
    print("=" * 60)
    print("🏥 SISTEMA DE GESTIÓN CLÍNICA")
    print("=" * 60)
    print(f"🌐 Servidor: http://{host}:{port}")
    print(f"🔧 Modo debug: {'Activado' if debug_mode else 'Desactivado'}")
    print(f"🗄️  Base de datos: {os.environ.get('DATABASE_URL', 'No configurada')}")
    print("=" * 60)
    print("📋 Credenciales por defecto:")
    print("   👤 Administrador: admin / admin123")
    print("   👨‍⚕️ Doctores: (Deben ser creados por el administrador)")
    print("=" * 60)
    
    # Ejecutar la aplicación
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )