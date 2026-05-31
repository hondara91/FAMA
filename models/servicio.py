"""
models/servicio.py - Modelo de datos para el modulo de Servicios.

Gestiona anuncios en los que el personal militar puede ofrecer
o buscar servicios: clases, viajes compartidos, trabajos, etc.
"""
from datetime import datetime

from bson import ObjectId


class Servicio:
    """Representa un anuncio de servicio en la plataforma FAMA."""

    def __init__(self, db):
        self.coleccion = db.servicios

    # ── Creacion ──────────────────────────────────────────────────────────────

    def crear(self, datos, user_id, nombre_usuario):
        """Construye y persiste el documento de un nuevo anuncio. Devuelve su ObjectId."""
        anuncio = {
            "tipo":      datos.get("tipo"),       # ofrecer | buscar
            "categoria": datos.get("categoria"),  # Viajes compartidos | Clases | Trabajos ...
            "titulo":    datos.get("titulo"),
            "precio":    datos.get("precio"),     # Importe en euros (puede estar vacio)
            "modalidad": datos.get("modalidad"),  # presencial | online
            "telefono":  datos.get("telefono"),
            "ciudad":    datos.get("ciudad"),
            "descripcion": datos.get("descripcion"),
            "usuario_id":     user_id,
            "nombre_usuario": nombre_usuario,
            "fecha_creacion":   datetime.now(),
            "fecha_modificacion": datetime.now(),
        }
        return self.coleccion.insert_one(anuncio).inserted_id

    # ── Consultas ─────────────────────────────────────────────────────────────

    def obtener_todos(self, filtros=None):
        """Devuelve servicios ordenados por fecha de creacion descendente."""
        return list(self.coleccion.find(filtros or {}).sort("fecha_creacion", -1))

    def obtener_por_id(self, anuncio_id):
        """Busca un servicio por su ObjectId."""
        return self.coleccion.find_one({"_id": ObjectId(anuncio_id)})

    def obtener_por_usuario(self, user_id):
        """Devuelve los servicios publicados por un usuario especifico."""
        return list(self.coleccion.find({"usuario_id": user_id}).sort("fecha_creacion", -1))

    # ── Actualizacion y borrado ───────────────────────────────────────────────

    def actualizar(self, anuncio_id, datos):
        """Actualiza campos con $set y renueva la fecha de modificacion."""
        datos["fecha_modificacion"] = datetime.now()
        self.coleccion.update_one({"_id": ObjectId(anuncio_id)}, {"$set": datos})

    def eliminar(self, anuncio_id):
        """Borra fisicamente el documento."""
        self.coleccion.delete_one({"_id": ObjectId(anuncio_id)})

    # ── Buscador ──────────────────────────────────────────────────────────────

    def construir_filtros(self, form_data):
        """
        Traduce los parametros GET del buscador a una query MongoDB.
        Los campos de texto usan $regex para busqueda parcial.
        """
        query = {}
        # Coincidencias exactas para los campos de tipo select
        if form_data.get("tipo"):
            query["tipo"] = form_data["tipo"]
        if form_data.get("categoria"):
            query["categoria"] = form_data["categoria"]
        if form_data.get("modalidad"):
            query["modalidad"] = form_data["modalidad"]
        # Busqueda parcial insensible a mayusculas para texto libre
        if form_data.get("ciudad"):
            query["ciudad"] = {"$regex": form_data["ciudad"], "$options": "i"}
        if form_data.get("titulo"):
            query["titulo"] = {"$regex": form_data["titulo"], "$options": "i"}
        return query
