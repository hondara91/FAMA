"""
resetear_passwords.py - Pone la contraseña de todos los usuarios a 'fama1234'.

Util para entornos de desarrollo y pruebas. No ejecutar en produccion.

    python scripts/resetear_passwords.py

El admin (admin@fama.es) queda excluido para no perder el acceso principal.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from utils.config import Config

PASSWORD = "fama1234"


def resetear_passwords():
    cliente = MongoClient(Config.MONGO_URI)
    db = cliente[Config.MONGO_DB_NAME]

    resultado = db.usuarios.update_many(
        {"email": {"$ne": "admin@appfama.es"}},
        {"$set": {
            "password": generate_password_hash(PASSWORD),
            "debe_cambiar_password": True,
            "email_verificado": True,
        }},
    )

    print(f"[OK] {resultado.modified_count} usuario(s) actualizados a contraseña '{PASSWORD}'.")
    print("     Todos deberán cambiarla en su próximo inicio de sesión.")
    cliente.close()


if __name__ == "__main__":
    resetear_passwords()
