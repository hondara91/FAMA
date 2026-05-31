import os


class Config:
    """Configuracion centralizada mediante variables de entorno."""

    SECRET_KEY = os.getenv("SECRET_KEY", "fama-dev-secret")
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "fama_db")
