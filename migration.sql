-- Script SQL para agregar nuevas columnas al modelo Usuario
-- Ejecutar este script directamente en la base de datos MySQL

-- Agregar columna 'estado' si no existe
SET @sql = (
    SELECT IF(
        (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
         WHERE TABLE_NAME = 'usuarios' 
         AND COLUMN_NAME = 'estado' 
         AND TABLE_SCHEMA = DATABASE()) = 0,
        'ALTER TABLE usuarios ADD COLUMN estado BOOLEAN NOT NULL DEFAULT TRUE',
        'SELECT "Columna estado ya existe" as mensaje'
    )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar columna 'fecha_creacion' si no existe
SET @sql = (
    SELECT IF(
        (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
         WHERE TABLE_NAME = 'usuarios' 
         AND COLUMN_NAME = 'fecha_creacion' 
         AND TABLE_SCHEMA = DATABASE()) = 0,
        'ALTER TABLE usuarios ADD COLUMN fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP',
        'SELECT "Columna fecha_creacion ya existe" as mensaje'
    )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar columna 'ultimo_acceso' si no existe
SET @sql = (
    SELECT IF(
        (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
         WHERE TABLE_NAME = 'usuarios' 
         AND COLUMN_NAME = 'ultimo_acceso' 
         AND TABLE_SCHEMA = DATABASE()) = 0,
        'ALTER TABLE usuarios ADD COLUMN ultimo_acceso DATETIME NULL',
        'SELECT "Columna ultimo_acceso ya existe" as mensaje'
    )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar columna 'cambiar_contrasena' si no existe
SET @sql = (
    SELECT IF(
        (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
         WHERE TABLE_NAME = 'usuarios' 
         AND COLUMN_NAME = 'cambiar_contrasena' 
         AND TABLE_SCHEMA = DATABASE()) = 0,
        'ALTER TABLE usuarios ADD COLUMN cambiar_contrasena BOOLEAN NOT NULL DEFAULT FALSE',
        'SELECT "Columna cambiar_contrasena ya existe" as mensaje'
    )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Actualizar registros existentes con valores por defecto si es necesario
UPDATE usuarios 
SET estado = TRUE 
WHERE estado IS NULL;

UPDATE usuarios 
SET fecha_creacion = NOW() 
WHERE fecha_creacion IS NULL;

UPDATE usuarios 
SET cambiar_contrasena = FALSE 
WHERE cambiar_contrasena IS NULL;

-- Verificar la estructura final
SELECT 'Migración completada. Estructura actual de la tabla usuarios:' as mensaje;
DESCRIBE usuarios;
