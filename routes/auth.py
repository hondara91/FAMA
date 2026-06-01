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
from utils.email import confirmar_token_verificacion, enviar_verificacion_email
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

        # crear() devuelve None si el email ya esta registrado en MongoDB
        user_id = modelo.crear(nombre, email)
        if user_id is None:
            flash("El email ya esta registrado.", "danger")
            return render_template("auth/registro.html")

        # Registrar la accion en el log y actualizar snapshot de contadores
        registrar_log(db, "registro", "crear_usuario", nombre, f"Email: {email}")
        actualizar_contadores(db)

        # Enviar email de verificacion; si falla se avisa pero la cuenta queda creada
        enviado = enviar_verificacion_email(email, nombre)
        if enviado:
            flash(
                f"Cuenta creada. Hemos enviado un enlace de verificacion a {email}. "
                "Verifica tu correo y luego espera la aprobacion del administrador.",
                "info",
            )
        else:
            flash(
                "Cuenta creada pero no pudimos enviar el email de verificacion. "
                "Contacta con el administrador para activar tu cuenta.",
                "warning",
            )
        return redirect(url_for("auth.login"))

    # GET: mostrar el formulario vacio
    return render_template("auth/registro.html")


# ── Verificacion de email ─────────────────────────────────────────────────────

@auth_bp.route("/verificar-email/<token>")
def verificar_email(token):
    """Confirma la direccion de email del usuario tras hacer clic en el enlace."""
    email = confirmar_token_verificacion(token)
    if not email:
        flash("El enlace de verificacion es invalido o ha expirado.", "danger")
        return redirect(url_for("auth.login"))

    db = get_db()
    modelo = Usuario(db)
    usuario = modelo.obtener_por_email(email)

    if not usuario:
        flash("No se encontro ninguna cuenta con ese email.", "danger")
        return redirect(url_for("auth.login"))

    if usuario.get("email_verificado"):
        flash("Tu correo ya estaba verificado. Espera la aprobacion del administrador.", "info")
        return redirect(url_for("auth.login"))

    modelo.verificar_email_usuario(email)
    registrar_log(db, "registro", "verificar_email", usuario["nombre"], f"Email: {email}")
    flash(
        "Correo verificado correctamente. Tu cuenta esta pendiente de aprobacion "
        "por el administrador. Te avisaremos cuando puedas acceder.",
        "success",
    )
    return redirect(url_for("auth.login"))


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

        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # autenticar() comprueba email + hash de contrasenia + activo + email_verificado + validado
        usuario = modelo.autenticar(email, password)
        if not usuario:
            candidato = modelo.obtener_por_email(email)
            if candidato and candidato.get("activo"):
                if not candidato.get("email_verificado"):
                    flash(
                        "Debes verificar tu correo electronico antes de iniciar sesion. "
                        "Revisa tu bandeja de entrada.",
                        "warning",
                    )
                elif not candidato.get("validado"):
                    flash("Tu cuenta esta pendiente de validacion por el administrador.", "warning")
                else:
                    flash("Email o contrasenia incorrectos.", "danger")
            else:
                flash("Email o contrasenia incorrectos.", "danger")
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

        # Verificar la contrasenia actual antes de permitir el cambio
        # (usa autenticar() para reutilizar la logica de verificacion de hash)
        if not modelo.autenticar(session["email"], password_actual):
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

        email    = request.form.get("email", "").strip().lower()
        respuesta = request.form.get("respuesta_seguridad", "").strip()
        nueva     = request.form.get("nueva_password", "")
        confirmar = request.form.get("confirmar_password", "")

        # verificar_respuesta_seguridad() compara con el hash almacenado
        if not modelo.verificar_respuesta_seguridad(email, respuesta):
            # Mensaje generico para no revelar si el email existe
            flash("Email o respuesta de seguridad incorrectos.", "danger")
            return render_template("auth/recuperar.html")

        if nueva != confirmar:
            flash("Las contrasenias no coinciden.", "danger")
            return render_template("auth/recuperar.html")

        # Buscar el usuario por email para obtener su ObjectId y cambiar la contrasenia
        usuario = db.usuarios.find_one({"email": email})
        if usuario:
            modelo.cambiar_password(str(usuario["_id"]), nueva)
            flash("Contrasenia recuperada correctamente. Ya puedes iniciar sesion.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/recuperar.html")
