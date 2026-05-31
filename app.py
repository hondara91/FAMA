from flask import Flask

from routes.main import main_bp
from utils.config import Config


def create_app():
    """Crea y configura la aplicacion Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(main_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=app.config["FLASK_HOST"],
        port=app.config["FLASK_PORT"],
        debug=app.config["FLASK_DEBUG"],
    )
