"""
Script de migración para agregar tablas de seguridad
Agrega las tablas LoginAttempt y AccountLock para protección contra fuerza bruta
"""

def add_security_tables():
    """Agrega las tablas de seguridad a la base de datos"""
    
    # SQL para crear tabla de intentos de login
    login_attempts_sql = """
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ip_address VARCHAR(45) NOT NULL,
        username VARCHAR(80),
        timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        success BOOLEAN NOT NULL DEFAULT FALSE,
        user_agent VARCHAR(500),
        INDEX idx_ip_timestamp (ip_address, timestamp),
        INDEX idx_username_timestamp (username, timestamp),
        INDEX idx_timestamp (timestamp)
    );
    """
    
    # SQL para crear tabla de bloqueos de cuenta
    account_locks_sql = """
    CREATE TABLE IF NOT EXISTS account_locks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80) NOT NULL,
        ip_address VARCHAR(45) NOT NULL,
        locked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        unlock_at DATETIME NOT NULL,
        reason VARCHAR(255) DEFAULT 'Multiple failed login attempts',
        INDEX idx_username_unlock (username, unlock_at),
        INDEX idx_ip_unlock (ip_address, unlock_at),
        INDEX idx_unlock_at (unlock_at)
    );
    """
    
    return [login_attempts_sql, account_locks_sql]

if __name__ == "__main__":
    print("Generando SQL para tablas de seguridad...")
    sql_commands = add_security_tables()
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"\n-- Comando {i}:")
        print(sql)
    
    print("\n✅ Scripts de migración generados.")
    print("💡 Ejecuta estos comandos en tu base de datos para agregar las protecciones de seguridad.")
