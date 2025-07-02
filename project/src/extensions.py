from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect  # 🔒 TC31: CSRF Protection

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()  # 🔒 TC31: Instancia de protección CSRF
limiter = Limiter(
    app=None,
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour", "30 per minute"],  # Ajustado para demo/presentación
    storage_uri="memory://"  # Usaremos memoria por simplicidad, en producción usar Redis
)
