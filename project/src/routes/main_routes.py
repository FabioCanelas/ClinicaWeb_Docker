"""
Rutas principales del sistema
Maneja la página de inicio y redirecciones generales
"""

from flask import Blueprint, redirect, url_for
from flask_login import current_user

# Blueprint para rutas principales
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Página de inicio del sistema
    Redirige automáticamente según el estado de autenticación del usuario
    """
    if current_user.is_authenticated:
        # Usuario autenticado: redirigir al dashboard correspondiente
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('doctor.dashboard'))
    else:
        # Usuario no autenticado: mostrar página de login
        return redirect(url_for('auth.login'))