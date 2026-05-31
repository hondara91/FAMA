"""
utils/db.py - Gestion de la conexion con MongoDB.

Implementa el patron singleton con inicializacion lazy (perezosa):
el cliente se crea la primera vez que se necesita y se reutiliza
en las siguientes llamadas, evitando abrir una conexion nueva por peticion.
"""
from flask import current_app
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Variable de modulo que guarda el cliente MongoDB entre peticiones.
# None indica que aun no se ha creado (lazy init).
_client = None


def get_mongo_client():
    """
    Devuelve el cliente MongoDB, creandolo si todavia no existe.

    Usa current_app para leer la URI de configuracion, por lo que
    debe llamarse siempre dentro de un contexto de aplicacion Flask.
    """
    global _client

    # Solo crear el cliente si aun no se ha inicializado (singleton)
    if _client is None:
        # serverSelectionTimeoutMS: si MongoDB no responde en 3 s, lanza
        # PyMongoError en lugar de bloquear la aplicacion indefinidamente
        _client = MongoClient(
            current_app.config["MONGO_URI"],
            serverSelectionTimeoutMS=3000,
        )

    return _client


def get_database():
    """Devuelve el objeto de base de datos configurado en MONGO_DB_NAME."""
    return get_mongo_client()[current_app.config["MONGO_DB_NAME"]]


# Alias corto para uso en rutas y modelos: from utils.db import get_db
get_db = get_database


def check_mongo_connection():
    """
    Comprueba la conexion con MongoDB enviando un ping al servidor.

    Devuelve una tupla (ok: bool, mensaje: str) que se muestra
    en la pagina de inicio para informar del estado del sistema.
    """
    try:
        # El comando 'ping' es el metodo oficial de MongoDB para verificar conectividad
        get_mongo_client().admin.command("ping")
        return True, "Conexion con MongoDB activa"
    except PyMongoError as error:
        # Captura cualquier error de red o autenticacion de PyMongo
        return False, f"No se pudo conectar con MongoDB: {error}"
