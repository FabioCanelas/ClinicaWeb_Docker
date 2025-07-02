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

-- =====================================
-- TABLAS DE SEGURIDAD - PROTECCIÓN CONTRA FUERZA BRUTA
-- =====================================

-- Crear tabla login_attempts para trackear intentos de login
CREATE TABLE IF NOT EXISTS login_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL COMMENT 'IPv4 o IPv6 del cliente',
    username VARCHAR(80) COMMENT 'Usuario que intentó login (puede ser NULL)',
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento del intento',
    success BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Si el intento fue exitoso',
    user_agent VARCHAR(500) COMMENT 'User-Agent del navegador',
    
    -- Índices para optimizar consultas de seguridad
    INDEX idx_ip_timestamp (ip_address, timestamp),
    INDEX idx_username_timestamp (username, timestamp),
    INDEX idx_timestamp (timestamp),
    INDEX idx_success_timestamp (success, timestamp)
) COMMENT 'Registro de intentos de login para detección de ataques';

-- Crear tabla account_locks para bloqueos temporales
CREATE TABLE IF NOT EXISTS account_locks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL COMMENT 'Usuario bloqueado (* para bloqueo por IP)',
    ip_address VARCHAR(45) NOT NULL COMMENT 'IP bloqueada',
    locked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento del bloqueo',
    unlock_at DATETIME NOT NULL COMMENT 'Momento en que expira el bloqueo',
    reason VARCHAR(255) DEFAULT 'Multiple failed login attempts' COMMENT 'Razón del bloqueo',
    
    -- Índices para verificación rápida de bloqueos
    INDEX idx_username_unlock (username, unlock_at),
    INDEX idx_ip_unlock (ip_address, unlock_at),
    INDEX idx_unlock_at (unlock_at)
) COMMENT 'Bloqueos temporales de cuentas e IPs';

-- Verificar que las tablas de seguridad se crearon correctamente
SELECT 'Tablas de seguridad creadas:' as mensaje;
SHOW TABLES LIKE '%attempt%';
SHOW TABLES LIKE '%lock%';

SELECT '✅ MIGRACIÓN DE SEGURIDAD COMPLETADA - Sistema protegido contra fuerza bruta' as status;
