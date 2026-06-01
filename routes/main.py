"""
routes/main.py - Ruta principal de la aplicacion FAMA.

Sirve el dashboard de inicio con los ultimos anuncios de cada modulo
y el indicador de estado de la conexion con MongoDB.
"""
from flask import Blueprint, render_template

from utils.db import check_mongo_connection, get_db

# Sin prefijo de URL: este blueprint responde en la raiz '/'
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Pagina principal: verifica MongoDB y carga los ultimos anuncios de cada modulo.
    Los datos se pasan a la plantilla para poblar las secciones del dashboard.
    """
    # Comprobar la conexion con MongoDB antes de cualquier consulta
    # El resultado se muestra como indicador visual en el hero de la pagina
    mongo_ok, mongo_message = check_mongo_connection()

    db = get_db()

    # Obtener los 4 anuncios mas recientes de cada modulo para el dashboard.
    # Se usa limit(3) para no sobrecargar la pagina de inicio.
    viviendas = list(db.viviendas.find().sort("fecha_creacion", -1).limit(3))
    servicios  = list(db.servicios.find().sort("fecha_creacion", -1).limit(3))

    # En compraventa se excluye el merchandising: el index muestra solo segunda mano general
    compraventa = list(
        db.compraventa.find({"es_merchandising": False}).sort("fecha_creacion", -1).limit(3)
    )

    # Los eventos de ocio se ordenan por fecha ascendente (proximos primero)
    eventos = list(db.ocio.find().sort("fecha", 1).limit(3))

    return render_template(
        "index.html",
        mongo_ok=mongo_ok,           # Bool para mostrar/ocultar la alerta de error
        mongo_message=mongo_message, # Texto del estado que aparece en el hero
        viviendas=viviendas,
        servicios=servicios,
        compraventa=compraventa,
        eventos=eventos,
    )
