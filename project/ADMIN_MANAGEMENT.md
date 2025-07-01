# Gestión de Administradores - Sistema Clínica

## Descripción
Nueva funcionalidad que permite al **superadministrador** gestionar usuarios con rol de administrador en el sistema.

## Características Implementadas

### 1. Vista de Lista de Administradores
- **URL**: `/admin/administradores`
- **Acceso**: Solo superadministrador
- **Funcionalidades**:
  - Lista todos los administradores del sistema
  - Muestra información detallada: nombre, usuario, carnet, estado, fechas
  - Identificación especial del superadministrador
  - Acciones disponibles por administrador

### 2. Gestión de Estados
- **Activar/Desactivar**: Los administradores pueden ser activados o desactivados
- **Protección**: El superadministrador no puede ser desactivado
- **Control de acceso**: Los administradores inactivos no pueden acceder al sistema

### 3. Reseteo de Contraseñas
- **Generación automática**: Contraseña temporal basada en `Admin{carnet}*`
- **Forzar cambio**: Se marca para cambio obligatorio en el próximo login
- **Protección**: No se puede resetear la contraseña del superadministrador

### 4. Validación en Formularios
- **Prevención de prefijos**: El sistema evita que se escriban manualmente "dr." o "admin."
- **Limpieza automática**: Los prefijos se eliminan automáticamente del input
- **Advertencias visuales**: Mensajes temporales cuando se detectan prefijos

## Campos Agregados al Modelo Usuario

```python
estado = db.Column(db.Boolean, default=True)  # Estado activo/inactivo
fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de registro
ultimo_acceso = db.Column(db.DateTime, nullable=True)  # Último acceso
cambiar_contrasena = db.Column(db.Boolean, default=False)  # Forzar cambio
```

## Archivos Creados/Modificados

### Nuevos Archivos
1. `templates/admin/administradores.html` - Vista principal de administradores
2. `migrate_db.py` - Script de migración de base de datos
3. `ADMIN_MANAGEMENT.md` - Esta documentación

### Archivos Modificados
1. `routes/admin_routes.py` - Nuevas rutas para gestión de administradores
2. `models/models.py` - Campos adicionales en modelo Usuario
3. `templates/admin/dashboard.html` - Botón y tarjeta clickeable para administradores
4. `templates/base.html` - Enlace en sidebar para superadmins
5. `templates/auth/register.html` - Validación mejorada de prefijos

## Rutas Implementadas

### GET /admin/administradores
- **Descripción**: Lista todos los administradores
- **Permisos**: Solo superadministrador
- **Plantilla**: `admin/administradores.html`

### POST /admin/administradores/toggle_estado/<int:admin_id>
- **Descripción**: Activa/desactiva un administrador
- **Permisos**: Solo superadministrador
- **Validaciones**: No permite desactivar al superadmin

### POST /admin/administradores/resetear_password/<int:admin_id>
- **Descripción**: Resetea la contraseña de un administrador
- **Permisos**: Solo superadministrador
- **Comportamiento**: Genera contraseña temporal y fuerza cambio

## Seguridad Implementada

### Decoradores de Seguridad
```python
@superadmin_required
def listar_administradores():
    # Solo superadministrador puede acceder
```

### Validaciones de Negocio
- No se puede desactivar al superadministrador
- No se puede resetear la contraseña del superadministrador
- Solo se pueden gestionar usuarios con rol "administrador"

### Validación Frontend
- Confirmaciones para acciones críticas
- Mensajes informativos sobre limitaciones
- Auto-ocultación de alertas exitosas

## Uso

### Para Acceder a la Gestión de Administradores
1. Iniciar sesión como superadministrador
2. Desde el dashboard: click en la tarjeta "Administradores"
3. O usar el menú lateral: "Administradores"
4. O acceder directamente: `/admin/administradores`

### Para Crear Nuevos Administradores
1. Usar el botón "Nuevo Administrador" en la lista
2. O usar el enlace "Registrar Usuario" del sidebar
3. Seleccionar rol "Administrador" (solo disponible para superadmin)

### Para Gestionar Administradores Existentes
1. **Activar/Desactivar**: Click en botón correspondiente
2. **Resetear Contraseña**: Click en "Resetear Password"
3. **Ver Detalles**: Información visible en la tabla

## Migración de Base de Datos

Para aplicar los cambios en la base de datos:

```bash
python migrate_db.py
```

Este script:
- Agrega las nuevas columnas al modelo Usuario
- Actualiza usuarios existentes con valores por defecto
- Maneja errores y rollback automático

## Estilos y UX

### Características Visuales
- Tarjetas con efecto hover para navegación
- Badges para identificar roles y estados
- Iconos Bootstrap para mejor UX
- Colores consistentes con el diseño del sistema

### Responsividad
- Diseño adaptable para dispositivos móviles
- Tablas responsive con scroll horizontal
- Navegación optimizada para pantallas pequeñas

## Consideraciones Técnicas

### Performance
- Uso de `joinedload` para optimizar consultas
- Índices en campos únicos (carnet_identidad, nombre_usuario)
- Paginación futura recomendada para grandes volúmenes

### Mantenimiento
- Código modular y bien documentado
- Separación clara de responsabilidades
- Logging para acciones críticas

## Próximas Mejoras Recomendadas

1. **Auditoría**: Log de acciones sobre administradores
2. **Notificaciones**: Email al resetear contraseñas
3. **Roles granulares**: Permisos más específicos
4. **Historial**: Registro de cambios de estado
5. **Bulk actions**: Acciones masivas sobre administradores

---

**Nota**: Esta funcionalidad está diseñada exclusivamente para superadministradores y mantiene la seguridad y integridad del sistema.
