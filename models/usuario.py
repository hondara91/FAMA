"""
models/usuario.py - Modelo de datos para los usuarios de FAMA.

Encapsula toda la logica de creacion, autenticación, gestion de roles
y recuperacion de contrasena. Nunca almacena contraseñas en texto plano:
usa el hash de werkzeug (PBKDF2 + salt aleatorio).
"""
import secrets
from datetime import datetime

from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash


class Usuario:
    """Representa a un usuario de la plataforma FAMA."""

    # Único lugar donde se definen los roles validos; cualquier validación
    # de rol en el resto del código debe referenciar esta constante.
    ROLES_VALIDOS = ("usuario", "gestor", "admin")

    def __init__(self, db):
        # Referencia directa a la coleccion MongoDB para todas las operaciones
        self.coleccion = db.usuarios

    # ── Creación ──────────────────────────────────────────────────────────────

    def crear(self, nombre, email, password=None, nombre_real="", apellidos="",
              pregunta_seguridad=None, respuesta_seguridad=None, rol="usuario", validado=False):
        """
        Crea un nuevo usuario. Devuelve el ObjectId insertado, None si el email
        ya existe, o 'nombre_duplicado' si el nombre ya está en uso.
        """
        if self.coleccion.find_one({"email": email}):
            return None
        if self.coleccion.find_one({"nombre": {"$regex": f"^{nombre}$", "$options": "i"}}):
            return "nombre_duplicado"

        password_hash = generate_password_hash(password) if password else generate_password_hash(secrets.token_hex(16))

        usuario = {
            "nombre": nombre,
            "nombre_real": nombre_real,
            "apellidos": apellidos,
            "email": email,
            "password": password_hash,
            "rol": rol,
            "foto_perfil": None,
            "pregunta_seguridad": pregunta_seguridad,
            "respuesta_seguridad": generate_password_hash(respuesta_seguridad.lower()) if respuesta_seguridad else None,
            "debe_cambiar_password": False,
            "activo": True,
            "validado": validado,
            "email_verificado": True,
            "fecha_registro": datetime.now(),
        }
        resultado = self.coleccion.insert_one(usuario)
        return resultado.inserted_id

    # ── Autenticación ─────────────────────────────────────────────────────────

    def autenticar(self, nombre, password):
        """
        Verifica nombre de usuario y contrasena (case-insensitive).
        Devuelve el documento completo del usuario o None si falla.
        Solo permite el acceso a cuentas activas Y validadas por el admin.
        """
        usuario = self.coleccion.find_one({
            "nombre": {"$regex": f"^{nombre}$", "$options": "i"},
            "activo": True,
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
        para obligar al usuario a escoger una nueva en su proximo inicio de sesión.
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

    def configurar_seguridad(self, user_id, pregunta, respuesta):
        """Establece la pregunta y respuesta de seguridad (primer acceso)."""
        self.coleccion.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "pregunta_seguridad":  pregunta,
                "respuesta_seguridad": generate_password_hash(respuesta.lower()),
            }},
        )

    def verificar_respuesta_seguridad(self, nombre, respuesta):
        """Comprueba la respuesta de seguridad. Devuelve False si el usuario no tiene pregunta configurada."""
        usuario = self.coleccion.find_one({"nombre": nombre})
        if usuario and usuario.get("respuesta_seguridad"):
            return check_password_hash(usuario["respuesta_seguridad"], respuesta.lower())
        return False

    def validar_usuario(self, user_id):
        """Aprueba la cuenta de un usuario pendiente de validación."""
        self.coleccion.update_one({"_id": ObjectId(user_id)}, {"$set": {"validado": True}})

    def eliminar(self, user_id):
        """Desactiva un usuario (soft-delete) poniendo 'activo' a False."""
        self.coleccion.update_one({"_id": ObjectId(user_id)}, {"$set": {"activo": False}})

    def reactivar(self, user_id):
        """Vuelve a activar un usuario previamente desactivado."""
        self.coleccion.update_one({"_id": ObjectId(user_id)}, {"$set": {"activo": True}})

    def eliminar_definitivo(self, user_id):
        """Borra el documento del usuario de forma permanente e irreversible."""
        self.coleccion.delete_one({"_id": ObjectId(user_id)})
