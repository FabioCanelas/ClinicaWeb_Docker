# ⚙️ Configuración y Mantenimiento del Sistema

## 🔧 Scripts de Utilidad

### Windows:
```cmd
# Iniciar sistema
iniciar_sistema.bat

# Detener sistema
docker compose down

# Ver logs
docker compose logs -f

# Reiniciar completamente
docker compose down -v && docker compose up -d --build
```

### Linux/Mac:
```bash
# Hacer ejecutable el script (solo la primera vez)
chmod +x iniciar_sistema.sh

# Iniciar sistema
./iniciar_sistema.sh

# Detener sistema
docker compose down

# Ver logs
docker compose logs -f

# Reiniciar completamente
docker compose down -v && docker compose up -d --build
```

## 🗄️ Gestión de Base de Datos

### Backup de la base de datos:
```bash
docker exec clinicaweb_db mysqldump -u root -proot clinicabd > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar backup:
```bash
docker exec -i clinicaweb_db mysql -u root -proot clinicabd < backup_file.sql
```

### Acceso directo a MySQL:
```bash
docker exec -it clinicaweb_db mysql -u root -proot clinicabd
```

## 🔍 Monitoreo

### Verificar uso de recursos:
```bash
docker stats
```

### Ver logs específicos:
```bash
# Logs de la aplicación web
docker logs clinicaweb_app -f

# Logs de la base de datos
docker logs clinicaweb_db -f
```

### Verificar salud de los contenedores:
```bash
docker ps
```

## 🚨 Solución de Problemas Comunes

### Puerto ocupado:
```bash
# Verificar qué proceso usa el puerto 5000
netstat -tulpn | grep 5000  # Linux
netstat -ano | findstr 5000  # Windows

# Cambiar puerto en docker-compose.yml
ports:
  - "8080:5000"  # Cambia 8080 por el puerto deseado
```

### Problemas de permisos (Linux):
```bash
sudo chown -R $USER:$USER .
```

### Limpiar sistema Docker:
```bash
# Limpiar contenedores detenidos
docker container prune -f

# Limpiar imágenes no utilizadas
docker image prune -f

# Limpiar todo el sistema
docker system prune -af

# Limpiar volúmenes (⚠️ ESTO BORRA TODOS LOS DATOS)
docker volume prune -f
```

### Reconstruir desde cero:
```bash
docker compose down -v
docker rmi clinicaweb_docker-web:latest
docker compose up -d --build
```

## 📊 Variables de Entorno Configurables

Crear archivo `.env` para personalizar:

```env
# Configuración de la aplicación
FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000

# Configuración de la base de datos
MYSQL_DATABASE=clinicabd
MYSQL_ROOT_PASSWORD=tu_password_seguro
DATABASE_URL=mysql+pymysql://root:tu_password_seguro@db:3306/clinicabd

# Configuración de puertos
WEB_PORT=5000
DB_PORT=3307
```

## 🔐 Seguridad para Producción

### Cambios recomendados para producción:

1. **Cambiar contraseñas por defecto**
2. **Usar secrets en lugar de variables de entorno**
3. **Configurar SSL/TLS**
4. **Limitar acceso a la base de datos**
5. **Usar un proxy reverso (nginx)**

### Ejemplo de configuración de producción:
```yaml
# docker-compose.prod.yml
services:
  db:
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
    secrets:
      - db_root_password
    ports: []  # No exponer puerto externamente

secrets:
  db_root_password:
    file: ./secrets/db_root_password.txt
```

## 📈 Optimización de Rendimiento

### Para desarrollo:
- Usar volúmenes para desarrollo en vivo
- Habilitar debug mode
- Logs verbosos

### Para producción:
- Usar bind mounts mínimos
- Deshabilitar debug mode
- Configurar logs estructurados
- Usar imágenes optimizadas

## 🔄 Actualizaciones

### Actualizar el sistema:
```bash
git pull origin main
docker compose down
docker compose up -d --build
```

### Actualizar solo la aplicación:
```bash
docker compose up -d --build web
```

### Actualizar solo la base de datos:
```bash
docker compose up -d --build db
```
