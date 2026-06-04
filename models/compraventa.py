"""
models/compraventa.py - Modelo de datos para el módulo de Compra-Venta.

Gestiona dos tipos de artículos en la misma coleccion MongoDB:
  - Articulos de segunda mano generales (es_merchandising=False).
  - Merchandising oficial de unidades de la Armada (es_merchandising=True),
    que se muestran en la seccion especial 'Tienda Armada'.
"""
from datetime import datetime

from bson import ObjectId


class Compraventa:
    """Representa un anuncio de compraventa en la plataforma FAMA."""

    def __init__(self, db):
        self.coleccion = db.compraventa

    # ── Creación ──────────────────────────────────────────────────────────────

    def crear(self, datos, user_id, nombre_usuario):
        """Construye y persiste el documento de un nuevo articulo. Devuelve su ObjectId."""
        anuncio = {
            "nombre_articulo": datos.get("nombre_articulo"),
            "uco":             datos.get("uco"),          # Unidad, Centro u Organismo del vendedor
            "precio":          datos.get("precio"),
            "descripcion":     datos.get("descripcion"),
            # Flag que determina si el articulo va a la sección Tienda Armada
            "es_merchandising": datos.get("es_merchandising", False),
            # Solo relevante si es_merchandising=True; nombre de la unidad Armada
            "unidad_armada":    datos.get("unidad_armada", ""),
            "fotos":            datos.get("fotos", []),
            "usuario_id":       user_id,
            "nombre_usuario":   nombre_usuario,
            "fecha_expiracion":   datos.get("fecha_expiracion"),
            "fecha_creacion":     datetime.now(),
            "fecha_modificacion": datetime.now(),
        }
        return self.coleccion.insert_one(anuncio).inserted_id

    # ── Consultas ─────────────────────────────────────────────────────────────

    def obtener_todos(self, filtros=None):
        """Devuelve artículos ordenados por fecha de creacion descendente."""
        return list(self.coleccion.find(filtros or {}).sort("fecha_creacion", -1))

    def obtener_merchandising(self):
        """
        Devuelve solo los artículos de la Tienda Armada.
        La ruta /compraventa/ usa un filtro separado para excluirlos
        y mostrar solo segunda mano general.
        """
        return list(self.coleccion.find({"es_merchandising": True}).sort("fecha_creacion", -1))

    def obtener_por_id(self, anuncio_id):
        """Busca un articulo por su ObjectId."""
        return self.coleccion.find_one({"_id": ObjectId(anuncio_id)})

    def obtener_por_usuario(self, user_id):
        """Devuelve los artículos publicados por un usuario especifico."""
        return list(self.coleccion.find({"usuario_id": user_id}).sort("fecha_creacion", -1))

    # ── Actualización y borrado ───────────────────────────────────────────────

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
        La ruta /compraventa/ anade manualmente 'es_merchandising=False'
        después de llamar a este metodo para excluir la Tienda Armada.
        """
        query = {}
        # Búsqueda parcial insensible a mayúsculas para nombre y UCO
        if form_data.get("nombre_articulo"):
            query["nombre_articulo"] = {"$regex": form_data["nombre_articulo"], "$options": "i"}
        if form_data.get("uco"):
            query["uco"] = {"$regex": form_data["uco"], "$options": "i"}
        # Filtro booleano para mostrar solo merchandising (usado por la Tienda Armada)
        if form_data.get("es_merchandising"):
            query["es_merchandising"] = True
        return query
