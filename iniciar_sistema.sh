#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================"
echo "         🏥 SISTEMA DE GESTIÓN CLÍNICA - INICIO AUTOMÁTICO"
echo "================================================================"
echo ""

# Verificar Docker
echo "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker no está instalado o no está en el PATH${NC}"
    echo "Por favor instala Docker y asegúrate de que esté ejecutándose"
    exit 1
fi

echo -e "${GREEN}✅ Docker detectado${NC}"
echo ""

# Verificar Docker Compose
echo "Verificando Docker Compose..."
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Error: Docker Compose no está disponible${NC}"
    echo "Por favor asegúrate de tener Docker Compose instalado"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose detectado${NC}"
echo ""

# Verificar que Docker esté ejecutándose
echo "Verificando que Docker esté ejecutándose..."
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Error: Docker no está ejecutándose${NC}"
    echo "Por favor inicia Docker Desktop o el servicio de Docker"
    exit 1
fi

echo -e "${GREEN}✅ Docker está ejecutándose${NC}"
echo ""

echo -e "${BLUE}🚀 Iniciando el sistema de gestión clínica...${NC}"
echo ""
echo -e "${YELLOW}Esto puede tomar algunos minutos la primera vez...${NC}"
echo ""

# Iniciar el sistema
docker compose up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================"
    echo -e "${GREEN}                ✅ SISTEMA INICIADO EXITOSAMENTE${NC}"
    echo "================================================================"
    echo ""
    echo -e "${BLUE}🌐 Aplicación Web:${NC} http://localhost:5000"
    echo -e "${BLUE}🗄️  Base de Datos:${NC} localhost:3307 (usuario: root, password: root)"
    echo ""
    echo -e "${YELLOW}📋 Comandos útiles:${NC}"
    echo "   Ver logs:          docker compose logs -f"
    echo "   Detener sistema:   docker compose down"
    echo "   Reiniciar:         docker compose restart"
    echo ""
    echo -e "${BLUE}🔍 Verificando estado de los contenedores...${NC}"
    echo ""
    docker ps --filter "name=clinicaweb"
    echo ""
    echo "================================================================"
    echo -e "${GREEN}El sistema está listo para usar. ¡Que tengas un buen día! 🎉${NC}"
    echo "================================================================"
    
    # Opcional: abrir el navegador automáticamente
    if command -v xdg-open &> /dev/null; then
        echo ""
        echo -e "${YELLOW}Abriendo navegador en 3 segundos...${NC}"
        sleep 3
        xdg-open http://localhost:5000
    elif command -v open &> /dev/null; then
        echo ""
        echo -e "${YELLOW}Abriendo navegador en 3 segundos...${NC}"
        sleep 3
        open http://localhost:5000
    fi
    
else
    echo ""
    echo -e "${RED}❌ Error al iniciar el sistema${NC}"
    echo ""
    echo "Ejecuta 'docker compose logs' para ver los detalles del error"
    echo ""
    exit 1
fi
