FROM python:3.11

WORKDIR /app

# Copia primero los archivos necesarios para la instalación
COPY requirements.txt .
COPY wait-for-it.sh .

RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto
COPY . .

# Comando por defecto: espera a que MySQL esté listo y luego ejecuta Flask
CMD ["bash", "-c", "chmod +x ./wait-for-it.sh && ./wait-for-it.sh db:3306 -- python run.py"]