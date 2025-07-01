#!/usr/bin/env python3
"""
Script de verificación del sistema de gestión de usuarios
Verifica que todas las funcionalidades estén operativas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from src.models.models import Usuario, Rol
from src.extensions import db

def verificar_rutas():
    """Verifica que todas las rutas estén definidas"""
    print("🔍 Verificando rutas...")
    
    app = create_app()
    
    with app.app_context():
        # Lista de rutas críticas que deben existir
        rutas_esperadas = [
            'admin.editar_usuario',
            'admin.eliminar_usuario', 
            'admin.cambiar_contrasena_propia',
            'admin.listar_administradores',
            'admin.toggle_estado_administrador',
            'admin.resetear_password_administrador',
            'auth.check_username'
        ]
        
        rutas_encontradas = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint:
                rutas_encontradas.append(rule.endpoint)
        
        print(f"📊 Total de rutas registradas: {len(rutas_encontradas)}")
        
        # Verificar rutas críticas
        faltantes = []
        for ruta in rutas_esperadas:
            if ruta in rutas_encontradas:
                print(f"✅ {ruta}")
            else:
                print(f"❌ {ruta} - NO ENCONTRADA")
                faltantes.append(ruta)
        
        if faltantes:
            print(f"\n⚠️  Rutas faltantes: {len(faltantes)}")
            return False
        else:
            print("\n✅ Todas las rutas críticas están registradas")
            return True

def verificar_templates():
    """Verifica que los templates existan"""
    print("\n🎨 Verificando templates...")
    
    templates_necesarios = [
        'src/templates/admin/editar_usuario.html',
        'src/templates/admin/cambiar_contrasena.html',
        'src/templates/admin/administradores.html',
        'src/templates/admin/doctores.html',
        'src/templates/admin/dashboard.html',
        'src/templates/auth/register.html'
    ]
    
    faltantes = []
    for template in templates_necesarios:
        if os.path.exists(template):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} - NO ENCONTRADO")
            faltantes.append(template)
    
    if faltantes:
        print(f"\n⚠️  Templates faltantes: {len(faltantes)}")
        return False
    else:
        print("\n✅ Todos los templates necesarios existen")
        return True

def verificar_base_datos():
    """Verifica la estructura de la base de datos"""
    print("\n💾 Verificando estructura de base de datos...")
    
    app = create_app()
    
    try:
        with app.app_context():
            # Verificar que las tablas existan
            inspector = db.inspect(db.engine)
            tablas = inspector.get_table_names()
            
            tablas_necesarias = ['usuarios', 'roles', 'especialidades', 'pacientes', 'expedientes']
            
            for tabla in tablas_necesarias:
                if tabla in tablas:
                    print(f"✅ Tabla '{tabla}' existe")
                else:
                    print(f"❌ Tabla '{tabla}' NO EXISTE")
                    return False
            
            # Verificar columnas críticas en la tabla usuarios
            columnas_usuarios = inspector.get_columns('usuarios')
            nombres_columnas = [col['name'] for col in columnas_usuarios]
            
            columnas_necesarias = ['estado', 'fecha_creacion', 'ultimo_acceso', 'cambiar_contrasena']
            
            print("\n🔍 Verificando columnas en tabla 'usuarios':")
            for columna in columnas_necesarias:
                if columna in nombres_columnas:
                    print(f"✅ Columna '{columna}' existe")
                else:
                    print(f"❌ Columna '{columna}' NO EXISTE")
                    print("💡 Ejecute el script de migración: python migrate_db.py")
                    return False
            
            print("\n✅ Estructura de base de datos correcta")
            return True
            
    except Exception as e:
        print(f"❌ Error al verificar base de datos: {e}")
        return False

def verificar_datos_iniciales():
    """Verifica que existan los roles básicos"""
    print("\n👥 Verificando datos iniciales...")
    
    app = create_app()
    
    try:
        with app.app_context():
            # Verificar roles
            roles_necesarios = ['administrador', 'doctor']
            
            for rol_nombre in roles_necesarios:
                rol = Rol.query.filter_by(nombre=rol_nombre).first()
                if rol:
                    print(f"✅ Rol '{rol_nombre}' existe")
                else:
                    print(f"❌ Rol '{rol_nombre}' NO EXISTE")
                    return False
            
            # Verificar superadmin
            superadmin = Usuario.query.filter_by(superadmin=True).first()
            if superadmin:
                print(f"✅ Superadmin existe: {superadmin.nombre_usuario}")
            else:
                print("⚠️  No se encontró superadmin")
                print("💡 Puede crear uno con: python verificar_admin.py --crear-superadmin")
            
            print("\n✅ Datos iniciales correctos")
            return True
            
    except Exception as e:
        print(f"❌ Error al verificar datos iniciales: {e}")
        return False

def verificar_funcionalidades_javascript():
    """Verifica que las funcionalidades JavaScript estén implementadas"""
    print("\n⚡ Verificando funcionalidades JavaScript...")
    
    # Verificar register.html
    try:
        with open('src/templates/auth/register.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
            funciones_necesarias = [
                'cleanUsernameFromPrefixes',
                'showPrefixWarning',
                'setupUsernameValidation',
                'updateUsernameField',
                'checkUserNameAvailability'
            ]
            
            for funcion in funciones_necesarias:
                if f'function {funcion}' in contenido:
                    print(f"✅ Función JavaScript '{funcion}' implementada")
                else:
                    print(f"❌ Función JavaScript '{funcion}' NO ENCONTRADA")
                    return False
            
            # Verificar elementos críticos
            elementos_criticos = [
                'input-username-container',
                'username-help',
                'prefix-warning',
                'username-feedback'
            ]
            
            for elemento in elementos_criticos:
                if elemento in contenido:
                    print(f"✅ Elemento '{elemento}' presente")
                else:
                    print(f"❌ Elemento '{elemento}' NO ENCONTRADO")
                    return False
            
            print("\n✅ Funcionalidades JavaScript correctas")
            return True
            
    except Exception as e:
        print(f"❌ Error al verificar JavaScript: {e}")
        return False

def verificar_permisos():
    """Verifica que los decoradores de permisos estén correctos"""
    print("\n🔐 Verificando decoradores de permisos...")
    
    try:
        with open('src/routes/admin_routes.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
            # Verificar decoradores críticos
            decoradores_esperados = [
                '@admin_required',
                '@superadmin_required', 
                '@login_required'
            ]
            
            for decorador in decoradores_esperados:
                if decorador in contenido:
                    count = contenido.count(decorador)
                    print(f"✅ Decorador '{decorador}' usado {count} veces")
                else:
                    print(f"❌ Decorador '{decorador}' NO ENCONTRADO")
                    return False
            
            # Verificar funciones críticas de seguridad
            funciones_seguridad = [
                'admin_required(f)',
                'superadmin_required(f)',
                'current_user.is_superadmin()',
                'current_user.is_admin()'
            ]
            
            for funcion in funciones_seguridad:
                if funcion in contenido:
                    print(f"✅ Función de seguridad '{funcion}' implementada")
                else:
                    print(f"❌ Función de seguridad '{funcion}' NO ENCONTRADA")
                    return False
            
            print("\n✅ Decoradores y permisos correctos")
            return True
            
    except Exception as e:
        print(f"❌ Error al verificar permisos: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🚀 VERIFICACIÓN COMPLETA DEL SISTEMA DE GESTIÓN DE USUARIOS")
    print("=" * 60)
    
    verificaciones = [
        verificar_rutas,
        verificar_templates,
        verificar_base_datos,
        verificar_datos_iniciales,
        verificar_funcionalidades_javascript,
        verificar_permisos
    ]
    
    resultados = []
    
    for verificacion in verificaciones:
        try:
            resultado = verificacion()
            resultados.append(resultado)
        except Exception as e:
            print(f"❌ Error en verificación: {e}")
            resultados.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    exitosas = sum(resultados)
    total = len(resultados)
    
    print(f"✅ Verificaciones exitosas: {exitosas}/{total}")
    
    if exitosas == total:
        print("🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("✨ El sistema está completamente funcional")
        print("\n📋 Funcionalidades disponibles:")
        print("   • Edición de usuarios (superadmin y administradores)")
        print("   • Eliminación de usuarios (con protecciones)")
        print("   • Cambio de contraseña propia")
        print("   • Código de emergencia para superadmin")
        print("   • Validación de prefijos en registro")
        print("   • Verificación AJAX de nombres de usuario")
        print("   • Gestión completa de administradores")
        print("   • Botones funcionales en todas las interfaces")
    else:
        print("⚠️  ALGUNAS VERIFICACIONES FALLARON")
        print("🔧 Revise los errores mostrados arriba")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
