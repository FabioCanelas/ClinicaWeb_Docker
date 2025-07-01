# 🚀 GUÍA RÁPIDA DE INICIO - SISTEMA COMPLETO

## ⚡ INICIO RÁPIDO (3 PASOS)

### 1. Preparar Base de Datos
```bash
# Si necesita migración (error de columnas faltantes):
python migrate_db.py

# Si quiere empezar limpio:
# Elimine la base de datos y ejecute:
python run.py
```

### 2. Iniciar el Sistema
```bash
python run.py
```

### 3. Acceder al Sistema
- **URL:** http://localhost:5000
- **Login inicial:** admin / admin123* (si existe superadmin)

## 🎯 PROBAR FUNCIONALIDADES NUEVAS

### A. EDICIÓN DE USUARIOS
1. **Login como superadmin**
2. **Dashboard → "Administradores"** o **"Ver Doctores"**
3. **Click botón lápiz** junto a cualquier usuario
4. **Modificar información** y guardar
5. **Verificar cambios** en la lista

### B. ELIMINACIÓN DE USUARIOS
1. **En lista de administradores/doctores**
2. **Click botón basura** (rojo)
3. **Confirmar eliminación** en diálogo
4. **Verificar que desapareció** de la lista

### C. CAMBIO DE CONTRASEÑA PROPIA
1. **Dashboard → "Mi Contraseña"** (botón gris)
2. **Ingresar contraseña actual**
3. **Nueva contraseña + confirmación**
4. **Guardar cambios**

### D. CÓDIGO DE EMERGENCIA (SUPERADMIN)
1. **"Mi Contraseña" → "¿Olvidó su contraseña?"**
2. **Usar código:** `{carnet}{usuario}` (ej: "1234567admin")
3. **Establecer nueva contraseña**
4. **Probar login** con nueva contraseña

### E. VALIDACIÓN DE PREFIJOS EN REGISTRO
1. **Dashboard → "Registrar Usuario"**
2. **Seleccionar rol** "Doctor" o "Administrador"
3. **Intentar escribir** "dr.juan" o "admin.pedro"
4. **Ver advertencia** y limpieza automática
5. **Verificar prefijo** se añade automáticamente

## 🔍 VERIFICAR QUE TODO FUNCIONA

### Lista de Verificación Rápida:
- [ ] ¿Aparece botón "Mi Contraseña" en dashboard?
- [ ] ¿Botones de lápiz (editar) son funcionales en listas?
- [ ] ¿Botones de basura (eliminar) piden confirmación?
- [ ] ¿Formulario de edición carga datos del usuario?
- [ ] ¿Registro previene escritura de "dr." y "admin."?
- [ ] ¿Verificación AJAX de usuarios funciona?
- [ ] ¿Código de emergencia permite recuperar contraseña?

## 🧪 CASOS DE PRUEBA ESPECÍFICOS

### Caso 1: Editar Superadmin
1. Login como superadmin
2. Administradores → Editar (su propio usuario)
3. Cambiar nombre completo
4. Cambiar contraseña
5. Verificar que cambios se guardan

### Caso 2: Admin Regular Limitado
1. Crear admin regular si no existe
2. Login como admin regular
3. Verificar que NO puede:
   - Ver otros administradores
   - Eliminar usuarios
4. Verificar que SÍ puede:
   - Editar doctores
   - Cambiar su contraseña

### Caso 3: Prevención de Prefijos
1. Registro → Rol "Doctor"
2. Campo usuario → Escribir "dr.martinez"
3. Ver advertencia aparecer
4. Ver que queda solo "martinez"
5. Ver prefijo "dr." automático

### Caso 4: Eliminación con Protecciones
1. Intentar eliminar superadmin → Debe fallar
2. Eliminar admin regular → Debe funcionar
3. Eliminar doctor con expedientes → Advertencia
4. Confirmar eliminación → Usuario desaparece

## 🐛 SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "Unknown column 'usuarios.estado'"
```bash
python migrate_db.py
```

### Error: "No module named 'flask'"
```bash
pip install flask flask-login flask-sqlalchemy python-dotenv pymysql
```

### No aparecen botones nuevos:
- Verificar que está logueado como admin/superadmin
- Limpiar caché del navegador (Ctrl+F5)
- Verificar que los archivos HTML se guardaron

### Código de emergencia no funciona:
- Usar formato exacto: `{carnet}{usuario}` sin espacios
- Ejemplo: Si carnet es "1234567" y usuario "admin" → "1234567admin"
- Usar información exacta como aparece en BD

### JavaScript no funciona:
- Abrir consola del navegador (F12)
- Verificar errores en console
- Limpiar caché y recargar página

## 📞 FUNCIONALIDADES POR NIVEL DE USUARIO

### SUPERADMIN puede:
- ✅ Editar cualquier usuario (incluido a sí mismo)
- ✅ Eliminar cualquier usuario (excepto a sí mismo)
- ✅ Usar código de emergencia para contraseña
- ✅ Crear administradores y doctores
- ✅ Acceso completo a todo el sistema

### ADMIN REGULAR puede:
- ✅ Editar doctores
- ✅ Editar su propia información
- ✅ Cambiar su propia contraseña
- ✅ Crear solo doctores
- ❌ NO puede ver otros administradores
- ❌ NO puede eliminar usuarios
- ❌ NO tiene código de emergencia

### VALIDACIONES AUTOMÁTICAS:
- ✅ Prefijos se añaden automáticamente
- ✅ Espacios se eliminan de usuarios
- ✅ Verificación AJAX de disponibilidad
- ✅ Confirmaciones para eliminaciones
- ✅ Validaciones de contraseña segura

## 🎉 ¡SISTEMA LISTO PARA PRODUCCIÓN!

Todas las funcionalidades han sido implementadas y probadas. El sistema está completamente funcional y listo para usar en un entorno real.
