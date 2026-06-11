"""
migrar_emails_mde.py - Actualiza los emails de todos los usuarios para que
terminen en @mde.es, conservando la parte local (antes de la @).

Ejecutar una sola vez:
    python scripts/migrar_emails_mde.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient

from utils.config import Config


def migrar():
    cliente = MongoClient(Config.MONGO_URI)
    db = cliente[Config.MONGO_DB_NAME]

    usuarios = list(db.usuarios.find({}, {"_id": 1, "nombre": 1, "email": 1}))
    actualizados = 0
    omitidos = 0

    for u in usuarios:
        email_actual = u.get("email", "")
        if email_actual.endswith("@mde.es"):
            omitidos += 1
            continue

        local = email_actual.split("@")[0] if "@" in email_actual else email_actual
        email_nuevo = f"{local}@mde.es"

        db.usuarios.update_one({"_id": u["_id"]}, {"$set": {"email": email_nuevo}})
        print(f"  {u['nombre']}: {email_actual} -> {email_nuevo}")
        actualizados += 1

    print(f"\nResultado: {actualizados} actualizados, {omitidos} ya tenían @mde.es.")
    cliente.close()


if __name__ == "__main__":
    migrar()
