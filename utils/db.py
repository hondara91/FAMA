from flask import current_app
from pymongo import MongoClient
from pymongo.errors import PyMongoError

_client = None


def get_mongo_client():
    """Devuelve un cliente MongoDB reutilizable para la aplicacion."""
    global _client

    if _client is None:
        _client = MongoClient(
            current_app.config["MONGO_URI"],
            serverSelectionTimeoutMS=3000,
        )

    return _client


def get_database():
    """Obtiene la base de datos configurada para Proyecto FAMA."""
    return get_mongo_client()[current_app.config["MONGO_DB_NAME"]]


def check_mongo_connection():
    """Comprueba la conexion con MongoDB mediante un ping."""
    try:
        get_mongo_client().admin.command("ping")
        return True, "Conexion con MongoDB activa"
    except PyMongoError as error:
        return False, f"No se pudo conectar con MongoDB: {error}"
