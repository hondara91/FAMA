"""
models/vivienda.py - Modelo de datos para el módulo de Viviendas.

Gestiona alquileres, intercambios y pisos compartidos del personal militar.
Los campos 'usuario_id' y 'nombre_usuario' permiten mostrar el autor
y controlar los permisos de edicion/borrado en las rutas.
"""
from datetime import datetime

from bson import ObjectId


class Vivienda:
    """Representa un anuncio de vivienda en la plataforma FAMA."""

    def __init__(self, db):
        self.coleccion = db.viviendas

    # ── Creación ──────────────────────────────────────────────────────────────

    def crear(self, datos, user_id, nombre_usuario):
        """Construye y persiste el documento de un nuevo anuncio. Devuelve su ObjectId."""
        anuncio = {
            "tipo_oferta":   datos.get("tipo_oferta"),    # alquiler | intercambio | compartir
            "tipo_inmueble": datos.get("tipo_inmueble"),  # Piso | Estudio | Chalet | Atico | Finca
            "ciudad":        datos.get("ciudad"),
            "zona":          datos.get("zona"),           # Barrio o zona dentro de la ciudad
            "habitaciones":  datos.get("habitaciones"),   # String: '1', '2', ... '5+'
            "banos":         datos.get("banos"),
            "planta":        datos.get("planta"),
            "precio":        datos.get("precio"),         # String con el importe en euros
            "extras":        datos.get("extras", []),     # Lista: ['garaje', 'ascensor', 'mascotas']
            "telefono":      datos.get("telefono"),
            "descripcion":   datos.get("descripcion"),
            "fotos":         datos.get("fotos", []),
            "usuario_id":       user_id,         # Usado para comprobar permisos de edicion
            "nombre_usuario":   nombre_usuario,  # Mostrado en la tarjeta sin consulta extra
            "fecha_expiracion":   datos.get("fecha_expiracion"),
            "fecha_creacion":     datetime.now(),
            "fecha_modificacion": datetime.now(),
        }
        return self.coleccion.insert_one(anuncio).inserted_id

    # ── Consultas ─────────────────────────────────────────────────────────────

    def obtener_todos(self, filtros=None):
        """Devuelve anuncios ordenados por fecha de creacion descendente (mas recientes primero)."""
        return list(self.coleccion.find(filtros or {}).sort("fecha_creacion", -1))

    def obtener_por_id(self, anuncio_id):
        """Busca un anuncio por su ObjectId. Devuelve None si no existe."""
        return self.coleccion.find_one({"_id": ObjectId(anuncio_id)})

    def obtener_por_usuario(self, user_id):
        """Devuelve los anuncios publicados por un usuario especifico."""
        return list(self.coleccion.find({"usuario_id": user_id}).sort("fecha_creacion", -1))

    # ── Actualización y borrado ───────────────────────────────────────────────

    def actualizar(self, anuncio_id, datos):
        """Actualiza campos con $set y renueva la fecha de modificacion."""
        datos["fecha_modificacion"] = datetime.now()
        self.coleccion.update_one({"_id": ObjectId(anuncio_id)}, {"$set": datos})

    def eliminar(self, anuncio_id):
        """Borra fisicamente el documento (no hay soft-delete en anuncios)."""
        self.coleccion.delete_one({"_id": ObjectId(anuncio_id)})

    # ── Buscador ──────────────────────────────────────────────────────────────

    def construir_filtros(self, form_data):
        """
        Traduce los parametros GET del buscador a una query MongoDB.
        Solo se anaden al diccionario los campos que el usuario relleno
        para no filtrar por campos vacios.
        """
        query = {}
        # Coincidencia exacta para los campos de tipo select
        if form_data.get("tipo_oferta"):
            query["tipo_oferta"] = form_data["tipo_oferta"]
        if form_data.get("tipo_inmueble"):
            query["tipo_inmueble"] = form_data["tipo_inmueble"]
        # $regex con 'i' para búsqueda parcial insensible a mayúsculas
        if form_data.get("ciudad"):
            query["ciudad"] = {"$regex": form_data["ciudad"], "$options": "i"}
        # Coincidencia exacta para el número de habitaciones (string del select)
        if form_data.get("habitaciones"):
            query["habitaciones"] = form_data["habitaciones"]
        return query
