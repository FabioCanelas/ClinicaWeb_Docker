# 🏥 Sistema de Gestión Clínica
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
## Requisitos
- Docker y Docker Compose instalados en tu sistema.
- Acceso a una terminal (CMD, PowerShell o Terminal de Linux/Mac).
### Pasos para la instalación y ejecución
- Clona el repositorio:
  https://github.com/FabioCanelas/ClinicaWeb_Docker.git
- Entra a la carpeta del proyecto:
  cd tu_repositorio
- Comando para Levantar (iniciar) los servicios de la pagina web
 docker-compose up --build