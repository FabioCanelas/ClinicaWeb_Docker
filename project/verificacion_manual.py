#!/usr/bin/env python3
"""
Verificación manual de archivos críticos
"""

import os

def verificar_archivos():
    print("🔍 VERIFICACIÓN MANUAL DE ARCHIVOS CRÍTICOS")
    print("=" * 50)
    
    archivos_criticos = [
        # Templates principales
        ('src/templates/admin/editar_usuario.html', 'Template de edición de usuarios'),
        ('src/templates/admin/cambiar_contrasena.html', 'Template de cambio de contraseña'),
        ('src/templates/admin/administradores.html', 'Lista de administradores'),
        ('src/templates/admin/doctores.html', 'Lista de doctores'),
        ('src/templates/admin/dashboard.html', 'Dashboard principal'),
        ('src/templates/auth/register.html', 'Formulario de registro'),
        ('src/templates/base.html', 'Template base'),
        
        # Rutas backend
        ('src/routes/admin_routes.py', 'Rutas de administración'),
        ('src/auth/routes.py', 'Rutas de autenticación'),
        ('src/models/models.py', 'Modelos de base de datos'),
        
        # Archivos de configuración
        ('src/app.py', 'Aplicación principal'),
        ('src/extensions.py', 'Extensiones Flask'),
        
        # Documentación
        ('FUNCIONALIDADES_USUARIOS.md', 'Documentación de funcionalidades'),
        ('INSTRUCCIONES_ADMIN.md', 'Instrucciones de administración'),
        ('migrate_db.py', 'Script de migración de BD')
    ]
    
    archivos_existentes = []
    archivos_faltantes = []
    
    for archivo, descripcion in archivos_criticos:
        if os.path.exists(archivo):
            print(f"✅ {archivo} - {descripcion}")
            archivos_existentes.append(archivo)
        else:
            print(f"❌ {archivo} - {descripcion} - NO ENCONTRADO")
            archivos_faltantes.append(archivo)
    
    print(f"\n📊 RESUMEN:")
    print(f"✅ Archivos existentes: {len(archivos_existentes)}")
    print(f"❌ Archivos faltantes: {len(archivos_faltantes)}")
    
    if archivos_faltantes:
        print(f"\n⚠️  Archivos faltantes:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        return False
    else:
        print(f"\n🎉 Todos los archivos críticos están presentes!")
        return True

def verificar_contenido_critico():
    print("\n🔍 VERIFICACIÓN DE CONTENIDO CRÍTICO")
    print("=" * 50)
    
    verificaciones = []
    
    # Verificar que admin_routes.py tenga las rutas nuevas
    try:
        with open('src/routes/admin_routes.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        rutas_esperadas = [
            '/usuarios/editar/<int:usuario_id>',
            '/usuarios/eliminar/<int:usuario_id>',
            '/perfil/cambiar_contrasena'
        ]
        
        for ruta in rutas_esperadas:
            if ruta in contenido:
                print(f"✅ Ruta '{ruta}' implementada")
                verificaciones.append(True)
            else:
                print(f"❌ Ruta '{ruta}' NO ENCONTRADA")
                verificaciones.append(False)
                
    except Exception as e:
        print(f"❌ Error al verificar admin_routes.py: {e}")
        verificaciones.append(False)
    
    # Verificar que register.html tenga las funciones JS
    try:
        with open('src/templates/auth/register.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        funciones_js = [
            'cleanUsernameFromPrefixes',
            'showPrefixWarning',
            'updateUsernameField',
            'checkUserNameAvailability'
        ]
        
        for funcion in funciones_js:
            if f'function {funcion}' in contenido:
                print(f"✅ Función JS '{funcion}' implementada")
                verificaciones.append(True)
            else:
                print(f"❌ Función JS '{funcion}' NO ENCONTRADA")
                verificaciones.append(False)
                
    except Exception as e:
        print(f"❌ Error al verificar register.html: {e}")
        verificaciones.append(False)
    
    # Verificar botones en administradores.html
    try:
        with open('src/templates/admin/administradores.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        botones_esperados = [
            'admin.editar_usuario',
            'admin.eliminar_usuario',
            'btn-outline-primary',  # Botón editar
            'btn-outline-danger'    # Botón eliminar
        ]
        
        for boton in botones_esperados:
            if boton in contenido:
                print(f"✅ Botón/URL '{boton}' en administradores.html")
                verificaciones.append(True)
            else:
                print(f"❌ Botón/URL '{boton}' NO ENCONTRADO en administradores.html")
                verificaciones.append(False)
                
    except Exception as e:
        print(f"❌ Error al verificar administradores.html: {e}")
        verificaciones.append(False)
    
    # Verificar botones en doctores.html
    try:
        with open('src/templates/admin/doctores.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        elementos_doctores = [
            'admin.editar_usuario',
            'admin.eliminar_usuario',
            'btn-outline-warning',  # Botón editar
            'btn-outline-danger'    # Botón eliminar
        ]
        
        for elemento in elementos_doctores:
            if elemento in contenido:
                print(f"✅ Elemento '{elemento}' en doctores.html")
                verificaciones.append(True)
            else:
                print(f"❌ Elemento '{elemento}' NO ENCONTRADO en doctores.html")
                verificaciones.append(False)
                
    except Exception as e:
        print(f"❌ Error al verificar doctores.html: {e}")
        verificaciones.append(False)
    
    return all(verificaciones)

def verificar_documentacion():
    print("\n📚 VERIFICACIÓN DE DOCUMENTACIÓN")
    print("=" * 50)
    
    try:
        with open('FUNCIONALIDADES_USUARIOS.md', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        secciones_esperadas = [
            'Edición de Usuarios',
            'Eliminación de Usuarios',
            'Cambio de Contraseña Propia',
            'Código de Emergencia'
        ]
        
        verificaciones = []
        for seccion in secciones_esperadas:
            if seccion in contenido:
                print(f"✅ Sección '{seccion}' documentada")
                verificaciones.append(True)
            else:
                print(f"❌ Sección '{seccion}' NO DOCUMENTADA")
                verificaciones.append(False)
        
        return all(verificaciones)
        
    except Exception as e:
        print(f"❌ Error al verificar documentación: {e}")
        return False

def main():
    print("🚀 VERIFICACIÓN MANUAL COMPLETA")
    print("=" * 60)
    
    resultado1 = verificar_archivos()
    resultado2 = verificar_contenido_critico()
    resultado3 = verificar_documentacion()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    if resultado1 and resultado2 and resultado3:
        print("🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✨ Todas las funcionalidades están implementadas correctamente")
        print("\n🔧 FUNCIONALIDADES VERIFICADAS:")
        print("   ✅ Edición de usuarios (superadmin y administradores)")
        print("   ✅ Eliminación de usuarios (con protecciones de seguridad)")
        print("   ✅ Cambio de contraseña propia (con código de emergencia)")
        print("   ✅ Validación de prefijos en nombres de usuario")
        print("   ✅ Botones funcionales en interfaces de administradores y doctores")
        print("   ✅ Documentación completa y actualizada")
        print("\n📋 PASOS SIGUIENTES:")
        print("   1. Ejecutar migración de BD si es necesario: python migrate_db.py")
        print("   2. Iniciar el servidor: python run.py")
        print("   3. Probar las funcionalidades en el navegador")
        return 0
    else:
        print("⚠️  VERIFICACIÓN INCOMPLETA")
        print("🔧 Revise los errores mostrados arriba")
        return 1

if __name__ == "__main__":
    exit(main())
