#!/bin/bash

# Script para ejecutar la migración de base de datos en Docker
# Este script debe ejecutarse desde el directorio del proyecto

echo "🚀 Iniciando migración de base de datos..."
echo "⚠️  IMPORTANTE: Asegúrate de que los contenedores estén ejecutándose"

# Verificar si Docker está corriendo
if ! docker ps &> /dev/null; then
    echo "❌ Docker no está ejecutándose o no tienes permisos"
    exit 1
fi

# Obtener el nombre del contenedor de la aplicación
CONTAINER_NAME=$(docker ps --format "table {{.Names}}" | grep -E "(app|web|clinic)" | head -1)

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ No se encontró el contenedor de la aplicación"
    echo "📋 Contenedores disponibles:"
    docker ps --format "table {{.Names}}\t{{.Image}}"
    echo ""
    read -p "Ingresa el nombre del contenedor de la aplicación: " CONTAINER_NAME
fi

echo "📦 Usando contenedor: $CONTAINER_NAME"

# Ejecutar la migración dentro del contenedor
echo "🔧 Ejecutando migración..."
docker exec -it $CONTAINER_NAME python migrate_db.py

echo "✅ Migración completada!"
echo "🔄 Reinicia la aplicación para aplicar los cambios"
