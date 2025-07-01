@echo off
echo 🚀 Iniciando migración de base de datos...
echo ⚠️  IMPORTANTE: Asegúrate de que los contenedores estén ejecutándose
echo.

REM Verificar si Docker está ejecutándose
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está ejecutándose o no tienes permisos
    pause
    exit /b 1
)

REM Mostrar contenedores disponibles
echo 📋 Contenedores disponibles:
docker ps --format "table {{.Names}}\t{{.Image}}"
echo.

REM Pedir el nombre del contenedor
set /p CONTAINER_NAME="📦 Ingresa el nombre del contenedor de la aplicación: "

echo.
echo 🔧 Ejecutando migración en el contenedor: %CONTAINER_NAME%
echo.

REM Ejecutar la migración dentro del contenedor
docker exec -it %CONTAINER_NAME% python migrate_db.py

echo.
echo ✅ Migración completada!
echo 🔄 Reinicia la aplicación para aplicar los cambios
echo.
pause
