# 🏥 Sistema de Gestión Clínica - ClinicaWeb Docker

Sistema completo de gestión para clínicas médicas desarrollado con Flask y MySQL, completamente dockerizado para facilitar el despliegue.

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker
- Docker Compose

### Instalación y Ejecución (Un Solo Comando)

```bash
docker compose up -d
```

¡Eso es todo! El sistema estará disponible en:
- **Aplicación Web**: http://localhost:5000
- **Base de Datos**: localhost:3307

## 📋 Características del Sistema

### 👥 Roles de Usuario
- **Administrador**: Gestión completa del sistema
- **Doctor**: Gestión de pacientes y consultas

### 🔧 Funcionalidades

#### Para Administradores:
- ✅ Dashboard administrativo
- ✅ Gestión de doctores
- ✅ Gestión de especialidades
- ✅ Reportes del sistema
- ✅ Diagnósticos por doctor

#### Para Doctores:
- ✅ Dashboard personalizado
- ✅ Gestión de pacientes
- ✅ Registro de consultas
- ✅ Expedientes médicos
- ✅ Nuevas consultas

## 🐳 Arquitectura Docker

### Servicios Incluidos:
- **Web**: Aplicación Flask (Puerto 5000)
- **Database**: MySQL 8.0 (Puerto 3307)

### Características:
- ✅ Persistencia de datos con volúmenes
- ✅ Health checks automáticos
- ✅ Sincronización de servicios
- ✅ Red interna segura

## 🛠️ Comandos Útiles

### Iniciar el sistema:
```bash
docker compose up -d
```

### Ver logs en tiempo real:
```bash
docker compose logs -f
```

### Detener el sistema:
```bash
docker compose down
```

### Reiniciar completamente:
```bash
docker compose down
docker compose up -d --build
```

### Acceder al contenedor web:
```bash
docker exec -it clinicaweb_docker-web-1 bash
```

### Acceder a la base de datos:
```bash
docker exec -it clinicaweb_docker-db-1 mysql -u root -p
# Password: root
```

## 🔍 Verificación del Sistema

### Verificar estado de los contenedores:
```bash
docker ps
```

### Ver logs de la aplicación:
```bash
docker logs clinicaweb_docker-web-1
```

### Ver logs de la base de datos:
```bash
docker logs clinicaweb_docker-db-1
```

## 🗄️ Base de Datos

### Configuración:
- **Host**: localhost
- **Puerto**: 3307
- **Usuario**: root
- **Contraseña**: root
- **Base de Datos**: clinicabd

### Conexión externa (opcional):
```bash
mysql -h localhost -P 3307 -u root -p
```

## 🔧 Variables de Entorno

El sistema utiliza las siguientes variables de entorno configuradas automáticamente:

```env
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://root:root@db:3306/clinicabd
```

## 📁 Estructura del Proyecto

```
ClinicaWeb_Docker/
├── docker-compose.yml      # Configuración de servicios
├── Dockerfile             # Imagen de la aplicación
├── requirements.txt       # Dependencias Python
├── run.py                # Punto de entrada
├── wait-for-it.sh        # Script de sincronización
└── project/              # Código fuente de la aplicación
    └── src/
        ├── app.py        # Aplicación Flask principal
        ├── models/       # Modelos de base de datos
        ├── routes/       # Rutas de la aplicación
        ├── templates/    # Plantillas HTML
        └── static/       # Archivos estáticos (CSS, JS)
```

## 🚨 Solución de Problemas

### El contenedor web no inicia:
```bash
docker logs clinicaweb_docker-web-1
```

### Error de conexión a la base de datos:
1. Verificar que el contenedor de BD esté saludable:
   ```bash
   docker ps
   ```
2. Esperar un poco más (la BD tarda en inicializar)

### Puerto ocupado:
Si el puerto 5000 está ocupado, editar `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Cambia 8080 por el puerto que prefieras
```

### Limpiar completamente y reiniciar:
```bash
docker compose down -v
docker system prune -f
docker compose up -d --build
```

## 👥 Uso del Sistema

### Primera vez:
1. Acceder a http://localhost:5000
2. Registrar una cuenta de administrador
3. Configurar doctores y especialidades
4. ¡Comenzar a usar el sistema!

### Credenciales de prueba:
El sistema permite crear usuarios desde la interfaz de registro.

## 🤝 Contribución

Para contribuir al proyecto:
1. Fork del repositorio
2. Crear una rama para tu feature
3. Commit de los cambios
4. Push a la rama
5. Abrir un Pull Request

## 📞 Soporte

Si encuentras algún problema:
1. Revisa los logs con `docker logs`
2. Verifica que Docker esté ejecutándose
3. Asegúrate de que los puertos 5000 y 3307 estén disponibles

---

## 🎯 Para Desarrolladores

### Desarrollo local:
```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd ClinicaWeb_Docker

# Ejecutar
docker compose up -d

# Ver logs en tiempo real durante desarrollo
docker compose logs -f web
```

### Estructura de desarrollo:
- Los cambios en el código se reflejan automáticamente (volume mount)
- La base de datos persiste entre reinicios
- Logs accesibles en tiempo real

¡El sistema está listo para usar! 🎉
