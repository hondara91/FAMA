"""
app.py - Punto de entrada de la aplicacion FAMA.

Crea la aplicacion Flask mediante el patron factoria (create_app),
registra todos los blueprints de cada modulo y configura el
contexto global de plantillas.
"""
import time
from datetime import datetime

from flask import Flask, redirect, session, url_for

# Timestamp (epoch) de la última limpieza de anuncios expirados.
# Uso de lista mutable para que la closure del before_request pueda mutarlo.
_ts_limpieza = [0.0]


def _limpiar_expirados(db, static_folder):
    """Elimina anuncios cuya fecha_expiracion ya ha pasado, incluyendo sus fotos."""
    from utils.uploads import eliminar_imagenes
    ahora = datetime.now()
    modulos = [
        (db.viviendas,    "viviendas"),
        (db.servicios,    "servicios"),
        (db.compraventa,  "compraventa"),
    ]
    for coleccion, subcarpeta in modulos:
        expirados = list(coleccion.find({
            "fecha_expiracion": {"$exists": True, "$ne": None, "$lte": ahora},
        }))
        for doc in expirados:
            try:
                eliminar_imagenes(doc.get("fotos", []), subcarpeta)
                coleccion.delete_one({"_id": doc["_id"]})
            except Exception:
                pass

# Clase de configuracion que lee variables de entorno
from utils.config import Config

# Blueprint de cada modulo funcional de la aplicacion
from routes.main import main_bp           # Pagina principal y dashboard
from routes.auth import auth_bp           # Registro, login, logout y contrasenas
from routes.viviendas import viviendas_bp # Anuncios de alquiler e intercambio
from routes.servicios import servicios_bp # Servicios entre personal militar
from routes.compraventa import compraventa_bp  # Segunda mano y tienda Armada
from routes.ocio import ocio_bp           # Eventos de ocio y calendario
from routes.admin import admin_bp         # Panel de gestion y logs
from routes.foro import foro_bp               # Foro de publicaciones y respuestas
from routes.novedades import novedades_bp     # Novedades y anuncios del admin


def create_app():
    """
    Factoria de la aplicacion Flask.

    Centraliza la creacion de la app para facilitar pruebas unitarias
    e integracion con servidores WSGI como gunicorn.
    """
    app = Flask(__name__)

    # Cargar toda la configuracion desde utils/config.py (variables de entorno)
    app.config.from_object(Config)

    # ── Registro de blueprints ────────────────────────────────────────────────
    # Cada blueprint tiene su propio prefijo de URL definido en su archivo.
    # El orden no afecta el funcionamiento, pero se mantiene logico:
    # primero los modulos publicos, luego los de autenticacion y admin.
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(viviendas_bp)
    app.register_blueprint(servicios_bp)
    app.register_blueprint(compraventa_bp)
    app.register_blueprint(ocio_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(foro_bp)
    app.register_blueprint(novedades_bp)

    # ── Verificación de sesión activa ────────────────────────────────────────
    # Las páginas públicas (listados, detalles, foro, etc.) son accesibles sin
    # login. Las rutas interactivas llevan @login_required individualmente.
    # Aquí solo verificamos que los usuarios ya autenticados siguen activos.
    @app.before_request
    def verificar_sesion():
        from bson import ObjectId
        from flask import request, flash
        if request.endpoint and (
            request.endpoint.startswith("auth.")
            or request.endpoint == "static"
        ):
            return None

        # Sin sesión: dejar pasar; @login_required en cada ruta protegida
        # redirigirá al login si hace falta.
        if not session.get("user_id"):
            return None

        from utils.db import get_db
        db = get_db()

        # Limpiar anuncios expirados como máximo una vez por hora.
        ahora_ts = time.time()
        if ahora_ts - _ts_limpieza[0] > 3600:
            _ts_limpieza[0] = ahora_ts
            try:
                _limpiar_expirados(db, app.static_folder)
            except Exception:
                pass
        usuario = db.usuarios.find_one(
            {"_id": ObjectId(session["user_id"])},
            {"activo": 1, "validado": 1},
        )
        if not usuario or not usuario.get("activo"):
            session.clear()
            flash("Tu sesión ha sido cerrada porque tu cuenta ha sido desactivada.", "danger")
            return redirect(url_for("auth.login"))
        if not usuario.get("validado"):
            session.clear()
            flash("Tu sesión ha sido cerrada porque tu cuenta ya no está validada.", "danger")
            return redirect(url_for("auth.login"))

    # ── Variables globales de plantillas ─────────────────────────────────────
    # Inyecta 'now' y 'hay_novedades' en TODAS las plantillas Jinja2.
    # 'hay_novedades' controla si el boton NOVEDADES se ilumina en amarillo.
    @app.context_processor
    def inyectar_contexto():
        from utils.db import get_db
        from flask import session as current_session

        hay_novedades       = False
        alertas_admin_total = 0
        alertas_admin       = {}

        try:
            db = get_db()

            # Badge de novedades no vistas
            ultima_visita = current_session.get("novedades_vistas_hasta")
            if ultima_visita:
                desde = datetime.fromisoformat(ultima_visita)
                hay_novedades = db.novedades.count_documents(
                    {"fecha_creacion": {"$gt": desde}}
                ) > 0
            else:
                hay_novedades = db.novedades.count_documents({}) > 0

            # Alertas para admin/gestor en el navbar
            rol = current_session.get("rol_real") or current_session.get("rol")
            if rol in ("admin", "gestor"):
                pendientes = db.usuarios.count_documents(
                    {"activo": True, "validado": False}
                )
                reportes = db.reportes.count_documents({"resuelto": False})
                alertas_admin = {
                    "pendientes": pendientes,
                    "reportes":   reportes,
                }
                alertas_admin_total = pendientes + reportes
        except Exception:
            pass

        return {
            "now":                datetime.now(),
            "hay_novedades":      hay_novedades,
            "alertas_admin":      alertas_admin,
            "alertas_admin_total": alertas_admin_total,
        }

    return app


# ── Instancia global de la aplicacion ────────────────────────────────────────
# Se crea aqui (y no solo en __main__) para que gunicorn pueda importarla
# directamente con: gunicorn "app:app"
app = create_app()


if __name__ == "__main__":
    # Arranque en desarrollo local; en produccion usar gunicorn
    app.run(
        host=app.config["FLASK_HOST"],
        port=app.config["FLASK_PORT"],
        debug=app.config["FLASK_DEBUG"],
    )
