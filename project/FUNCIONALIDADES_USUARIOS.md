# Gestión de Usuarios - Funcionalidades de Edición y Eliminación

## Funcionalidades Implementadas

### 1. Edición de Usuarios

#### Para Administradores Regulares:
- ✅ Pueden **editar doctores** completamente (información personal, matrícula, especialidades, contraseña)
- ❌ **NO** pueden editar otros administradores

#### Para Superadministrador:
- ✅ Puede **editar cualquier usuario** (administradores y doctores)
- ✅ Puede **editarse a sí mismo** incluida su contraseña
- ✅ Funcionalidad de **recuperación de contraseña** si la olvida

### 2. Eliminación de Usuarios

#### Para Administradores Regulares:
- ✅ Pueden **eliminar doctores**
- ❌ **NO** pueden eliminar administradores

#### Para Superadministrador:
- ✅ Puede **eliminar cualquier usuario** excepto a sí mismo
- ✅ Confirmación múltiple para prevenir eliminaciones accidentales

### 3. Cambio de Contraseña Propia

#### Para Todos los Administradores:
- ✅ Ruta dedicada para cambiar su propia contraseña
- ✅ Validación de contraseña actual
- ✅ Validaciones de seguridad (mayúsculas, caracteres especiales, longitud)

#### Para Superadministrador (Funcionalidad Especial):
- ✅ **Código de emergencia** si olvida su contraseña
- ✅ Código: `{carnet_identidad}{nombre_usuario}` (ejemplo: `1234567admin`)
- ✅ Permite recuperar acceso sin intervención externa

## Rutas Nuevas Agregadas

### `/admin/usuarios/editar/<int:usuario_id>`
- **Métodos:** GET, POST
- **Permisos:** Administradores (con restricciones según nivel)
- **Función:** Permite editar información de usuarios
- **Template:** `admin/editar_usuario.html`

### `/admin/usuarios/eliminar/<int:usuario_id>`
- **Métodos:** POST
- **Permisos:** Solo superadministrador
- **Función:** Elimina usuarios del sistema
- **Protecciones:** No puede eliminar al superadmin

### `/admin/perfil/cambiar_contrasena`
- **Métodos:** GET, POST
- **Permisos:** Cualquier administrador
- **Función:** Cambio de contraseña propia
- **Template:** `admin/cambiar_contrasena.html`

## Templates Creados

### 1. `admin/editar_usuario.html`
**Características:**
- Formulario adaptativo según el tipo de usuario (doctor vs administrador)
- Campos específicos para doctores (matrícula, especialidades)
- Sección de cambio de contraseña opcional
- Validación en tiempo real
- Información de auditoría (fechas de registro y último acceso)

### 2. `admin/cambiar_contrasena.html`
**Características:**
- Verificación de contraseña actual
- Código de emergencia para superadmin
- Validación avanzada de nueva contraseña
- Medidor de fortaleza de contraseña
- Consejos de seguridad

## Botones y Enlaces Agregados

### En `admin/administradores.html`:
- ✅ Botón **"Editar"** para todos los administradores
- ✅ Botón **"Eliminar"** para administradores regulares
- ❌ Superadmin marcado como "Protegido" (no se puede eliminar)

### En `admin/doctores.html`:
- ✅ Botón **"Editar"** funcional (reemplaza el anterior no funcional)
- ✅ Botón **"Eliminar"** funcional (reemplaza el anterior no funcional)
- ✅ Confirmación con advertencia sobre expedientes

### En el Dashboard (`admin/dashboard.html`):
- ✅ Botón **"Mi Contraseña"** en acciones rápidas

### En la Barra Lateral (`base.html`):
- ✅ Enlace **"Mi Contraseña"** en menú de administradores

## Validaciones y Seguridad

### Validaciones de Contraseña:
- ✅ Mínimo 8 caracteres
- ✅ Al menos una letra mayúscula
- ✅ Al menos un carácter especial
- ✅ Confirmación de contraseña

### Protecciones Implementadas:
- ✅ Verificación de permisos por nivel de usuario
- ✅ Prevención de edición/eliminación del superadmin por otros
- ✅ Validación de duplicados (carnet, matrícula)
- ✅ Confirmaciones para acciones destructivas
- ✅ Manejo de errores con rollback de base de datos

### Código de Emergencia para Superadmin:
- **Formato:** `{carnet_identidad}{nombre_usuario}`
- **Ejemplo:** Si el superadmin tiene carnet "1234567" y usuario "admin", el código es "1234567admin"
- **Uso:** Solo cuando olvida completamente su contraseña actual
- **Seguridad:** Se basa en información que solo el superadmin conoce

## Flujo de Uso

### Para Editar un Usuario:
1. Ir a la lista de administradores o doctores
2. Hacer clic en el botón "Editar" (ícono de lápiz)
3. Modificar los campos necesarios
4. Opcionalmente cambiar la contraseña
5. Guardar cambios

### Para Eliminar un Usuario:
1. Ir a la lista correspondiente
2. Hacer clic en el botón "Eliminar" (ícono de basura)
3. Confirmar la acción en el diálogo
4. El usuario será eliminado permanentemente

### Para Cambiar Contraseña Propia:
1. Desde el dashboard o menú lateral, hacer clic en "Mi Contraseña"
2. Ingresar contraseña actual (o código de emergencia si es superadmin)
3. Ingresar nueva contraseña
4. Confirmar nueva contraseña
5. Guardar cambios

### Recuperación de Contraseña del Superadmin:
1. Ir a "Mi Contraseña"
2. Hacer clic en "¿Olvidó su contraseña?"
3. Ingresar el código de emergencia: `{carnet}{usuario}`
4. Establecer nueva contraseña
5. Guardar cambios

## Consideraciones Importantes

### ⚠️ Acciones Irreversibles:
- La **eliminación de usuarios** es permanente
- Se recomienda hacer respaldo antes de eliminar doctores con expedientes

### 🔐 Seguridad:
- Solo el superadmin puede eliminar usuarios
- Los administradores regulares tienen acceso limitado
- El superadmin no puede ser eliminado por ningún usuario

### 📝 Auditoría:
- Se mantiene registro de fechas de creación y último acceso
- Los cambios de contraseña resetean el flag `cambiar_contrasena`

### 🚀 Próximas Mejoras Sugeridas:
- Log de auditoría para cambios de usuarios
- Notificaciones por email para cambios de contraseña
- Políticas de contraseña más avanzadas
- Backup automático antes de eliminaciones

## Solución de Problemas

### Error: "Unknown column 'usuarios.estado'"
- **Causa:** Falta migrar la base de datos
- **Solución:** Ejecutar los scripts de migración incluidos en el proyecto

### No aparecen los botones de editar/eliminar:
- **Causa:** Permisos insuficientes o usuario no logueado como administrador
- **Solución:** Verificar que está logueado como administrador o superadmin

### Error al cambiar contraseña del superadmin:
- **Causa:** Código de emergencia incorrecto
- **Solución:** Usar formato `{carnet}{usuario}` sin espacios ni puntos
