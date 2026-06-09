"""
models/ocio.py - Modelo de datos para el módulo de Ocio.

Gestiona eventos de ocio: creacion, edicion, eliminacion,
inscripcion/desinscripcion con control de aforo y exportacion
al formato que espera FullCalendar.js.
"""
from datetime import datetime

from bson import ObjectId


class Ocio:
    """Representa un evento de ocio en la plataforma FAMA."""

    # Mapa de color por tipo de evento usado tanto en el calendario
    # como en los badges de las tarjetas (mismos valores que Bootstrap/FullCalendar)
    _COLORES_TIPO = {
        "Deporte":  "#198754",   # Verde Bootstrap success
        "Cultural": "#0d6efd",   # Azul Bootstrap primary
        "Otros":    "#6c757d",   # Gris Bootstrap secondary
    }

    def __init__(self, db):
        self.coleccion = db.ocio

    # ── Creación ──────────────────────────────────────────────────────────────

    def crear(self, datos, user_id, nombre_usuario):
        """Crea un nuevo evento y devuelve su ObjectId."""
        evento = {
            "tipo_evento":  datos.get("tipo_evento"),
            "titulo":       datos.get("titulo"),
            "fecha":        datos.get("fecha"),   # String 'YYYY-MM-DD' (input[type=date])
            "hora":         datos.get("hora"),    # String 'HH:MM'      (input[type=time])
            "lugar":        datos.get("lugar"),
            "aforo_maximo": int(datos.get("aforo_maximo", 0)),
            "descripcion":  datos.get("descripcion"),
            "inscritos":    [],         # Lista de user_id (strings) de participantes
            "usuario_id":      user_id,
            "nombre_usuario":  nombre_usuario,
            "fecha_creacion":  datetime.now(),
            "fecha_modificacion": datetime.now(),
        }
        return self.coleccion.insert_one(evento).inserted_id

    # ── Consultas ─────────────────────────────────────────────────────────────

    def obtener_todos(self, filtros=None, skip=0, limit=0):
        """Devuelve todos los eventos, ordenados por fecha ascendente (próximos primero)."""
        cursor = self.coleccion.find(filtros or {}).sort("fecha", 1)
        if limit:
            cursor = cursor.skip(skip).limit(limit)
        return list(cursor)

    def contar(self, filtros=None):
        return self.coleccion.count_documents(filtros or {})

    def obtener_por_id(self, evento_id):
        """Busca un evento por su ObjectId."""
        return self.coleccion.find_one({"_id": ObjectId(evento_id)})

    def obtener_por_usuario(self, user_id):
        """Devuelve los eventos creados por un usuario concreto."""
        return list(self.coleccion.find({"usuario_id": user_id}).sort("fecha", 1))

    # ── Actualización y borrado ───────────────────────────────────────────────

    def actualizar(self, evento_id, datos):
        """Actualiza los campos de un evento y renueva su fecha de modificacion."""
        datos["fecha_modificacion"] = datetime.now()
        self.coleccion.update_one({"_id": ObjectId(evento_id)}, {"$set": datos})

    def eliminar(self, evento_id):
        """Elimina fisicamente un evento (las inscripciones se pierden con el)."""
        self.coleccion.delete_one({"_id": ObjectId(evento_id)})

    # ── Gestión de inscripciones ──────────────────────────────────────────────

    def inscribir_usuario(self, evento_id, user_id):
        """
        Inscribe al usuario en el evento si hay plazas disponibles.

        Comprueba tres condiciones antes de inscribir:
          1. El evento existe.
          2. El usuario no esta ya inscrito (evita duplicados).
          3. No se ha superado el aforo maximo.

        Devuelve (True, mensaje_ok) o (False, motivo_error).
        """
        evento = self.obtener_por_id(evento_id)

        # Condicion 1: el evento debe existir en la base de datos
        if not evento:
            return False, "Evento no encontrado."

        # Condicion 2: el user_id no debe estar ya en la lista de inscritos
        if user_id in evento.get("inscritos", []):
            return False, "Ya estas inscrito en este evento."

        # Condicion 3: el número de inscritos no puede superar el aforo máximo
        if len(evento.get("inscritos", [])) >= evento.get("aforo_maximo", 0):
            return False, "El aforo máximo ha sido alcanzado."

        # $push anade el user_id al array 'inscritos' de forma atomica en MongoDB
        self.coleccion.update_one(
            {"_id": ObjectId(evento_id)},
            {"$push": {"inscritos": user_id}},
        )
        return True, "Inscripción realizada con éxito."

    def desinscribir_usuario(self, evento_id, user_id):
        """
        Elimina el user_id de la lista de inscritos.
        $pull elimina todas las ocurrencias del valor en el array.
        """
        self.coleccion.update_one(
            {"_id": ObjectId(evento_id)},
            {"$pull": {"inscritos": user_id}},
        )

    # ── Integracion con FullCalendar ──────────────────────────────────────────

    def obtener_para_calendario(self):
        """
        Devuelve los eventos en el formato de objeto que espera FullCalendar.js:
          { id, title, start (ISO 8601), color }

        Usa una proyeccion MongoDB para traer solo los campos necesarios
        y reducir el trafico de red.
        """
        # Proyeccion: solo traer los campos que necesita FullCalendar (1 = incluir)
        eventos = self.coleccion.find(
            {},
            {"titulo": 1, "fecha": 1, "hora": 1, "tipo_evento": 1}
        )
        return [
            {
                "id":    str(e["_id"]),
                "title": e.get("titulo", ""),
                # FullCalendar espera el campo 'start' en formato ISO 8601
                "start": f"{e.get('fecha', '')}T{e.get('hora', '00:00')}",
                # Color del evento segun su tipo; azul por defecto si el tipo es desconocido
                "color": self._COLORES_TIPO.get(e.get("tipo_evento", ""), "#0d6efd"),
            }
            for e in eventos
        ]

    # ── Buscador ──────────────────────────────────────────────────────────────

    def construir_filtros(self, form_data):
        """
        Traduce los parametros GET del formulario de busqueda a una
        query MongoDB. Solo incluye los campos que el usuario haya rellenado.
        """
        query = {}
        # Coincidencia exacta para el tipo de evento (select)
        if form_data.get("tipo_evento"):
            query["tipo_evento"] = form_data["tipo_evento"]
        # Búsqueda parcial insensible a mayúsculas para título y lugar
        if form_data.get("titulo"):
            query["titulo"] = {"$regex": form_data["titulo"], "$options": "i"}
        if form_data.get("lugar"):
            query["lugar"] = {"$regex": form_data["lugar"], "$options": "i"}
        # Coincidencia exacta para la fecha (string 'YYYY-MM-DD')
        if form_data.get("fecha"):
            query["fecha"] = form_data["fecha"]
        return query
