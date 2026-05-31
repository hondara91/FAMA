"""
models/usuario.py - Modelo de datos para los usuarios de FAMA.

Encapsula toda la logica de creacion, autenticacion, gestion de roles
y recuperacion de contrasena. Nunca almacena contrasenias en texto plano:
usa el hash de werkzeug (PBKDF2 + salt aleatorio).
"""
from datetime import datetime

from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash


class Usuario:
    """Representa a un usuario de la plataforma FAMA."""

    # Unico lugar donde se definen los roles validos; cualquier validacion
    # de rol en el resto del codigo debe referenciar esta constante.
    ROLES_VALIDOS = ("usuario", "gestor", "admin")

    def __init__(self, db):
        # Referencia directa a la coleccion MongoDB para todas las operaciones
        self.coleccion = db.usuarios

    # ── Creacion ──────────────────────────────────────────────────────────────

    def crear(self, nombre, email, password, pregunta_seguridad, respuesta_seguridad, rol="usuario"):
        """
        Crea un nuevo usuario con contrasena cifrada.
        Devuelve el ObjectId insertado o None si el email ya existe.
        """
        # Verificar unicidad del email antes de insertar
        if self.coleccion.find_one({"email": email}):
            return None  # Email duplicado: la ruta mostrara un flash de error

        usuario = {
            "nombre": nombre,
            "email": email,
            # Nunca almacenar la contrasena en texto plano; werkzeug usa PBKDF2+SHA256
            "password": generate_password_hash(password),
            "rol": rol,
            "foto_perfil": None,
            "pregunta_seguridad": pregunta_seguridad,
            # La respuesta se normaliza a minusculas antes de hashear para que la
            # comparacion no sea sensible a mayusculas en la recuperacion de cuenta
            "respuesta_seguridad": generate_password_hash(respuesta_seguridad.lower()),
            # Flag que fuerza al usuario a cambiar la contrasena tras un reset por admin
            "debe_cambiar_password": False,
            # Soft-delete: 'activo=False' desactiva sin borrar el historial
            "activo": True,
            "fecha_registro": datetime.now(),
        }
        resultado = self.coleccion.insert_one(usuario)
        return resultado.inserted_id

    # ── Autenticacion ─────────────────────────────────────────────────────────

    def autenticar(self, email, password):
        """
        Verifica email y contrasena.
        Devuelve el documento completo del usuario o None si falla.
        """
        # El filtro 'activo: True' impide el acceso a cuentas desactivadas por admin
        usuario = self.coleccion.find_one({"email": email, "activo": True})
        if usuario and check_password_hash(usuario["password"], password):
            return usuario
        # Devolver None en ambos casos (email incorrecto o contrasena incorrecta)
        # evita revelar si el email existe o no (enumeracion de usuarios)
        return None

    # ── Consultas ─────────────────────────────────────────────────────────────

    def obtener_por_id(self, user_id):
        """Busca un usuario por su ObjectId de MongoDB."""
        return self.coleccion.find_one({"_id": ObjectId(user_id)})

    def obtener_todos(self):
        """Devuelve todos los usuarios ordenados por fecha de registro descendente."""
        return list(self.coleccion.find().sort("fecha_registro", -1))

    # ── Actualizaciones ───────────────────────────────────────────────────────

    def actualizar(self, user_id, datos):
        """Actualiza los campos indicados del usuario usando $set (no sobreescribe todo)."""
        self.coleccion.update_one({"_id": ObjectId(user_id)}, {"$set": datos})

    def cambiar_rol(self, user_id, nuevo_rol):
        """
        Cambia el rol del usuario.
        Valida contra ROLES_VALIDOS para evitar roles arbitrarios en la BD.
        """
        if nuevo_rol in self.ROLES_VALIDOS:
            self.coleccion.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"rol": nuevo_rol}},
            )

    def resetear_password(self, user_id):
        """
        Establece la contrasena a 'Password' (valor conocido por el admin)
        y activa el flag 'debe_cambiar_password' para obligar al usuario a
        escoger una nueva en su proximo inicio de sesion.
        """
        self.coleccion.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "password": generate_password_hash("Password"),
                "debe_cambiar_password": True,  # La ruta de login redirige al formulario de cambio
            }},
        )

    def cambiar_password(self, user_id, nueva_password):
        """
        Actualiza la contrasena con el nuevo hash y desactiva el aviso
        de cambio obligatorio si estaba activo.
        """
        self.coleccion.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "password": generate_password_hash(nueva_password),
                "debe_cambiar_password": False,
            }},
        )

    def verificar_respuesta_seguridad(self, email, respuesta):
        """
        Comprueba la respuesta de seguridad para recuperar la cuenta.
        La comparacion es insensible a mayusculas (se normaliza con .lower()).
        """
        usuario = self.coleccion.find_one({"email": email})
        if usuario:
            # lower() para igualar la normalizacion aplicada al crear el usuario
            return check_password_hash(usuario["respuesta_seguridad"], respuesta.lower())
        return False

    def eliminar(self, user_id):
        """
        Desactiva un usuario (soft-delete) poniendo 'activo' a False.
        No borra el documento para conservar el historial de actividad.
        """
        self.coleccion.update_one({"_id": ObjectId(user_id)}, {"$set": {"activo": False}})
