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

    # ── Variables globales de plantillas ─────────────────────────────────────
    # Inyecta 'now' en TODAS las plantillas Jinja2 sin pasarla manualmente.
    # Se usa principalmente en el footer para mostrar el ano actual.
    @app.context_processor
    def inyectar_contexto():
        return {"now": datetime.now()}

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
