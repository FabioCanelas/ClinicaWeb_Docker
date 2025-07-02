"""
Módulo de seguridad para protección contra ataques de fuerza bruta
Maneja rate limiting, bloqueos temporales y logging de seguridad
"""

from datetime import datetime, timedelta
from flask import request, session
from ..models.models import LoginAttempt, AccountLock, Usuario
from ..extensions import db
import logging

# Configurar logging de seguridad
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)

# Configuración de seguridad
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 1  # Ajustado a 1 minuto para demo/presentación
RATE_LIMIT_WINDOW_MINUTES = 15

class SecurityManager:
    """Gestiona la seguridad y protección contra ataques de fuerza bruta"""
    
    @staticmethod
    def get_client_ip():
        """Obtiene la IP real del cliente considerando proxies"""
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        elif request.environ.get('HTTP_X_REAL_IP'):
            return request.environ['HTTP_X_REAL_IP']
        else:
            return request.environ.get('REMOTE_ADDR', 'unknown')
    
    @staticmethod
    def get_user_agent():
        """Obtiene el User-Agent del cliente"""
        return request.headers.get('User-Agent', 'unknown')[:500]
    
    @staticmethod
    def is_account_locked(username, ip_address):
        """Verifica si una cuenta/IP está bloqueada"""
        current_time = datetime.utcnow()
        
        # Verificar bloqueo por username
        username_lock = AccountLock.query.filter_by(
            username=username
        ).filter(
            AccountLock.unlock_at > current_time
        ).first()
        
        # Verificar bloqueo por IP
        ip_lock = AccountLock.query.filter_by(
            ip_address=ip_address
        ).filter(
            AccountLock.unlock_at > current_time
        ).first()
        
        if username_lock:
            return True, f"Cuenta bloqueada hasta {username_lock.unlock_at.strftime('%H:%M:%S')}"
        
        if ip_lock:
            return True, f"IP bloqueada hasta {ip_lock.unlock_at.strftime('%H:%M:%S')}"
        
        return False, None
    
    @staticmethod
    def get_failed_attempts_count(username, ip_address, window_minutes=RATE_LIMIT_WINDOW_MINUTES):
        """Cuenta los intentos fallidos recientes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        # Contar intentos fallidos por username
        username_attempts = LoginAttempt.query.filter_by(
            username=username,
            success=False
        ).filter(
            LoginAttempt.timestamp > cutoff_time
        ).count()
        
        # Contar intentos fallidos por IP
        ip_attempts = LoginAttempt.query.filter_by(
            ip_address=ip_address,
            success=False
        ).filter(
            LoginAttempt.timestamp > cutoff_time
        ).count()
        
        return max(username_attempts, ip_attempts)
    
    @staticmethod
    def log_login_attempt(username, success=False):
        """Registra un intento de login"""
        ip_address = SecurityManager.get_client_ip()
        user_agent = SecurityManager.get_user_agent()
        
        # Crear registro del intento
        attempt = LoginAttempt(
            ip_address=ip_address,
            username=username,
            success=success,
            user_agent=user_agent
        )
        
        db.session.add(attempt)
        
        # Log de seguridad
        if success:
            security_logger.info(f"Successful login: {username} from {ip_address}")
        else:
            security_logger.warning(f"Failed login attempt: {username} from {ip_address}")
        
        # Si el intento falló, verificar si necesitamos bloquear
        if not success:
            failed_count = SecurityManager.get_failed_attempts_count(username, ip_address)
            
            if failed_count >= MAX_LOGIN_ATTEMPTS - 1:  # -1 porque este intento aún no se ha committeado
                SecurityManager.create_account_lock(username, ip_address)
                security_logger.critical(f"ACCOUNT LOCKED: {username} from {ip_address} after {MAX_LOGIN_ATTEMPTS} failed attempts")
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            security_logger.error(f"Error logging login attempt: {str(e)}")
    
    @staticmethod
    def create_account_lock(username, ip_address):
        """Crea un bloqueo temporal de cuenta"""
        unlock_time = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        
        # Bloquear por username
        username_lock = AccountLock(
            username=username,
            ip_address=ip_address,
            unlock_at=unlock_time,
            reason=f"Multiple failed login attempts ({MAX_LOGIN_ATTEMPTS})"
        )
        
        # Bloquear por IP (para prevenir ataques a múltiples cuentas)
        ip_lock = AccountLock(
            username="*",  # Wildcard para indicar bloqueo por IP
            ip_address=ip_address,
            unlock_at=unlock_time,
            reason=f"Multiple failed login attempts from IP"
        )
        
        db.session.add(username_lock)
        db.session.add(ip_lock)
    
    @staticmethod
    def cleanup_old_records():
        """Limpia registros antiguos de intentos y bloqueos"""
        # Limpiar intentos de más de 7 días
        cutoff_attempts = datetime.utcnow() - timedelta(days=7)
        LoginAttempt.query.filter(LoginAttempt.timestamp < cutoff_attempts).delete()
        
        # Limpiar bloqueos expirados
        AccountLock.query.filter(AccountLock.unlock_at < datetime.utcnow()).delete()
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            security_logger.error(f"Error cleaning up old security records: {str(e)}")
    
    @staticmethod
    def is_suspicious_activity(username, ip_address):
        """Detecta actividad sospechosa"""
        # Verificar si hay demasiados intentos en un período corto
        recent_attempts = SecurityManager.get_failed_attempts_count(username, ip_address, window_minutes=5)
        
        if recent_attempts >= 3:
            return True, "Demasiados intentos en poco tiempo"
        
        # Verificar si la IP ha intentado múltiples cuentas
        cutoff_time = datetime.utcnow() - timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)
        unique_usernames = db.session.query(LoginAttempt.username).filter_by(
            ip_address=ip_address,
            success=False
        ).filter(
            LoginAttempt.timestamp > cutoff_time
        ).distinct().count()
        
        if unique_usernames > 3:
            return True, "Múltiples cuentas atacadas desde esta IP"
        
        return False, None
    
    @staticmethod
    def get_security_status(username):
        """Obtiene el estado de seguridad de una cuenta"""
        ip_address = SecurityManager.get_client_ip()
        
        # Verificar bloqueos
        is_locked, lock_message = SecurityManager.is_account_locked(username, ip_address)
        
        # Obtener intentos recientes
        failed_attempts = SecurityManager.get_failed_attempts_count(username, ip_address)
        
        # Verificar actividad sospechosa
        is_suspicious, suspicious_reason = SecurityManager.is_suspicious_activity(username, ip_address)
        
        return {
            'is_locked': is_locked,
            'lock_message': lock_message,
            'failed_attempts': failed_attempts,
            'remaining_attempts': MAX_LOGIN_ATTEMPTS - failed_attempts,
            'is_suspicious': is_suspicious,
            'suspicious_reason': suspicious_reason
        }
