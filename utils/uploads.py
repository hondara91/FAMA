"""
utils/uploads.py - Gestion de subida y borrado de imagenes en FAMA.

Centraliza la logica de almacenamiento para evitar duplicarla en cada route.
Los archivos se guardan en static/uploads/<subcarpeta>/.

Subcarpetas usadas:
  viviendas/    servicios/    compraventa/    foro/    perfiles/
"""
import os
from datetime import datetime

from flask import current_app
from werkzeug.utils import secure_filename

_EXTENSIONES = {"png", "jpg", "jpeg", "gif", "webp"}


def guardar_imagenes(archivos, subcarpeta: str) -> list:
    """
    Valida y guarda una lista de FileStorage en static/uploads/<subcarpeta>/.
    Ignora silenciosamente los archivos vacios o con extension no permitida.
    Devuelve la lista de nombres de archivo guardados.
    """
    nombres = []
    for archivo in archivos:
        if not archivo or archivo.filename == "":
            continue
        ext = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
        if ext not in _EXTENSIONES:
            continue
        # Nombre unico: timestamp_microsegundos + nombre seguro para evitar colisiones
        nombre = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{secure_filename(archivo.filename)}"
        carpeta = os.path.join(current_app.static_folder, "uploads", subcarpeta)
        os.makedirs(carpeta, exist_ok=True)
        archivo.save(os.path.join(carpeta, nombre))
        nombres.append(nombre)
    return nombres


def eliminar_imagenes(nombres, subcarpeta: str):
    """Borra del disco los archivos indicados en static/uploads/<subcarpeta>/."""
    for nombre in (nombres or []):
        if not nombre:
            continue
        ruta = os.path.join(current_app.static_folder, "uploads", subcarpeta, nombre)
        if os.path.exists(ruta):
            os.remove(ruta)
