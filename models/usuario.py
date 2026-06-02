"""
models/usuario.py - Modelo de datos para los usuarios de FAMA.

Encapsula toda la logica de creacion, autenticacion, gestion de roles
y recuperacion de contrasena. Nunca almacena contrasenias en texto plano:
usa el hash de werkzeug (PBKDF2 + salt aleatorio).
"""
import secrets
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

    def crear(self, nombre, email, rol="usuario", validado=False):
        """
        Crea un nuevo usuario con contrasena interna aleatoria (el usuario la recibira
        por email cuando el admin apruebe su cuenta).
        Devuelve el ObjectId insertado o None si el email ya existe.
        """
        if self.coleccion.find_one({"email": email}):
            return None

        usuario = {
            "nombre": nombre,
            "email": email,
            # Contrasena bloqueada hasta que el admin apruebe la cuenta y se asigne fama1234
            "password": generate_password_hash(secrets.token_hex(16)),
            "rol": rol,
            "foto_perfil": None,
            "pregunta_seguridad": None,
            "respuesta_seguridad": None,
            "debe_cambiar_password": False,
            "activo": True,
            "validado": validado,
            "email_verificado": True,
            "fecha_registro": datetime.now(),
        }
        resultado = self.coleccion.insert_one(usuario)
        return resultado.inserted_id

    # ── Autenticacion ─────────────────────────────────────────────────────────

    def autenticar(self, email, password):
        """
        Verifica email y contrasena.
        Devuelve el documento completo del usuario o None si falla.
        Solo permite el acceso a cuentas activas Y validadas por el admin.
        """
        usuario = self.coleccion.find_one({
            "email": email,
            "activo": True,
            "email_verificado": True,
            "validado": True,
        })
        if usuario and check_password_hash(usuario["password"], password):
            return usuario
        return None

    def obtener_por_email(self, email):
        """Busca un usuario por email sin restricciones de estado."""
        return self.coleccion.find_one({"email": email})

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
        Establece la contrasena a 'fama1234' y activa el flag 'debe_cambiar_password'
        para obligar al usuario a escoger una nueva en su proximo inicio de sesion.
        """
        self.coleccion.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "password": generate_password_hash("fama1234"),
                "debe_cambiar_password": True,
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

    def establecer_password_temporal(self, user_id, password_temporal):
        """Asigna una contrasena temporal y activa el flag de cambio obligatorio en el proximo login."""
        self.coleccion.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "password": generate_password_hash(password_temporal),
                "debe_cambiar_password": True,
            }},
        )

    def verificar_respuesta_seguridad(self, email, respuesta):
        """Comprueba la respuesta de seguridad. Devuelve False si el usuario no tiene pregunta configurada."""
        usuario = self.coleccion.find_one({"email": email})
        if usuario and usuario.get("respuesta_seguridad"):
            return check_password_hash(usuario["respuesta_seguridad"], respuesta.lower())
        return False

    def validar_usuario(self, user_id):
        """Aprueba la cuenta de un usuario pendiente de validacion."""
        self.coleccion.update_one({"_id": ObjectId(user_id)}, {"$set": {"validado": True}})

    def eliminar(self, user_id):
        """
        Desactiva un usuario (soft-delete) poniendo 'activo' a False.
        No borra el documento para conservar el historial de actividad.
        """
        self.coleccion.update_one({"_id": ObjectId(user_id)}, {"$set": {"activo": False}})
