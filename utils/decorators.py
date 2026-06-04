"""
utils/decorators.py - Decoradores de control de acceso para las rutas de FAMA.

Jerarquia de roles: admin > gestor > usuario

Orden de apilado recomendado sobre las rutas:
    @login_required    <- primero: sin sesión no tiene sentido comprobar el rol
    @admin_required    <- segundo: comprueba el rol una vez confirmada la sesión
"""
from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(f):
    """Redirige al login si el usuario no ha iniciado sesión."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Permite el acceso solo a usuarios con rol 'admin'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("rol") != "admin":
            flash("Acceso restringido a administradores.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


def gestor_required(f):
    """Permite el acceso a usuarios con rol 'gestor' o 'admin'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("rol") not in ("admin", "gestor"):
            flash("Acceso restringido a gestores y administradores.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated
