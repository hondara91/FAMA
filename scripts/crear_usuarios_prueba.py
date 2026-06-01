"""
scripts/crear_usuarios_prueba.py
Crea 10 usuarios de prueba validados con avatar de color generado sin Pillow.
Ejecutar desde la raiz del proyecto: python scripts/crear_usuarios_prueba.py
"""
import struct
import zlib
import os
from datetime import datetime

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from utils.config import Config

# ── Datos de los 10 usuarios ──────────────────────────────────────────────────

USUARIOS = [
    ("marisol", "marisol_74@hotmail.com",       (231, 76,  60)),   # rojo
    ("carlota", "carlota.ramos@gmail.com",       ( 52,152,219)),   # azul
    ("roberto", "r.garcia89@yahoo.es",           ( 46,204,113)),   # verde
    ("antonio", "antonio_m@outlook.com",         (155, 89,182)),   # morado
    ("beatriz", "bea.torrent@hotmail.es",        (243,156, 18)),   # naranja
    ("carmelo", "c.morales@gmail.com",           ( 26,188,156)),   # verde-azul
    ("dolores", "lola.d@yahoo.com",              (233, 30, 99)),   # rosa
    ("ernesto", "ernesto.v87@outlook.es",        ( 52, 73, 94)),   # azul oscuro
    ("gabriel", "gabriel_rn@hotmail.com",        ( 39,174, 96)),   # verde oscuro
    ("nicolas", "nico.sanchez@gmail.com",        (230,126, 34)),   # naranja oscuro
]

PASSWORD = "Fama1234"   # contrasenia comun para todos los usuarios de prueba


# ── Generador de PNG solido sin dependencias externas ────────────────────────

def _chunk(name: bytes, data: bytes) -> bytes:
    c = name + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def crear_png(r: int, g: int, b: int, size: int = 80) -> bytes:
    """Devuelve los bytes de un PNG cuadrado de color solido."""
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    fila = bytes([0]) + bytes([r, g, b] * size)   # filtro None + pixeles RGB
    idat = zlib.compress(fila * size)

    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


# ── Script principal ──────────────────────────────────────────────────────────

def main():
    cliente = MongoClient(Config.MONGO_URI)
    db      = cliente[Config.MONGO_DB_NAME]
    col     = db.usuarios

    carpeta_perfiles = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "static", "uploads", "perfiles"
    )
    os.makedirs(carpeta_perfiles, exist_ok=True)

    creados = 0
    for nombre, email, (r, g, b) in USUARIOS:
        if col.find_one({"email": email}):
            print(f"  [SKIP] {nombre} ya existe ({email})")
            continue

        # Guardar avatar PNG en disco
        nombre_foto = f"avatar_{nombre}.png"
        ruta_foto   = os.path.join(carpeta_perfiles, nombre_foto)
        with open(ruta_foto, "wb") as f:
            f.write(crear_png(r, g, b))

        col.insert_one({
            "nombre":              nombre,
            "email":               email,
            "password":            generate_password_hash(PASSWORD),
            "rol":                 "usuario",
            "foto_perfil":         nombre_foto,
            "pregunta_seguridad":  None,
            "respuesta_seguridad": None,
            "debe_cambiar_password": False,
            "activo":              True,
            "validado":            True,
            "email_verificado":    True,
            "fecha_registro":      datetime.now(),
        })
        print(f"  [OK]   {nombre} | {email}")
        creados += 1

    cliente.close()
    print(f"\n{creados} usuario(s) creado(s). Contrasenia: {PASSWORD}")


if __name__ == "__main__":
    main()
