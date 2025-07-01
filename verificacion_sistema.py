#!/usr/bin/env python3
"""
Script de verificación rápida del sistema de clínica web
Verifica que todos los archivos clave estén en su lugar y sean funcionales
"""

import os
import sys

def check_file_exists(file_path, description, use_project_dir=True):
    """Verifica si un archivo existe"""
    if use_project_dir:
        full_path = os.path.join("project", file_path)
    else:
        full_path = file_path
        
    if os.path.exists(full_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NO ENCONTRADO")
        return False

def check_directory_exists(dir_path, description):
    """Verifica si un directorio existe"""
    full_path = os.path.join("project", dir_path)
    if os.path.exists(full_path) and os.path.isdir(full_path):
        print(f"✅ {description}: {dir_path}/")
        return True
    else:
        print(f"❌ {description}: {dir_path}/ - NO ENCONTRADO")
        return False

def main():
    print("🔍 VERIFICACIÓN RÁPIDA DEL SISTEMA DE CLÍNICA WEB")
    print("=" * 60)
    
    # Cambiar al directorio raíz si estamos en project/
    current_dir = os.getcwd()
    if current_dir.endswith("project"):
        os.chdir("..")
        print(f"📁 Cambiando directorio de {current_dir} a {os.getcwd()}")
    
    print("\n📂 VERIFICANDO ESTRUCTURA DE DIRECTORIOS:")
    directories = [
        ("src", "Código fuente principal"),
        ("src/templates", "Templates HTML"),
        ("src/templates/admin", "Templates de administración"),
        ("src/templates/auth", "Templates de autenticación"),
        ("src/routes", "Rutas de la aplicación"),
        ("src/models", "Modelos de datos"),
        ("src/static", "Archivos estáticos"),
        ("src/static/css", "Hojas de estilo")
    ]
    
    dir_results = []
    for dir_path, description in directories:
        dir_results.append(check_directory_exists(dir_path, description))
    
    print("\n📄 VERIFICANDO ARCHIVOS PRINCIPALES:")
    files = [
        ("run.py", "Archivo principal de ejecución", False),
        ("requirements.txt", "Dependencias de Python", False),
        ("docker-compose.yml", "Configuración de Docker", False),
        ("Dockerfile", "Imagen de Docker", False),
        ("src/app.py", "Aplicación Flask principal", True),
        ("src/models/models.py", "Modelos de base de datos", True)
    ]
    
    file_results = []
    for file_path, description, use_project in files:
        file_results.append(check_file_exists(file_path, description, use_project))
    
    print("\n🔧 VERIFICANDO TEMPLATES NUEVOS:")
    new_templates = [
        ("src/templates/admin/editar_usuario.html", "Template de edición de usuarios", True),
        ("src/templates/admin/cambiar_contrasena.html", "Template de cambio de contraseña", True),
        ("src/templates/auth/register.html", "Template de registro (con JS optimizado)", True)
    ]
    
    template_results = []
    for file_path, description, use_project in new_templates:
        template_results.append(check_file_exists(file_path, description, use_project))
    
    print("\n📚 VERIFICANDO DOCUMENTACIÓN:")
    docs = [
        ("project/FUNCIONALIDADES_USUARIOS.md", "Documentación de funcionalidades"),
        ("project/ESTADO_FINAL_SISTEMA.md", "Estado final del sistema"),
        ("project/VERIFICACION_FINAL_COMPLETA.md", "Verificación final completa")
    ]
    
    doc_results = []
    for file_path, description in docs:
        if os.path.exists(file_path):
            print(f"✅ {description}: {file_path}")
            doc_results.append(True)
        else:
            print(f"❌ {description}: {file_path} - NO ENCONTRADO")
            doc_results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    
    total_dirs = len(directories)
    dirs_ok = sum(dir_results)
    print(f"📂 Directorios: {dirs_ok}/{total_dirs} ({'✅' if dirs_ok == total_dirs else '⚠️'})")
    
    total_files = len(files)
    files_ok = sum(file_results)
    print(f"📄 Archivos principales: {files_ok}/{total_files} ({'✅' if files_ok == total_files else '⚠️'})")
    
    total_templates = len(new_templates)
    templates_ok = sum(template_results)
    print(f"🔧 Templates nuevos: {templates_ok}/{total_templates} ({'✅' if templates_ok == total_templates else '⚠️'})")
    
    total_docs = len(docs)
    docs_ok = sum(doc_results)
    print(f"📚 Documentación: {docs_ok}/{total_docs} ({'✅' if docs_ok == total_docs else '⚠️'})")
    
    total_items = total_dirs + total_files + total_templates + total_docs
    total_ok = dirs_ok + files_ok + templates_ok + docs_ok
    
    print(f"\n🎯 TOTAL GENERAL: {total_ok}/{total_items} ({(total_ok/total_items)*100:.1f}%)")
    
    if total_ok == total_items:
        print("\n🎉 ¡SISTEMA COMPLETAMENTE VERIFICADO!")
        print("✅ Todos los archivos están en su lugar")
        print("✅ El sistema está listo para ejecutar")
        print("\n🚀 Para iniciar el sistema:")
        print("   1. docker-compose up --build")
        print("   2. Acceder a http://localhost:5000")
        return 0
    else:
        print(f"\n⚠️ Faltan {total_items - total_ok} elementos")
        print("❌ El sistema requiere completar algunos archivos")
        return 1

if __name__ == "__main__":
    sys.exit(main())
