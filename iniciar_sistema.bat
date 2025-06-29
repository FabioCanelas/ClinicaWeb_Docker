@echo off
echo ================================================================
echo         🏥 SISTEMA DE GESTIÓN CLÍNICA - INICIO AUTOMÁTICO
echo ================================================================
echo.
echo Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker no está instalado o no está en el PATH
    echo Por favor instala Docker Desktop y asegúrate de que esté ejecutándose
    pause
    exit /b 1
)

echo ✅ Docker detectado
echo.
echo Verificando Docker Compose...
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker Compose no está disponible
    echo Por favor asegúrate de tener Docker Compose instalado
    pause
    exit /b 1
)

echo ✅ Docker Compose detectado
echo.
echo 🚀 Iniciando el sistema de gestión clínica...
echo.
echo Esto puede tomar algunos minutos la primera vez...
echo.

docker compose up -d --build

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo                     ✅ SISTEMA INICIADO EXITOSAMENTE
    echo ================================================================
    echo.
    echo 🌐 Aplicación Web: http://localhost:5000
    echo 🗄️  Base de Datos: localhost:3307 ^(usuario: root, password: root^)
    echo.
    echo 📋 Comandos útiles:
    echo    Ver logs:          docker compose logs -f
    echo    Detener sistema:   docker compose down
    echo    Reiniciar:         docker compose restart
    echo.
    echo 🔍 Verificando estado de los contenedores...
    echo.
    docker ps --filter "name=clinicaweb"
    echo.
    echo ================================================================
    echo El sistema está listo para usar. ¡Que tengas un buen día! 🎉
    echo ================================================================
) else (
    echo.
    echo ❌ Error al iniciar el sistema
    echo.
    echo Ejecuta 'docker compose logs' para ver los detalles del error
    echo.
)

echo.
echo Presiona cualquier tecla para continuar...
pause >nul
