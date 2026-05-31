"""
crear_admin.py - Script de utilidad para crear el usuario administrador.

Ejecutar UNA SOLA VEZ despues de arrancar la aplicacion por primera vez:

    python crear_admin.py

El script es IDEMPOTENTE: si el email ya existe, no hace ningun cambio
y termina con un mensaje informativo. Es seguro ejecutarlo varias veces.

Credenciales por defecto (cambiar tras el primer login):
    Email:      admin@fama.es
    Contrasenia: Admin1234
"""
from datetime import datetime

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# Importar la configuracion centralizada para leer MONGO_URI y MONGO_DB_NAME
from utils.config import Config

# ── Datos del administrador por defecto ──────────────────────────────────────
# Modificar estos valores antes de ejecutar en entornos no de desarrollo
ADMIN_NOMBRE   = "Administrador FAMA"
ADMIN_EMAIL    = "admin@fama.es"
ADMIN_PASSWORD = "Admin1234"
ADMIN_PREGUNTA = "Nombre del primer buque de la Armada?"
ADMIN_RESPUESTA = "galera"  # Normalizado a minusculas al hashear


def crear_admin():
    """Crea el usuario administrador por defecto si no existe en la base de datos."""
    # Conexion directa a MongoDB sin contexto Flask (script de utilidad)
    cliente = MongoClient(Config.MONGO_URI)
    db      = cliente[Config.MONGO_DB_NAME]

    # Verificar si ya existe un admin con este email antes de insertar
    if db.usuarios.find_one({"email": ADMIN_EMAIL}):
        print(f"[INFO] El administrador '{ADMIN_EMAIL}' ya existe. No se realizo ningun cambio.")
        cliente.close()
        return

    # Construir el documento del administrador con los mismos campos que crea Usuario.crear()
    admin = {
        "nombre": ADMIN_NOMBRE,
        "email":  ADMIN_EMAIL,
        # Hashear la contrasenia; nunca almacenar en texto plano
        "password": generate_password_hash(ADMIN_PASSWORD),
        "rol": "admin",
        "pregunta_seguridad": ADMIN_PREGUNTA,
        # Normalizar la respuesta a minusculas igual que hace Usuario.crear()
        "respuesta_seguridad": generate_password_hash(ADMIN_RESPUESTA.lower()),
        # No forzar cambio de contrasenia en el primer login del admin
        "debe_cambiar_password": False,
        "activo": True,
        "fecha_registro": datetime.now(),
    }

    db.usuarios.insert_one(admin)

    # Mostrar las credenciales en consola para que el operador las tenga a mano
    print("=" * 50)
    print("Usuario administrador creado correctamente.")
    print(f"   Email:       {ADMIN_EMAIL}")
    print(f"   Contrasenia: {ADMIN_PASSWORD}")
    print("   Cambia la contrasenia tras el primer login.")
    print("=" * 50)

    cliente.close()  # Cerrar la conexion al terminar el script


if __name__ == "__main__":
    crear_admin()
