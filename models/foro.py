"""
models/foro.py - Modelos de datos para el módulo de Foro.

Colecciones MongoDB:
  - foro_canales:   canales tematicos que agrupan los hilos.
  - foro_posts:     publicaciones principales (pertenecen a un canal).
  - foro_respuestas: respuestas anidadas bajo un post.
"""
from datetime import datetime

from bson import ObjectId


class ForoCanal:
    """Representa un canal tematico del foro."""

    COLORES = ("primary", "success", "warning", "danger", "info", "secondary", "dark")
    ICONOS  = [
        ("chat-dots",    "General"),
        ("people",       "Comunidad"),
        ("house",        "Vivienda"),
        ("map",          "Ciudad"),
        ("briefcase",    "Trabajo"),
        ("calendar",     "Eventos"),
        ("star",         "Destacado"),
        ("anchor",       "Armada"),
        ("shield-check", "Seguridad"),
        ("book",         "Formacion"),
        ("car-front",    "Transporte"),
        ("heart",        "Ocio"),
    ]

    def __init__(self, db):
        self.coleccion = db.foro_canales

    def crear(self, nombre, descripcion, color, icono, user_id, nombre_usuario):
        canal = {
            "nombre":         nombre,
            "descripcion":    descripcion,
            "color":          color,
            "icono":          icono,
            "usuario_id":     user_id,
            "nombre_usuario": nombre_usuario,
            "fecha_creacion": datetime.now(),
        }
        return self.coleccion.insert_one(canal).inserted_id

    def obtener_todos(self, skip=0, limit=0):
        cursor = self.coleccion.find().sort("fecha_creacion", 1)
        if limit:
            cursor = cursor.skip(skip).limit(limit)
        return list(cursor)

    def contar(self):
        return self.coleccion.count_documents({})

    def obtener_por_id(self, canal_id):
        return self.coleccion.find_one({"_id": ObjectId(canal_id)})

    def eliminar(self, canal_id):
        self.coleccion.delete_one({"_id": ObjectId(canal_id)})


class ForoPost:
    """Representa una publicacion principal del foro."""

    def __init__(self, db):
        self.coleccion = db.foro_posts

    # ── Creación ──────────────────────────────────────────────────────────────

    def obtener_por_canal(self, canal_id, filtros=None):
        """Devuelve posts de un canal ordenados por fecha descendente."""
        query = dict(filtros or {})
        query["canal_id"] = str(canal_id)
        return list(self.coleccion.find(query).sort("fecha_creacion", -1))

    def contar_por_canal(self, canal_id):
        return self.coleccion.count_documents({"canal_id": str(canal_id)})

    def crear(self, titulo, contenido, fotos, canal_id, user_id, nombre_usuario):
        """Inserta un nuevo post y devuelve su ObjectId."""
        post = {
            "titulo":          titulo,
            "contenido":       contenido,
            "fotos":           fotos or [],
            "imagen":          None,
            "canal_id":        str(canal_id),
            "usuario_id":      user_id,
            "nombre_usuario":  nombre_usuario,
            "fecha_creacion":  datetime.now(),
            "fecha_modificacion": datetime.now(),
        }
        return self.coleccion.insert_one(post).inserted_id

    # ── Consultas ─────────────────────────────────────────────────────────────

    def obtener_todos(self, filtros=None):
        """Devuelve todos los posts ordenados por fecha descendente (mas recientes primero)."""
        return list(self.coleccion.find(filtros or {}).sort("fecha_creacion", -1))

    def obtener_por_id(self, post_id):
        """Busca un post por su ObjectId."""
        return self.coleccion.find_one({"_id": ObjectId(post_id)})

    def obtener_por_usuario(self, user_id):
        """Devuelve los posts publicados por un usuario concreto."""
        return list(self.coleccion.find({"usuario_id": user_id}).sort("fecha_creacion", -1))

    # ── Actualización y borrado ───────────────────────────────────────────────

    def actualizar(self, post_id, datos):
        """Actualiza los campos indicados y renueva la fecha de modificacion."""
        datos["fecha_modificacion"] = datetime.now()
        self.coleccion.update_one({"_id": ObjectId(post_id)}, {"$set": datos})

    def eliminar(self, post_id):
        """Borra fisicamente el post. Las respuestas asociadas deben borrarse aparte."""
        self.coleccion.delete_one({"_id": ObjectId(post_id)})

    # ── Buscador ──────────────────────────────────────────────────────────────

    def construir_filtros(self, form_data):
        """Traduce los parametros GET del buscador a una query MongoDB."""
        query = {}
        # Búsqueda parcial insensible a mayúsculas en título y contenido
        if form_data.get("q"):
            query["$or"] = [
                {"titulo":    {"$regex": form_data["q"], "$options": "i"}},
                {"contenido": {"$regex": form_data["q"], "$options": "i"}},
            ]
        # Filtro por autor (nombre de usuario exacto)
        if form_data.get("autor"):
            query["nombre_usuario"] = {"$regex": form_data["autor"], "$options": "i"}
        return query


class ForoRespuesta:
    """Representa una respuesta a un post del foro."""

    def __init__(self, db):
        self.coleccion = db.foro_respuestas

    # ── Creación ──────────────────────────────────────────────────────────────

    def crear(self, post_id, contenido, fotos, user_id, nombre_usuario):
        """Inserta una nueva respuesta asociada al post indicado."""
        respuesta = {
            "post_id":        post_id,
            "contenido":      contenido,
            "fotos":          fotos or [],
            "imagen":         None,   # Legado
            "usuario_id":     user_id,
            "nombre_usuario": nombre_usuario,
            "fecha_creacion": datetime.now(),
        }
        return self.coleccion.insert_one(respuesta).inserted_id

    # ── Consultas ─────────────────────────────────────────────────────────────

    def obtener_por_post(self, post_id):
        """Devuelve todas las respuestas de un post ordenadas cronologicamente."""
        return list(self.coleccion.find({"post_id": post_id}).sort("fecha_creacion", 1))

    def obtener_por_id(self, respuesta_id):
        """Busca una respuesta por su ObjectId."""
        return self.coleccion.find_one({"_id": ObjectId(respuesta_id)})

    def contar_por_post(self, post_id):
        """Devuelve el numero de respuestas de un post."""
        return self.coleccion.count_documents({"post_id": post_id})

    # ── Borrado ───────────────────────────────────────────────────────────────

    def eliminar(self, respuesta_id):
        """Borra fisicamente una respuesta."""
        self.coleccion.delete_one({"_id": ObjectId(respuesta_id)})

    def eliminar_por_post(self, post_id):
        """Borra todas las respuestas de un post (usado al eliminar el post padre)."""
        self.coleccion.delete_many({"post_id": post_id})
