"""
app.py - Punto de entrada de la aplicacion FAMA.

Crea la aplicacion Flask mediante el patron factoria (create_app),
registra todos los blueprints de cada modulo y configura el
contexto global de plantillas.
"""
from datetime import datetime

from flask import Flask

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

    # ── Variables globales de plantillas ─────────────────────────────────────
    # Inyecta 'now' y 'hay_novedades' en TODAS las plantillas Jinja2.
    # 'hay_novedades' controla si el boton NOVEDADES se ilumina en amarillo.
    @app.context_processor
    def inyectar_contexto():
        from utils.db import get_db
        from flask import session as current_session

        hay_novedades = False
        try:
            db = get_db()
            ultima_visita = current_session.get("novedades_vistas_hasta")
            if ultima_visita:
                # Comparar fecha de la novedad mas reciente con la ultima visita del usuario
                desde = datetime.fromisoformat(ultima_visita)
                hay_novedades = db.novedades.count_documents(
                    {"fecha_creacion": {"$gt": desde}}
                ) > 0
            else:
                # Primera visita o sesion nueva: amarillo si existe al menos una novedad
                hay_novedades = db.novedades.count_documents({}) > 0
        except Exception:
            pass  # Si MongoDB no esta disponible, el boton permanece sin color especial

        return {"now": datetime.now(), "hay_novedades": hay_novedades}

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
