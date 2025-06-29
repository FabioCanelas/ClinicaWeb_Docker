FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script de espera para la base de datos
COPY wait-for-db.py .

# Copia el resto del código del proyecto
COPY . .

# Exponer el puerto
EXPOSE 5000

# Script de salud para verificar que la app esté funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Comando por defecto
CMD ["python", "wait-for-db.py"]