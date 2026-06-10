"""
routes/admin.py - Panel de administracion de FAMA.

Rutas protegidas por rol:
  - gestor_required: panel, listar/editar usuarios, resetear contraseña.
  - admin_required : cambiar rol, eliminar usuario, ver/eliminar/exportar logs.

Jerarquia de roles: admin > gestor > usuario
"""
import os
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, session, url_for

from models.usuario import Usuario
from utils.db import get_db
from utils.decorators import admin_required, gestor_required, login_required
from utils.logs import exportar_logs_pdf, registrar_log
from utils.validators import validar_password_fuerte

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def desactivar_admin_bootstrap(db, ignore_user_id=None):
    """Desactiva el admin creado por defecto por scripts/crear_admin.py si existe."""
    usuario_bootstrap = Usuario(db).obtener_por_email("admin@appfama.es")
    if not usuario_bootstrap:
        return False
    if usuario_bootstrap.get("rol") != "admin" or not usuario_bootstrap.get("activo", False):
        return False
    if ignore_user_id and usuario_bootstrap["_id"] == ObjectId(ignore_user_id):
        return False
    Usuario(db).eliminar(usuario_bootstrap["_id"])
    return True


# ── Panel principal ───────────────────────────────────────────────────────────

@admin_bp.route("/")
@login_required
@gestor_required  # Gestores y admins pueden ver el panel
def panel():
    """Muestra estadisticas globales y accesos rapidos a las secciones de admin."""
    db = get_db()

    # Contar documentos en cada coleccion para las tarjetas de estadisticas
    stats = {
        "usuarios":    db.usuarios.count_documents({"activo": True, "validado": True}),
        "pendientes":  db.usuarios.count_documents({"activo": True, "validado": False}),
        "viviendas":   db.viviendas.count_documents({}),
        "servicios":   db.servicios.count_documents({}),
        "compraventa": db.compraventa.count_documents({}),
        "ocio":        db.ocio.count_documents({}),
    }
    # Calcular el total de anuncios como suma de todos los módulos
    stats["total_anuncios"] = (
        stats["viviendas"] + stats["servicios"] + stats["compraventa"] + stats["ocio"]
    )
    return render_template("admin/panel.html", stats=stats)


# ── Gestión de usuarios ───────────────────────────────────────────────────────

@admin_bp.route("/usuarios")
@login_required
@gestor_required
def listar_usuarios():
    """Lista usuarios con buscador y paginacion configurable."""
    db        = get_db()
    q         = request.args.get("q", "").strip()
    pagina    = max(1, int(request.args.get("pagina", 1)))
    por_pagina = int(request.args.get("por_pagina", 10))
    if por_pagina not in (10, 25, 50, 100):
        por_pagina = 10

    filtro = {}
    if q:
        filtro["$or"] = [
            {"nombre": {"$regex": q, "$options": "i"}},
            {"email":  {"$regex": q, "$options": "i"}},
        ]

    total        = db.usuarios.count_documents(filtro)
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    pagina        = min(pagina, total_paginas)

    usuarios = list(
        db.usuarios.find(filtro)
        .sort("fecha_registro", -1)
        .skip((pagina - 1) * por_pagina)
        .limit(por_pagina)
    )

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios,
        q=q,
        pagina=pagina,
        total_paginas=total_paginas,
        total=total,
        por_pagina=por_pagina,
    )


@admin_bp.route("/usuarios/crear", methods=["POST"])
@login_required
@admin_required
def crear_usuario():
    """Crea un usuario directamente desde el panel admin (ya validado)."""
    db = get_db()
    modelo = Usuario(db)

    nombre_usuario     = request.form.get("nombre_usuario", "").strip()
    nombre_real        = request.form.get("nombre", "").strip()
    apellidos          = request.form.get("apellidos", "").strip()
    email              = request.form.get("email", "").strip().lower()
    password           = request.form.get("password", "")
    confirmar_password = request.form.get("confirmar_password", "")

    if not all([nombre_usuario, nombre_real, apellidos, email, password, confirmar_password]):
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    if "@" not in email:
        flash("Introduce un email válido.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    if password != confirmar_password:
        flash("Las contraseñas no coinciden.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    error_pwd = validar_password_fuerte(password)
    if error_pwd:
        flash(error_pwd, "danger")
        return redirect(url_for("admin.listar_usuarios"))

    resultado = modelo.crear(
        nombre_usuario, email, password,
        nombre_real=nombre_real,
        apellidos=apellidos,
        validado=True,
    )

    if resultado is None:
        flash("El email ya está registrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))
    if resultado == "nombre_duplicado":
        flash("Ese ID de usuario ya está en uso.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    # Forzar cambio de contraseña en el primer inicio de sesión
    modelo.actualizar(str(resultado), {"debe_cambiar_password": True})

    registrar_log(db, "registro", "crear_usuario_admin", session["nombre"],
                  f"Usuario creado por admin: {nombre_usuario}")
    flash(f"Usuario {nombre_usuario} creado. Se le pedirá cambiar la contraseña al entrar.", "success")
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/usuarios/reportar/<user_id>", methods=["POST"])
@login_required
@gestor_required
def reportar_usuario(user_id):
    """El gestor reporta a un usuario al administrador."""
    db = get_db()
    usuario = Usuario(db).obtener_por_id(user_id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    motivo = request.form.get("motivo", "").strip()
    if not motivo:
        flash("Debes indicar el motivo del reporte.", "danger")
        return redirect(url_for("admin.ver_usuario", user_id=user_id))

    db.reportes.insert_one({
        "tipo_reporte":    "usuario",
        "usuario_id":      user_id,
        "usuario_nombre":  usuario["nombre"],
        "motivo":          motivo,
        "gestor_id":       session["user_id"],
        "gestor_nombre":   session["nombre"],
        "fecha":           datetime.now(),
        "resuelto":        False,
    })
    registrar_log(db, "registro", "reportar_usuario", session["nombre"],
                  f"Usuario reportado: {usuario['nombre']}")
    flash("Usuario reportado al administrador.", "warning")
    return redirect(url_for("admin.ver_usuario", user_id=user_id))


@admin_bp.route("/usuarios/ver/<user_id>")
@login_required
@gestor_required
def ver_usuario(user_id):
    """Muestra la ficha completa de un usuario."""
    db      = get_db()
    usuario = Usuario(db).obtener_por_id(user_id)
    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))
    return render_template("admin/ver_usuario.html", usuario=usuario)


@admin_bp.route("/usuarios/editar/<user_id>", methods=["GET", "POST"])
@login_required
@gestor_required  # Tanto gestor como admin pueden editar nombre/email
def editar_usuario(user_id):
    """Edita datos basicos de un usuario. Solo admin puede cambiar el rol desde aqui."""
    db = get_db()
    modelo = Usuario(db)
    usuario = modelo.obtener_por_id(user_id)

    # Verificar que el usuario existe antes de mostrar el formulario
    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    if request.method == "POST":
        # Borrar foto de perfil si se solicitó
        if "borrar_foto" in request.form and usuario.get("foto_perfil"):
            ruta = os.path.join(current_app.static_folder, "uploads", "perfiles", usuario["foto_perfil"])
            if os.path.exists(ruta):
                os.remove(ruta)
            modelo.actualizar(user_id, {"foto_perfil": None})
            registrar_log(db, "registro", "borrar_foto_perfil", session["nombre"],
                          f"Foto de perfil eliminada del usuario: {usuario['nombre']}")
            flash("Foto de perfil eliminada.", "success")
            return redirect(url_for("admin.editar_usuario", user_id=user_id))

        # Campos editables por gestor: nombre y email
        datos = {
            "nombre": request.form.get("nombre", "").strip(),
            "email":  request.form.get("email", "").strip().lower(),
        }
        # El campo 'rol' solo se procesa si el usuario actual es admin
        # (el formulario muestra el select de rol solo si session.rol=='admin')
        if session.get("rol") == "admin":
            datos["rol"] = request.form.get("rol", "usuario")

        modelo.actualizar(user_id, datos)
        registrar_log(db, "registro", "editar_usuario", session["nombre"],
                      f"Usuario editado: {datos['nombre']}")
        if datos.get("rol") == "admin":
            desactivado = desactivar_admin_bootstrap(db, ignore_user_id=user_id)
            if desactivado:
                flash("Usuario actualizado. El administrador bootstrap por defecto ha sido desactivado.", "success")
            else:
                flash("Usuario actualizado.", "success")
        else:
            flash("Usuario actualizado.", "success")
        return redirect(url_for("admin.listar_usuarios"))

    # GET: mostrar el formulario con los datos actuales del usuario
    return render_template("admin/editar_usuario.html", usuario=usuario)


@admin_bp.route("/usuarios/rol/<user_id>", methods=["POST"])
@login_required
@admin_required  # Solo admin puede cambiar roles directamente desde la tabla
def cambiar_rol(user_id):
    """Cambia el rol de un usuario desde el dropdown de la tabla de usuarios."""
    db = get_db()
    modelo = Usuario(db)
    nuevo_rol = request.form.get("rol")
    usuario   = modelo.obtener_por_id(user_id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    modelo.cambiar_rol(user_id, nuevo_rol)
    registrar_log(db, "registro", "cambiar_rol", session["nombre"],
                  f"Usuario: {usuario['nombre']} -> Nuevo rol: {nuevo_rol}")

    if nuevo_rol == "admin":
        desactivado = desactivar_admin_bootstrap(db, ignore_user_id=user_id)
        if desactivado:
            flash("Rol actualizado a 'admin'. El administrador bootstrap por defecto ha sido desactivado.", "success")
        else:
            flash(f"Rol actualizado a '{nuevo_rol}' para {usuario['nombre']}", "success")
        return redirect(url_for("admin.listar_usuarios"))

    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/usuarios/validar/<user_id>", methods=["POST"])
@login_required
@gestor_required
def validar_usuario(user_id):
    """Aprueba la cuenta de un usuario pendiente de validación."""
    db = get_db()
    modelo  = Usuario(db)
    usuario = modelo.obtener_por_id(user_id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    modelo.validar_usuario(user_id)
    registrar_log(db, "registro", "validar_usuario", session["nombre"],
                  f"Cuenta validada: {usuario['nombre']}")
    flash(f"Cuenta de {usuario['nombre']} aprobada.", "success")
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/usuarios/resetear/<user_id>", methods=["POST"])
@login_required
@gestor_required  # Gestores pueden resetear contraseñas de usuarios normales
def resetear_password(user_id):
    """Resetea la contraseña del usuario a 'fama1234' y obliga a cambiarla en el próximo login."""
    db = get_db()
    modelo  = Usuario(db)
    usuario = modelo.obtener_por_id(user_id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    modelo.resetear_password(user_id)
    registrar_log(db, "registro", "resetear_password", session["nombre"],
                  f"Contrasenia reseteada para: {usuario['nombre']}")
    flash(f"Contraseña de {usuario['nombre']} reseteada a 'fama1234'.", "success")
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/usuarios/reactivar/<user_id>", methods=["POST"])
@login_required
@admin_required
def reactivar_usuario(user_id):
    """Reactiva una cuenta previamente desactivada."""
    db = get_db()
    modelo  = Usuario(db)
    usuario = modelo.obtener_por_id(user_id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    modelo.reactivar(user_id)
    registrar_log(db, "registro", "reactivar_usuario", session["nombre"],
                  f"Usuario reactivado: {usuario['nombre']}")
    flash(f"Usuario {usuario['nombre']} reactivado.", "success")
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/usuarios/eliminar-definitivo/<user_id>", methods=["POST"])
@login_required
@admin_required
def eliminar_definitivo_usuario(user_id):
    """Elimina un usuario de forma permanente e irreversible."""
    db = get_db()
    modelo  = Usuario(db)
    usuario = modelo.obtener_por_id(user_id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    modelo.eliminar_definitivo(user_id)
    registrar_log(db, "registro", "eliminar_definitivo_usuario", session["nombre"],
                  f"Usuario eliminado permanentemente: {usuario['nombre']}")
    flash(f"Usuario {usuario['nombre']} eliminado permanentemente.", "info")
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/usuarios/eliminar/<user_id>", methods=["POST"])
@login_required
@admin_required  # Solo admin puede desactivar cuentas
def eliminar_usuario(user_id):
    """
    Desactiva (soft-delete) un usuario.
    Protege al administrador principal para evitar quedar sin acceso.
    """
    db = get_db()
    modelo  = Usuario(db)
    usuario = modelo.obtener_por_id(user_id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    if str(usuario["_id"]) == session["user_id"]:
        flash("No puedes eliminarte a ti mismo.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    if usuario.get("rol") == "admin":
        num_admins = db.usuarios.count_documents({"rol": "admin", "activo": True})
        if num_admins <= 1:
            flash("No puedes eliminar al único administrador activo.", "danger")
            return redirect(url_for("admin.listar_usuarios"))

    # Soft-delete: pone activo=False, no borra el documento ni el historial
    modelo.eliminar(user_id)
    registrar_log(db, "registro", "eliminar_usuario", session["nombre"],
                  f"Usuario eliminado: {usuario['nombre']}")
    flash(f"Usuario {usuario['nombre']} desactivado.", "info")
    return redirect(url_for("admin.listar_usuarios"))


# ── Gestión de logs ───────────────────────────────────────────────────────────

@admin_bp.route("/logs")
@login_required
@admin_required  # Los logs son sensibles; solo admin puede verlos
def ver_logs():
    """
    Muestra la tabla de logs con filtrado opcional por tipo ('registro' o 'control').
    El parametro GET 'tipo' viene del selector de pestanas en la vista.
    """
    db        = get_db()
    tipo      = request.args.get("tipo", "")
    pagina    = max(1, int(request.args.get("pagina", 1)))
    por_pagina = int(request.args.get("por_pagina", 10))
    if por_pagina not in (10, 25, 50, 100):
        por_pagina = 10

    query = {"tipo": tipo} if tipo else {}
    total        = db.logs.count_documents(query)
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    pagina        = min(pagina, total_paginas)

    logs = list(
        db.logs.find(query)
        .sort("fecha", -1)
        .skip((pagina - 1) * por_pagina)
        .limit(por_pagina)
    )
    return render_template(
        "admin/logs.html",
        logs=logs,
        tipo_filtro=tipo,
        pagina=pagina,
        total_paginas=total_paginas,
        total=total,
        por_pagina=por_pagina,
    )


@admin_bp.route("/logs/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_logs():
    """
    Elimina los logs cuyos IDs llegaron marcados con checkbox en el formulario.
    delete_many() con $in borra todos de una sola operacion MongoDB.
    """
    db  = get_db()
    ids = request.form.getlist("log_ids")  # Lista de strings con los ObjectId seleccionados

    if not ids:
        flash("No seleccionaste ningun log.", "warning")
        return redirect(url_for("admin.ver_logs"))

    # Convertir strings a ObjectId para la query de MongoDB
    object_ids = [ObjectId(i) for i in ids if i]
    resultado  = db.logs.delete_many({"_id": {"$in": object_ids}})
    flash(f"{resultado.deleted_count} log(s) eliminado(s).", "info")
    return redirect(url_for("admin.ver_logs"))


@admin_bp.route("/logs/exportar")
@login_required
@admin_required
def exportar_logs():
    """
    Genera un PDF con los logs visibles (respetando el filtro de tipo activo)
    y lo devuelve como archivo descargable.
    """
    db    = get_db()
    tipo  = request.args.get("tipo", "")
    query = {"tipo": tipo} if tipo else {}
    logs  = list(db.logs.find(query).sort("fecha", -1))

    titulo = f"Logs FAMA - {tipo.capitalize() if tipo else 'Todos'}"
    # exportar_logs_pdf() devuelve un BytesIO listo para send_file
    buffer = exportar_logs_pdf(logs, titulo)

    return send_file(
        buffer,
        mimetype="application/pdf",
        download_name=f"logs_fama_{tipo or 'todos'}.pdf",
        as_attachment=True,
    )


# ── Reportes de anuncios ──────────────────────────────────────────────────────

@admin_bp.route("/reportes")
@login_required
@gestor_required
def ver_reportes():
    """Lista reportes con paginacion configurable."""
    db        = get_db()
    pagina    = max(1, int(request.args.get("pagina", 1)))
    por_pagina = int(request.args.get("por_pagina", 10))
    if por_pagina not in (10, 25, 50, 100):
        por_pagina = 10

    total        = db.reportes.count_documents({})
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    pagina        = min(pagina, total_paginas)

    reportes = list(
        db.reportes.find()
        .sort("fecha", -1)
        .skip((pagina - 1) * por_pagina)
        .limit(por_pagina)
    )
    return render_template(
        "admin/reportes.html",
        reportes=reportes,
        pagina=pagina,
        total_paginas=total_paginas,
        total=total,
        por_pagina=por_pagina,
    )


@admin_bp.route("/reportes/nuevo", methods=["POST"])
@login_required
@gestor_required
def crear_reporte():
    """Crea un reporte sobre un anuncio y lo almacena para revisión de los admins."""
    db      = get_db()
    anuncio_id  = request.form.get("anuncio_id")
    tipo_modulo = request.form.get("tipo_modulo")
    motivo      = request.form.get("motivo", "").strip()

    if not motivo:
        flash("Debes indicar el motivo del reporte.", "danger")
        return redirect(request.referrer or url_for("main.index"))

    db.reportes.insert_one({
        "anuncio_id":  anuncio_id,
        "tipo_modulo": tipo_modulo,
        "motivo":      motivo,
        "gestor_id":   session["user_id"],
        "gestor_nombre": session["nombre"],
        "fecha":       datetime.now(),
        "resuelto":    False,
    })
    flash("Reporte enviado a los administradores.", "success")
    return redirect(request.referrer or url_for("main.index"))


@admin_bp.route("/reportes/resolver/<reporte_id>", methods=["POST"])
@login_required
@admin_required
def resolver_reporte(reporte_id):
    """Marca un reporte como resuelto."""
    db = get_db()
    db.reportes.update_one({"_id": ObjectId(reporte_id)}, {"$set": {"resuelto": True}})
    flash("Reporte marcado como resuelto.", "success")
    return redirect(url_for("admin.ver_reportes"))


@admin_bp.route("/reportes/eliminar/<reporte_id>", methods=["POST"])
@login_required
@admin_required
def eliminar_reporte(reporte_id):
    """Elimina un reporte definitivamente."""
    db = get_db()
    db.reportes.delete_one({"_id": ObjectId(reporte_id)})
    flash("Reporte eliminado.", "info")
    return redirect(url_for("admin.ver_reportes"))


# ── Manual de administrador ───────────────────────────────────────────────────

_CARPETA_MANUAL = None

def _carpeta_manual():
    carpeta = os.path.join(current_app.static_folder, "uploads", "manual")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


@admin_bp.route("/manual")
@login_required
@gestor_required
def manual():
    """Muestra el manual de administrador con los PDFs subidos."""
    carpeta = _carpeta_manual()
    archivos = sorted(
        f for f in os.listdir(carpeta) if f.lower().endswith(".pdf")
    )
    return render_template("admin/manual.html", archivos=archivos)


@admin_bp.route("/manual/subir", methods=["POST"])
@login_required
@admin_required
def manual_subir():
    """Solo el admin puede subir PDFs al manual."""
    archivo = request.files.get("pdf")
    if not archivo or archivo.filename == "":
        flash("Selecciona un archivo PDF.", "danger")
        return redirect(url_for("admin.manual"))
    if not archivo.filename.lower().endswith(".pdf"):
        flash("Solo se permiten archivos PDF.", "danger")
        return redirect(url_for("admin.manual"))
    from werkzeug.utils import secure_filename
    nombre = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secure_filename(archivo.filename)}"
    archivo.save(os.path.join(_carpeta_manual(), nombre))
    flash("Documento subido correctamente.", "success")
    return redirect(url_for("admin.manual"))


@admin_bp.route("/manual/eliminar/<nombre>", methods=["POST"])
@login_required
@admin_required
def manual_eliminar(nombre):
    """Solo el admin puede eliminar PDFs del manual."""
    from werkzeug.utils import secure_filename
    ruta = os.path.join(_carpeta_manual(), secure_filename(nombre))
    if os.path.exists(ruta):
        os.remove(ruta)
        flash("Documento eliminado.", "info")
    return redirect(url_for("admin.manual"))


# ── Test de conexión a base de datos ─────────────────────────────────────────

@admin_bp.route("/test-bd")
@login_required
@admin_required
def test_bd():
    """Comprueba la conexión a MongoDB y redirige al panel con el resultado."""
    db = get_db()
    try:
        db.command("ping")
        flash("Conexión a la base de datos: OK.", "success")
    except Exception as exc:
        flash(f"Error de conexión a la base de datos: {exc}", "danger")
    return redirect(url_for("admin.panel"))
