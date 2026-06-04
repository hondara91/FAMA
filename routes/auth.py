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
from utils.validators import validar_password_fuerte

# Prefijo /auth para todas las rutas de este blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

PREGUNTAS_SEGURIDAD = [
    "¿Cuál es el nombre de tu primera mascota?",
    "¿En qué ciudad naciste?",
    "¿Cuál es el nombre de tu madre?",
    "¿Cuál es tu película favorita?",
]

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

        nombre_usuario      = request.form.get("nombre_usuario", "").strip()
        nombre_real         = request.form.get("nombre", "").strip()
        apellidos           = request.form.get("apellidos", "").strip()
        email               = request.form.get("email", "").strip().lower()
        password            = request.form.get("password", "")
        confirmar_password  = request.form.get("confirmar_password", "")
        pregunta_seguridad  = request.form.get("pregunta_seguridad", "").strip()
        respuesta_seguridad = request.form.get("respuesta_seguridad", "").strip()

        def _render_registro():
            return render_template("auth/registro.html", preguntas=PREGUNTAS_SEGURIDAD)

        if not all([nombre_usuario, nombre_real, apellidos, email, password,
                    confirmar_password, pregunta_seguridad, respuesta_seguridad]):
            flash("Todos los campos son obligatorios.", "danger")
            return _render_registro()

        if "@" not in email:
            flash("Introduce un email válido.", "danger")
            return _render_registro()

        if password != confirmar_password:
            flash("Las contraseñas no coinciden.", "danger")
            return _render_registro()

        error_pwd = validar_password_fuerte(password)
        if error_pwd:
            flash(error_pwd, "danger")
            return _render_registro()

        resultado = modelo.crear(
            nombre_usuario, email, password,
            nombre_real=nombre_real,
            apellidos=apellidos,
            pregunta_seguridad=pregunta_seguridad,
            respuesta_seguridad=respuesta_seguridad,
        )
        if resultado is None:
            flash("El email ya está registrado.", "danger")
            return _render_registro()
        if resultado == "nombre_duplicado":
            flash("Ese nombre de usuario ya está en uso. Elige otro.", "danger")
            return _render_registro()

        registrar_log(db, "registro", "crear_usuario", nombre_usuario, f"Email: {email}")
        actualizar_contadores(db)

        flash(
            "Solicitud recibida. Tu cuenta está pendiente de validación por el administrador. "
            "Este proceso puede durar unas horas.",
            "info",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/registro.html", preguntas=PREGUNTAS_SEGURIDAD)


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
            candidato = db.usuarios.find_one({
                "nombre": {"$regex": f"^{nombre_login}$", "$options": "i"}
            })
            if candidato and candidato.get("activo") and not candidato.get("validado"):
                flash("Tu cuenta está pendiente de validación por el administrador.", "warning")
            else:
                flash("Usuario o contraseña incorrectos.", "danger")
            return render_template("auth/login.html")

        # ── Construir la sesion Flask ─────────────────────────────────────────
        # Solo se guardan los datos necesarios en la cookie de sesion (firmada con SECRET_KEY)
        session["user_id"]    = str(usuario["_id"])
        session["nombre"]     = usuario["nombre"]
        session["rol"]        = usuario["rol"]
        session["foto_perfil"] = usuario.get("foto_perfil")

        # Primer acceso: cuenta creada por admin sin pregunta de seguridad
        if usuario.get("debe_cambiar_password") and not usuario.get("pregunta_seguridad"):
            flash("Completa la configuración inicial de tu cuenta.", "info")
            return redirect(url_for("auth.primer_acceso"))

        # Contraseña reseteada: solo cambiar contraseña (ya tiene pregunta de seguridad)
        if usuario.get("debe_cambiar_password"):
            flash("Tu contraseña fue restablecida. Cámbiala antes de continuar.", "warning")
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
            flash("Las contraseñas nuevas no coinciden.", "danger")
            return render_template("auth/cambiar_password.html")

        error_pwd = validar_password_fuerte(nueva)
        if error_pwd:
            flash(error_pwd, "danger")
            return render_template("auth/cambiar_password.html")

        # Persistir el nuevo hash y desactivar el flag de cambio obligatorio
        modelo.cambiar_password(session["user_id"], nueva)
        registrar_log(db, "registro", "cambiar_password", session["nombre"])
        flash("Contrasenia cambiada correctamente.", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/cambiar_password.html")


# ── Primer acceso (cuenta creada por admin) ──────────────────────────────────

@auth_bp.route("/primer-acceso", methods=["GET", "POST"])
@login_required
def primer_acceso():
    """
    Flujo de primer acceso para cuentas creadas por el administrador.
    El usuario debe: 1) elegir una contraseña segura  2) configurar pregunta de seguridad.
    """
    db     = get_db()
    modelo = Usuario(db)

    # Si ya completó la configuración, no debe volver aquí
    usuario = modelo.obtener_por_id(session["user_id"])
    if not usuario or (not usuario.get("debe_cambiar_password") and usuario.get("pregunta_seguridad")):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        nueva              = request.form.get("nueva_password", "")
        confirmar          = request.form.get("confirmar_password", "")
        pregunta_seguridad = request.form.get("pregunta_seguridad", "").strip()
        respuesta_seguridad = request.form.get("respuesta_seguridad", "").strip()

        if nueva != confirmar:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("auth/primer_acceso.html", preguntas=PREGUNTAS_SEGURIDAD)

        error_pwd = validar_password_fuerte(nueva)
        if error_pwd:
            flash(error_pwd, "danger")
            return render_template("auth/primer_acceso.html", preguntas=PREGUNTAS_SEGURIDAD)

        if not pregunta_seguridad or not respuesta_seguridad:
            flash("La pregunta y la respuesta de seguridad son obligatorias.", "danger")
            return render_template("auth/primer_acceso.html", preguntas=PREGUNTAS_SEGURIDAD)

        modelo.cambiar_password(session["user_id"], nueva)
        modelo.configurar_seguridad(session["user_id"], pregunta_seguridad, respuesta_seguridad)
        registrar_log(db, "registro", "primer_acceso", session["nombre"])

        flash(f"¡Bienvenido, {session['nombre']}! Tu cuenta está lista.", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/primer_acceso.html", preguntas=PREGUNTAS_SEGURIDAD)


# ── Simulación de rol ────────────────────────────────────────────────────────

@auth_bp.route("/simular-rol/<rol>")
@login_required
def simular_rol(rol):
    """Permite al admin o gestor elegir temporalmente otro rol."""
    roles_validos = ("admin", "gestor", "usuario")

    rol_real = session.get("rol_real") or session.get("rol")
    if rol_real not in ("admin", "gestor"):
        flash("No tienes permiso para cambiar de rol.", "danger")
        return redirect(url_for("main.index"))

    # El gestor solo puede moverse entre gestor y usuario
    if rol_real == "gestor" and rol not in ("gestor", "usuario"):
        flash("Solo puedes cambiar al rol de usuario.", "danger")
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

    user_id = session["user_id"]
    mis_anuncios = {
        "viviendas":   list(db.viviendas.find({"usuario_id": user_id}).sort("fecha_creacion", -1)),
        "servicios":   list(db.servicios.find({"usuario_id": user_id}).sort("fecha_creacion", -1)),
        "compraventa": list(db.compraventa.find({"usuario_id": user_id}).sort("fecha_creacion", -1)),
        "ocio":        list(db.ocio.find({"usuario_id": user_id}).sort("fecha_creacion", -1)),
    }
    return render_template("auth/perfil.html", usuario=usuario, mis_anuncios=mis_anuncios)


# ── Recuperacion de cuenta ────────────────────────────────────────────────────

@auth_bp.route("/recuperar", methods=["GET", "POST"])
def recuperar_password():
    """
    Recuperacion de cuenta en tres pasos:
      1. Introduce el ID de usuario
      2. Se muestra la pregunta de seguridad y se pide la respuesta
      3. Si la respuesta es correcta, se permite cambiar la contraseña
    """
    if request.method == "GET":
        session.pop("rec_nombre", None)
        session.pop("rec_verificado", None)
        return render_template("auth/recuperar.html", paso=1)

    db    = get_db()
    modelo = Usuario(db)
    paso   = request.form.get("paso", "1")

    if paso == "1":
        nombre_rec = request.form.get("nombre", "").strip()
        usuario = db.usuarios.find_one({"nombre": nombre_rec})
        if not usuario or not usuario.get("pregunta_seguridad"):
            flash("ID de usuario no encontrado o sin pregunta de seguridad configurada.", "danger")
            return render_template("auth/recuperar.html", paso=1)
        session["rec_nombre"] = nombre_rec
        return render_template("auth/recuperar.html", paso=2, pregunta=usuario["pregunta_seguridad"])

    if paso == "2":
        nombre_rec = session.get("rec_nombre")
        if not nombre_rec:
            return redirect(url_for("auth.recuperar_password"))
        respuesta = request.form.get("respuesta_seguridad", "").strip()
        if not modelo.verificar_respuesta_seguridad(nombre_rec, respuesta):
            flash("Respuesta de seguridad incorrecta.", "danger")
            usuario = db.usuarios.find_one({"nombre": nombre_rec})
            return render_template("auth/recuperar.html", paso=2, pregunta=usuario["pregunta_seguridad"])
        session["rec_verificado"] = True
        return render_template("auth/recuperar.html", paso=3)

    if paso == "3":
        nombre_rec = session.get("rec_nombre")
        if not nombre_rec or not session.get("rec_verificado"):
            return redirect(url_for("auth.recuperar_password"))
        nueva     = request.form.get("nueva_password", "")
        confirmar = request.form.get("confirmar_password", "")
        if nueva != confirmar:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("auth/recuperar.html", paso=3)
        error_pwd = validar_password_fuerte(nueva)
        if error_pwd:
            flash(error_pwd, "danger")
            return render_template("auth/recuperar.html", paso=3)
        usuario = db.usuarios.find_one({"nombre": nombre_rec})
        if usuario:
            modelo.cambiar_password(str(usuario["_id"]), nueva)
            session.pop("rec_nombre", None)
            session.pop("rec_verificado", None)
            flash("Contraseña recuperada correctamente. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))

    return redirect(url_for("auth.recuperar_password"))
