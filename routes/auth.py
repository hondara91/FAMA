"""
routes/auth.py - Rutas de autenticacion de FAMA.

Gestiona todo el ciclo de identidad del usuario:
  /auth/registro        -> Crear nueva cuenta
  /auth/login           -> Iniciar sesion
  /auth/logout          -> Cerrar sesion
  /auth/cambiar-password-> Cambiar contrasenia (usuario autenticado)
  /auth/recuperar       -> Recuperar cuenta via pregunta de seguridad
"""
import os
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from models.usuario import Usuario
from utils.db import get_db
from utils.decorators import login_required
from utils.logs import actualizar_contadores, registrar_log

# Prefijo /auth para todas las rutas de este blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_EXTENSIONES_IMAGEN = {"png", "jpg", "jpeg", "gif", "webp"}


def _guardar_foto_perfil(archivo):
    """Guarda una foto de perfil en static/uploads/perfiles/."""
    if not archivo or archivo.filename == "":
        return None

    ext = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
    if ext not in _EXTENSIONES_IMAGEN:
        return None

    nombre = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{secure_filename(archivo.filename)}"
    carpeta = os.path.join(current_app.static_folder, "uploads", "perfiles")
    os.makedirs(carpeta, exist_ok=True)

    archivo.save(os.path.join(carpeta, nombre))
    return nombre


def _eliminar_foto_perfil(nombre):
    """Borra del disco una foto de perfil anterior si existe."""
    if not nombre:
        return
    ruta = os.path.join(current_app.static_folder, "uploads", "perfiles", nombre)
    if os.path.exists(ruta):
        os.remove(ruta)


# ── Registro ──────────────────────────────────────────────────────────────────

@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Muestra el formulario de registro (GET) y procesa el alta (POST)."""
    if request.method == "POST":
        db = get_db()
        modelo = Usuario(db)

        nombre = request.form.get("nombre", "").strip()
        email  = request.form.get("email", "").strip().lower()

        if not all([nombre, email]):
            flash("El nombre y el email son obligatorios.", "danger")
            return render_template("auth/registro.html")

        if "@" not in email:
            flash("Introduce un email válido.", "danger")
            return render_template("auth/registro.html")

        resultado = modelo.crear(nombre, email)
        if resultado is None:
            flash("El email ya está registrado.", "danger")
            return render_template("auth/registro.html")
        if resultado == "nombre_duplicado":
            flash("Ese nombre de usuario ya está en uso. Elige otro.", "danger")
            return render_template("auth/registro.html")

        registrar_log(db, "registro", "crear_usuario", nombre, f"Email: {email}")
        actualizar_contadores(db)

        flash(
            "Solicitud recibida. Tu cuenta está pendiente de validación por el administrador. "
            "Este proceso puede durar unas horas.",
            "info",
        )
        return redirect(url_for("auth.login"))

    # GET: mostrar el formulario vacio
    return render_template("auth/registro.html")


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Muestra el formulario de login (GET) y autentica al usuario (POST)."""
    # Si ya tiene sesion activa, redirigir al inicio sin mostrar el formulario
    if "user_id" in session:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        db = get_db()
        modelo = Usuario(db)

        nombre_login = request.form.get("nombre", "").strip()
        password     = request.form.get("password", "")

        usuario = modelo.autenticar(nombre_login, password)
        if not usuario:
            candidato = db.usuarios.find_one({"nombre": nombre_login})
            if candidato and candidato.get("activo") and not candidato.get("validado"):
                flash("Tu cuenta está pendiente de validación por el administrador.", "warning")
            else:
                flash("Usuario o contraseña incorrectos.", "danger")
            return render_template("auth/login.html")

        # ── Construir la sesion Flask ─────────────────────────────────────────
        # Solo se guardan los datos necesarios en la cookie de sesion (firmada con SECRET_KEY)
        session["user_id"] = str(usuario["_id"])  # ObjectId convertido a string
        session["nombre"]  = usuario["nombre"]
        session["email"]   = usuario["email"]
        session["rol"]     = usuario["rol"]        # Usado por los decoradores de acceso
        session["foto_perfil"] = usuario.get("foto_perfil")

        # Si el admin reseteo la contrasenia, obligar al usuario a cambiarla ahora
        if usuario.get("debe_cambiar_password"):
            flash("Tu contrasenia fue restablecida. Cambiala antes de continuar.", "warning")
            return redirect(url_for("auth.cambiar_password"))

        flash(f"Bienvenido, {usuario['nombre']}!", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/login.html")


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route("/logout")
def logout():
    """Destruye la sesion activa y redirige al login."""
    nombre = session.get("nombre", "")
    session.clear()  # Elimina todos los datos de la cookie de sesion
    flash(f"Sesion cerrada. Hasta pronto, {nombre}!", "info")
    return redirect(url_for("auth.login"))


# ── Cambio de contrasenia (usuario autenticado) ───────────────────────────────

@auth_bp.route("/cambiar-password", methods=["GET", "POST"])
@login_required  # Requiere sesion activa
def cambiar_password():
    """Permite al usuario autenticado actualizar su propia contrasenia."""
    if request.method == "POST":
        db = get_db()
        modelo = Usuario(db)

        password_actual = request.form.get("password_actual", "")
        nueva    = request.form.get("nueva_password", "")
        confirmar = request.form.get("confirmar_password", "")

        if not modelo.autenticar(session["nombre"], password_actual):
            flash("La contrasenia actual es incorrecta.", "danger")
            return render_template("auth/cambiar_password.html")

        if nueva != confirmar:
            flash("Las contrasenias nuevas no coinciden.", "danger")
            return render_template("auth/cambiar_password.html")

        if len(nueva) < 6:
            flash("La nueva contrasenia debe tener al menos 6 caracteres.", "danger")
            return render_template("auth/cambiar_password.html")

        # Persistir el nuevo hash y desactivar el flag de cambio obligatorio
        modelo.cambiar_password(session["user_id"], nueva)
        registrar_log(db, "registro", "cambiar_password", session["nombre"])
        flash("Contrasenia cambiada correctamente.", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/cambiar_password.html")


# ── Simulación de rol ────────────────────────────────────────────────────────

@auth_bp.route("/simular-rol/<rol>")
@login_required
def simular_rol(rol):
    """Permite al admin simular temporalmente otro rol para probar la interfaz."""
    roles_validos = ("admin", "gestor", "usuario")

    # Solo el admin real puede activar la simulación
    rol_real = session.get("rol_real") or session.get("rol")
    if rol_real != "admin":
        flash("Solo el administrador puede simular roles.", "danger")
        return redirect(url_for("main.index"))

    if rol not in roles_validos:
        flash("Rol no válido.", "danger")
        return redirect(url_for("main.index"))

    # Guardar el rol real la primera vez que se activa la simulación
    if not session.get("rol_real"):
        session["rol_real"] = session["rol"]

    session["rol"] = rol
    return redirect(request.referrer or url_for("main.index"))


# ── Perfil de usuario ────────────────────────────────────────────────────────

@auth_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    """Permite al usuario cambiar su foto de perfil."""
    db = get_db()
    modelo = Usuario(db)
    usuario = modelo.obtener_por_id(session["user_id"])

    if not usuario:
        session.clear()
        flash("No se ha encontrado tu usuario. Vuelve a iniciar sesion.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        if request.form.get("borrar_foto"):
            _eliminar_foto_perfil(usuario.get("foto_perfil"))
            modelo.actualizar(session["user_id"], {"foto_perfil": None})
            session["foto_perfil"] = None
            registrar_log(db, "registro", "borrar_foto_perfil", session["nombre"])
            flash("Foto de perfil eliminada.", "info")
            return redirect(url_for("auth.perfil"))

        foto = _guardar_foto_perfil(request.files.get("foto_perfil"))
        if not foto:
            flash("Selecciona una imagen valida: PNG, JPG, JPEG, GIF o WEBP.", "danger")
            return render_template("auth/perfil.html", usuario=usuario)

        _eliminar_foto_perfil(usuario.get("foto_perfil"))
        modelo.actualizar(session["user_id"], {"foto_perfil": foto})
        session["foto_perfil"] = foto
        registrar_log(db, "registro", "cambiar_foto_perfil", session["nombre"])

        flash("Foto de perfil actualizada.", "success")
        return redirect(url_for("auth.perfil"))

    return render_template("auth/perfil.html", usuario=usuario)


# ── Recuperacion de cuenta ────────────────────────────────────────────────────

@auth_bp.route("/recuperar", methods=["GET", "POST"])
def recuperar_password():
    """
    Permite recuperar el acceso respondiendo la pregunta de seguridad.
    No requiere sesion activa (el usuario no puede hacer login).
    """
    if request.method == "POST":
        db = get_db()
        modelo = Usuario(db)

        nombre_rec = request.form.get("nombre", "").strip()
        respuesta  = request.form.get("respuesta_seguridad", "").strip()
        nueva      = request.form.get("nueva_password", "")
        confirmar  = request.form.get("confirmar_password", "")

        if not modelo.verificar_respuesta_seguridad(nombre_rec, respuesta):
            flash("Usuario o respuesta de seguridad incorrectos.", "danger")
            return render_template("auth/recuperar.html")

        if nueva != confirmar:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("auth/recuperar.html")

        usuario = db.usuarios.find_one({"nombre": nombre_rec})
        if usuario:
            modelo.cambiar_password(str(usuario["_id"]), nueva)
            flash("Contraseña recuperada correctamente. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/recuperar.html")
