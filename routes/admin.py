"""
routes/admin.py - Panel de administracion de FAMA.

Rutas protegidas por rol:
  - gestor_required: panel, listar/editar usuarios, resetear contrasenia.
  - admin_required : cambiar rol, eliminar usuario, ver/eliminar/exportar logs.

Jerarquia de roles: admin > gestor > usuario
"""
from bson import ObjectId
from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for

from models.usuario import Usuario
from utils.db import get_db
from utils.decorators import admin_required, gestor_required, login_required
from utils.email import enviar_aprobacion_cuenta
from utils.logs import exportar_logs_pdf, registrar_log

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ── Panel principal ───────────────────────────────────────────────────────────

@admin_bp.route("/")
@login_required
@gestor_required  # Gestores y admins pueden ver el panel
def panel():
    """Muestra estadisticas globales y accesos rapidos a las secciones de admin."""
    db = get_db()

    # Contar documentos en cada coleccion para las tarjetas de estadisticas
    stats = {
        "usuarios":    db.usuarios.count_documents({"activo": True, "validado": True, "email_verificado": True}),
        # Pendientes = email verificado pero aun sin aprobar por admin
        "pendientes":  db.usuarios.count_documents({"activo": True, "email_verificado": True, "validado": False}),
        "viviendas":   db.viviendas.count_documents({}),
        "servicios":   db.servicios.count_documents({}),
        "compraventa": db.compraventa.count_documents({}),
        "ocio":        db.ocio.count_documents({}),
    }
    # Calcular el total de anuncios como suma de todos los modulos
    stats["total_anuncios"] = (
        stats["viviendas"] + stats["servicios"] + stats["compraventa"] + stats["ocio"]
    )
    return render_template("admin/panel.html", stats=stats)


# ── Gestion de usuarios ───────────────────────────────────────────────────────

@admin_bp.route("/usuarios")
@login_required
@gestor_required
def listar_usuarios():
    """Lista usuarios con buscador y paginacion de 10 en 10."""
    db        = get_db()
    q         = request.args.get("q", "").strip()
    pagina    = max(1, int(request.args.get("pagina", 1)))
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
    )


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

    # cambiar_rol() valida que nuevo_rol este en ROLES_VALIDOS antes de persistir
    modelo.cambiar_rol(user_id, nuevo_rol)
    registrar_log(db, "registro", "cambiar_rol", session["nombre"],
                  f"Usuario: {usuario['nombre']} -> Nuevo rol: {nuevo_rol}")
    flash(f"Rol actualizado a '{nuevo_rol}' para {usuario['nombre']}.", "success")
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/usuarios/validar/<user_id>", methods=["POST"])
@login_required
@gestor_required
def validar_usuario(user_id):
    """Aprueba la cuenta de un usuario pendiente de validacion."""
    db = get_db()
    modelo  = Usuario(db)
    usuario = modelo.obtener_por_id(user_id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    password_temp = Usuario.generar_password_temporal()
    modelo.validar_usuario(user_id)
    modelo.establecer_password_temporal(user_id, password_temp)
    enviado = enviar_aprobacion_cuenta(usuario["email"], usuario["nombre"], password_temp)

    registrar_log(db, "registro", "validar_usuario", session["nombre"],
                  f"Cuenta validada: {usuario['nombre']}")

    if enviado:
        flash(f"Cuenta de {usuario['nombre']} aprobada. Se le ha enviado la contrasena temporal por email.", "success")
    else:
        flash(f"Cuenta de {usuario['nombre']} aprobada pero el email no pudo enviarse. Contrasena temporal: {password_temp}", "warning")
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/usuarios/resetear/<user_id>", methods=["POST"])
@login_required
@gestor_required  # Gestores pueden resetear contrasenias de usuarios normales
def resetear_password(user_id):
    """
    Pone la contrasenia del usuario a 'Password' y activa el flag
    'debe_cambiar_password' para que cambie en su proximo login.
    """
    db = get_db()
    modelo  = Usuario(db)
    usuario = modelo.obtener_por_id(user_id)

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    modelo.resetear_password(user_id)
    registrar_log(db, "registro", "resetear_password", session["nombre"],
                  f"Contrasenia reseteada para: {usuario['nombre']}")
    flash(f"Contrasenia de {usuario['nombre']} reseteada a 'Password'.", "success")
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

    # Proteccion: no se puede desactivar al admin que esta realizando la accion
    # ni a ninguna cuenta con rol 'admin' cuyo ID coincida con el user_id recibido
    if str(usuario["_id"]) == user_id and usuario.get("rol") == "admin":
        flash("No puedes eliminar al administrador principal.", "danger")
        return redirect(url_for("admin.listar_usuarios"))

    # Soft-delete: pone activo=False, no borra el documento ni el historial
    modelo.eliminar(user_id)
    registrar_log(db, "registro", "eliminar_usuario", session["nombre"],
                  f"Usuario eliminado: {usuario['nombre']}")
    flash(f"Usuario {usuario['nombre']} desactivado.", "info")
    return redirect(url_for("admin.listar_usuarios"))


# ── Gestion de logs ───────────────────────────────────────────────────────────

@admin_bp.route("/logs")
@login_required
@admin_required  # Los logs son sensibles; solo admin puede verlos
def ver_logs():
    """
    Muestra la tabla de logs con filtrado opcional por tipo ('registro' o 'control').
    El parametro GET 'tipo' viene del selector de pestanas en la vista.
    """
    db   = get_db()
    tipo  = request.args.get("tipo", "")
    # Si se especifica tipo, filtrar; si no, mostrar todos los logs
    query = {"tipo": tipo} if tipo else {}
    logs  = list(db.logs.find(query).sort("fecha", -1))  # Mas recientes primero
    return render_template("admin/logs.html", logs=logs, tipo_filtro=tipo)


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
        as_attachment=True,  # Fuerza la descarga en lugar de mostrar en el navegador
    )
