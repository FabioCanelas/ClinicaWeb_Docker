# 🏥 Sistema de Gestión Clínica

Sistema integral de gestión clínica desarrollado con Flask, diseñado para facilitar la administración de consultas médicas, gestión de pacientes y control de expedientes clínicos.

## ✨ Características Principales

### 👨‍💼 Panel de Administrador
- **Gestión de Doctores**: Registro, edición y administración de cuentas médicas
- **Gestión de Especialidades**: Catálogo completo de especialidades médicas
- **Reportes y Estadísticas**: Análisis detallado de consultas y rendimiento
- **Dashboard Ejecutivo**: Vista general del sistema con métricas clave

### 👨‍⚕️ Panel de Doctores
- **Gestión de Pacientes**: Registro completo de información de pacientes
- **Registro de Consultas**: Sistema completo de consultas médicas
- **Expedientes Médicos**: Historial clínico detallado por paciente
- **Dashboard Personal**: Resumen de actividades y consultas recientes

### 🔐 Sistema de Autenticación
- **Roles de Usuario**: Administrador y Doctor con permisos específicos
- **Sesiones Seguras**: Autenticación robusta con Flask-Login
- **Gestión de Credenciales**: Sistema seguro de contraseñas

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.8+ con Flask
- **Base de Datos**: MySQL con SQLAlchemy ORM
- **Frontend**: Bootstrap 5 + HTML5 + CSS3 + JavaScript
- **Autenticación**: Flask-Login
- **Formularios**: Flask-WTF + WTForms
- **Iconos**: Bootstrap Icons

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- MySQL 5.7 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd proyecto_clinica
```

### 2. Crear Entorno Virtual
```bash
python -m venv env

# En Windows
env\Scripts\activate

# En Linux/Mac
source env/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

#### Crear la Base de Datos MySQL
```sql
CREATE DATABASE clinicabd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Ejecutar el Script de Creación de Tablas
```sql
-- Usar el script SQL proporcionado en la documentación
USE clinicabd;

-- Tabla de roles de usuario
CREATE TABLE roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) UNIQUE NOT NULL
);

-- Tabla de usuarios del sistema
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre_usuario VARCHAR(80) UNIQUE NOT NULL,
  contrasena VARCHAR(255) NOT NULL,
  rol_id INT NOT NULL,
  FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- [Resto del script SQL...]
```

### 5. Configurar Variables de Entorno
```bash
# Copiar el archivo de ejemplo
cp src/.env.example src/.env

# Editar el archivo .env con tus configuraciones
SECRET_KEY=tu-clave-secreta-muy-segura
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost/clinicabd
```

### 6. Ejecutar la Aplicación
```bash
python run.py
```

La aplicación estará disponible en: `http://127.0.0.1:5000`

## 👤 Credenciales por Defecto

### Administrador
- **Usuario**: `admin`
- **Contraseña**: `admin123`

### Doctores
Los doctores deben ser creados por el administrador a través del panel de administración.

## 📁 Estructura del Proyecto

```
proyecto_clinica/
├── env/                          # Entorno virtual
├── src/                          # Código fuente
│   ├── models/                   # Modelos de datos
│   │   └── models.py            # Definición de tablas
│   ├── auth/                     # Autenticación
│   │   └── routes.py            # Rutas de login/logout
│   ├── routes/                   # Rutas de la aplicación
│   │   ├── main_routes.py       # Rutas principales
│   │   ├── admin_routes.py      # Rutas del administrador
│   │   └── doctor_routes.py     # Rutas de doctores
│   ├── templates/               # Plantillas HTML
│   │   ├── base.html           # Plantilla base
│   │   ├── auth/               # Plantillas de autenticación
│   │   ├── admin/              # Plantillas del administrador
│   │   └── doctor/             # Plantillas de doctores
│   ├── static/                  # Archivos estáticos
│   │   └── css/
│   │       └── style.css       # Estilos personalizados
│   ├── app.py                  # Configuración principal de Flask
│   └── .env.example           # Ejemplo de variables de entorno
├── requirements.txt            # Dependencias de Python
├── run.py                     # Script de ejecución
└── README.md                  # Documentación
```

## 🔧 Funcionalidades Detalladas

### Gestión de Pacientes
- Registro completo con datos personales y de contacto
- Búsqueda avanzada por carnet, nombre o apellidos
- Historial médico completo
- Estado activo/inactivo

### Sistema de Consultas
- Registro detallado de consultas médicas
- Clasificación por especialidades
- Datos estructurados (síntomas, diagnóstico, tratamiento)
- Filtros por fecha y paciente

### Expedientes Médicos
- Historial cronológico de consultas
- Vista timeline con detalles expandibles
- Información del paciente integrada
- Función de impresión

### Reportes y Estadísticas
- Consultas por especialidad
- Rendimiento por doctor
- Gráficos interactivos
- Métricas del sistema

## 🛡️ Seguridad

- **Autenticación**: Sistema robusto con Flask-Login
- **Autorización**: Control de acceso basado en roles
- **Validación**: Validación de formularios del lado servidor
- **Contraseñas**: Hash seguro con Werkzeug
- **Sesiones**: Gestión segura de sesiones de usuario

## 🎨 Interfaz de Usuario

- **Diseño Responsivo**: Compatible con dispositivos móviles
- **Bootstrap 5**: Framework CSS moderno
- **Iconografía**: Bootstrap Icons para una experiencia visual consistente
- **UX/UI**: Interfaz intuitiva y profesional
- **Accesibilidad**: Cumple con estándares de accesibilidad web

## 📊 Base de Datos

### Tablas Principales
- **roles**: Tipos de usuario (administrador, doctor)
- **usuarios**: Cuentas de acceso al sistema
- **pacientes**: Información de pacientes
- **especialidades**: Catálogo de especialidades médicas
- **expedientes**: Consultas y datos clínicos

### Relaciones
- Usuario → Rol (muchos a uno)
- Expediente → Paciente (muchos a uno)
- Expediente → Especialidad (muchos a uno)
- Expediente → Usuario/Doctor (muchos a uno)

## 🔄 Flujo de Trabajo

### Para Administradores
1. Iniciar sesión con credenciales de administrador
2. Gestionar doctores (crear, editar, desactivar)
3. Administrar especialidades médicas
4. Revisar reportes y estadísticas del sistema

### Para Doctores
1. Iniciar sesión con credenciales proporcionadas
2. Registrar nuevos pacientes
3. Crear consultas médicas detalladas
4. Revisar expedientes de pacientes
5. Gestionar su agenda de consultas

## 🚨 Solución de Problemas

### Error de Conexión a Base de Datos
- Verificar que MySQL esté ejecutándose
- Confirmar credenciales en el archivo `.env`
- Asegurar que la base de datos `clinicabd` existe

### Error de Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error de Permisos
- En Windows: Ejecutar como administrador
- En Linux/Mac: Verificar permisos de archivos

## 📈 Próximas Mejoras

- [ ] Sistema de citas médicas
- [ ] Integración con sistemas de laboratorio
- [ ] Notificaciones por email
- [ ] API REST para integración externa
- [ ] Módulo de facturación
- [ ] Respaldos automáticos
- [ ] Auditoría de acciones

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama para nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

---

**Sistema de Gestión Clínica v1.0** - Desarrollado con ❤️ para mejorar la atención médica