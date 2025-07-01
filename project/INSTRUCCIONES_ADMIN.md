# 🎯 Instrucciones Rápidas - Gestión de Administradores

## ⚡ Configuración Inicial

### 1. Migrar Base de Datos
```bash
cd project
python migrate_db.py
```

### 2. Verificar Implementación (Opcional)
```bash
python verificar_admin.py
```

### 3. Crear Superadministrador Demo (Si es necesario)
```bash
python verificar_admin.py --crear-superadmin
```

## 🚀 Funcionalidades Disponibles

### Para el Superadministrador:

#### 📋 Ver Lista de Administradores
- **Dashboard → Tarjeta "Administradores"** (click)
- **Sidebar → "Administradores"**
- **URL directa:** `/admin/administradores`

#### ➕ Crear Nuevo Administrador
- **Lista de Administradores → "Nuevo Administrador"**
- **Sidebar → "Registrar Usuario"** → Seleccionar rol "Administrador"

#### ⚙️ Gestionar Administradores Existentes
- **Editar:** Botón con ícono de lápiz para modificar información
- **Activar/Desactivar:** Botón en lista de administradores
- **Resetear Contraseña:** Botón "Resetear Password"
- **Eliminar:** Botón con ícono de basura (NO disponible para superadmin)
- **Ver Información:** Datos visibles en la tabla

#### 🗂️ Gestionar Doctores  
- **Ver Lista:** Dashboard → "Ver Doctores" o Sidebar → "Doctores"
- **Editar Doctor:** Botón con ícono de lápiz en lista de doctores
- **Eliminar Doctor:** Botón con ícono de basura (⚠️ elimina también expedientes)
- **Nuevo Doctor:** Botón "Nuevo Doctor"

#### 🔑 Gestión de Contraseña Propia
- **Cambio Normal:** Dashboard → "Mi Contraseña" o Sidebar → "Mi Contraseña"
- **Código de Emergencia:** Si olvida su contraseña, usar `{carnet}{usuario}`
- **Ejemplo:** Si carnet es "1234567" y usuario "admin", código: "1234567admin"

## 🔧 Validaciones Implementadas

### ✅ Formulario de Registro
- ❌ **Prefijos automáticos:** No escribir "dr." o "admin." manualmente
- ⚠️ **Advertencias:** Mensajes si se detectan prefijos
- 🧹 **Limpieza automática:** Los prefijos se eliminan automáticamente

### 🛡️ Seguridad de Administradores
- 🚫 **Superadmin protegido:** No se puede desactivar ni resetear password
- 🔐 **Solo superadmin:** Acceso exclusivo a gestión de administradores
- ✋ **Confirmaciones:** Diálogos para acciones críticas

## 📱 Navegación

### Dashboard de Administrador
```
Dashboard
├── Tarjeta "Administradores" (Solo Superadmin) 🖱️ Click → Lista
├── Botón "Administradores" (Solo Superadmin) → Lista
└── Otros botones existentes...
```

### Sidebar
```
Menú Lateral (Administradores)
├── Dashboard
├── Doctores
├── Administradores (Solo Superadmin) ⭐
├── Especialidades
├── Reportes
└── Registrar Usuario
```

## 🎨 Elementos Visuales

### Identificadores
- 🛡️ **Badge "SUPERADMIN":** Rojo para el superadministrador
- ✅ **Estado "Activo":** Verde con ícono check
- ❌ **Estado "Inactivo":** Rojo con ícono X
- 🔒 **"Protegido":** Badge gris para superadmin

### Botones de Acción
- 🟢 **"Activar":** Botón verde con ícono play
- 🟡 **"Desactivar":** Botón amarillo con ícono pause
- 🔵 **"Resetear Password":** Botón azul con ícono llave

## 📋 Información Mostrada

### Lista de Administradores
| Campo | Descripción |
|-------|-------------|
| **Nombre Completo** | Con avatar e identificador de SUPERADMIN |
| **Usuario** | Formato código (ej: admin.juan) |
| **Carnet** | Número de identificación |
| **Estado** | Activo/Inactivo con badge colorizado |
| **Fecha Registro** | Cuándo se creó la cuenta |
| **Último Acceso** | Última vez que inició sesión |
| **Acciones** | Botones para gestionar el usuario |

## 🔄 Flujo de Trabajo

### Crear Administrador
1. **Acceder** → Lista de administradores
2. **Click** → "Nuevo Administrador"
3. **Completar** → Formulario (seleccionar rol "Administrador")
4. **Usuario automático** → Se agrega prefijo "admin."
5. **Confirmar** → Usuario creado y listado

### Resetear Contraseña
1. **Localizar** → Administrador en la lista
2. **Click** → "Resetear Password"
3. **Confirmar** → Acción en diálogo
4. **Nueva contraseña** → Formato: `Admin{carnet}*`
5. **Cambio forzado** → En próximo login

### Activar/Desactivar
1. **Localizar** → Administrador en la lista
2. **Click** → "Activar" o "Desactivar"
3. **Confirmar** → Acción en diálogo
4. **Estado actualizado** → Badge cambia de color

## 🚨 Casos Especiales

### ⚠️ Limitaciones del Superadmin
- **No se puede desactivar** a sí mismo
- **No se puede resetear** su propia contraseña
- **Aparece como "Protegido"** en acciones

### 🔒 Administradores Inactivos
- **No pueden acceder** al sistema
- **Estado visible** como "Inactivo"
- **Se pueden reactivar** por el superadmin

## 🆘 Solución de Problemas

### Error: "No se encontró el rol administrador"
```bash
# Verificar roles en base de datos
python verificar_admin.py
```

### Error: "Campos faltantes en Usuario"
```bash
# Ejecutar migración
python migrate_db.py
```

### Error: "Acceso denegado"
- ✅ Verificar que sea superadministrador
- ✅ Verificar que esté autenticado
- ✅ Revisar permisos del usuario

---

## 📞 Soporte

Si encuentras problemas:
1. 📖 Revisar `ADMIN_MANAGEMENT.md` para documentación completa
2. 🔍 Ejecutar `python verificar_admin.py` para diagnóstico
3. 📋 Revisar logs de la aplicación
4. 🔄 Reiniciar servidor si es necesario

## 🆕 NUEVAS FUNCIONALIDADES IMPLEMENTADAS

### 🛠️ Edición y Eliminación de Usuarios

#### Para Superadministrador:
- ✅ **Editar cualquier usuario:** Botón de lápiz en listas de administradores y doctores
- ✅ **Eliminar usuarios:** Botón de basura (excepto superadmin)
- ✅ **Recuperación de contraseña:** Código de emergencia `{carnet}{usuario}`
- ✅ **Auto-edición:** Puede editar su propia información y contraseña

#### Para Administradores Regulares:  
- ✅ **Editar doctores:** Acceso completo a edición de doctores
- ✅ **Eliminar doctores:** Con confirmación de expedientes
- ✅ **Cambiar contraseña propia:** Funcionalidad segura
- ❌ **NO pueden editar/eliminar administradores**

### 🎯 Nuevos Botones Funcionales

#### En Lista de Administradores:
- 📝 **Editar:** Todos los administradores (ícono lápiz)
- 🗑️ **Eliminar:** Solo administradores regulares (ícono basura)
- 🛡️ **Protección:** Superadmin marcado como "Protegido"

#### En Lista de Doctores:
- 📝 **Editar:** Funcional (antes solo visual)
- 🗑️ **Eliminar:** Funcional con advertencia de expedientes

#### En Dashboard y Sidebar:
- 🔑 **"Mi Contraseña":** Acceso rápido al cambio de contraseña

### 🔐 Funcionalidad de Emergencia para Superadmin

Si el superadmin olvida su contraseña:

1. **Ir a:** Dashboard → "Mi Contraseña" → "¿Olvidó su contraseña?"
2. **Código:** `{carnet_identidad}{nombre_usuario}` (sin espacios)
3. **Ejemplo:** Carnet "1234567" + Usuario "admin" = Código "1234567admin"
4. **Importante:** Usar información exacta como aparece en el sistema

### ⚠️ Advertencias de Seguridad

- **Eliminación de doctores:** También elimina todos sus expedientes
- **Eliminación permanente:** No hay papelera de reciclaje
- **Código de emergencia:** Solo para situaciones críticas
- **Confirmaciones múltiples:** Para prevenir acciones accidentales
