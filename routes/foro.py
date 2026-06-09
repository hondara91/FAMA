"""
routes/foro.py - Rutas del módulo de Foro (canales + posts + respuestas).

  GET  /foro/                          -> lista de canales
  GET/POST /foro/canal/nuevo           -> crear canal (gestor/admin)
  POST /foro/canal/eliminar/<id>       -> eliminar canal (admin)
  GET  /foro/canal/<canal_id>          -> posts dentro de un canal
  GET/POST /foro/canal/<canal_id>/nuevo-> crear post en el canal
  GET  /foro/detalle/<post_id>         -> post + hilo de respuestas
  POST /foro/detalle/<post_id>         -> nueva respuesta
  GET/POST /foro/editar/<post_id>      -> editar post
  POST /foro/eliminar/<post_id>        -> eliminar post
  POST /foro/respuesta/eliminar/<id>   -> eliminar respuesta
"""
from bson import ObjectId
from flask import (Blueprint, flash, redirect,
                   render_template, request, session, url_for)

from models.foro import ForoCanal, ForoPost, ForoRespuesta
from utils.db import get_db
from utils.decorators import gestor_required, login_required
from utils.logs import registrar_log
from utils.uploads import eliminar_imagenes, guardar_imagenes

foro_bp = Blueprint("foro", __name__, url_prefix="/foro")


def _fotos_doc(doc):
    """Devuelve la lista de fotos de un post/respuesta unificando campo nuevo y legado."""
    fotos = list(doc.get("fotos") or [])
    if doc.get("imagen"):
        fotos.insert(0, doc["imagen"])
    return fotos


def _anotar_fotos_autor(db, documentos):
    """Anade foto_autor a posts/respuestas resolviendo el usuario actual."""
    ids = []
    for doc in documentos:
        try:
            ids.append(ObjectId(doc.get("usuario_id")))
        except Exception:
            pass

    usuarios = {
        str(u["_id"]): u.get("foto_perfil")
        for u in db.usuarios.find({"_id": {"$in": ids}}, {"foto_perfil": 1})
    } if ids else {}

    for doc in documentos:
        doc["foto_autor"] = usuarios.get(doc.get("usuario_id"))


# ── Lista de canales ──────────────────────────────────────────────────────────

@foro_bp.route("/")
@login_required
def listar():
    """Página principal del foro: muestra todos los canales disponibles."""
    import math
    PER_PAGE = 12
    db     = get_db()
    modelo = ForoCanal(db)
    posts  = ForoPost(db)
    total  = modelo.contar()
    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
    total_paginas = max(1, math.ceil(total / PER_PAGE))
    page = min(page, total_paginas)
    canales = modelo.obtener_todos(skip=(page - 1) * PER_PAGE, limit=PER_PAGE)
    for c in canales:
        c["num_posts"] = posts.contar_por_canal(str(c["_id"]))
    return render_template("foro/listar.html", canales=canales, page=page, total_paginas=total_paginas)


# ── Crear canal ───────────────────────────────────────────────────────────────

@foro_bp.route("/canal/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_canal():
    """Formulario para crear un nuevo canal (cualquier usuario autenticado)."""
    if request.method == "POST":
        db     = get_db()
        modelo = ForoCanal(db)

        nombre      = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        color       = request.form.get("color", "primary")
        icono       = request.form.get("icono", "chat-dots")

        if not nombre:
            flash("El nombre del canal es obligatorio.", "danger")
            return render_template("foro/nuevo_canal.html", colores=ForoCanal.COLORES, iconos=ForoCanal.ICONOS)

        modelo.crear(nombre, descripcion, color, icono, session["user_id"], session["nombre"])
        registrar_log(db, "registro", "crear_canal_foro", session["nombre"], f"Canal: {nombre}")
        flash(f"Canal '{nombre}' creado correctamente.", "success")
        return redirect(url_for("foro.listar"))

    return render_template("foro/nuevo_canal.html", colores=ForoCanal.COLORES, iconos=ForoCanal.ICONOS)


# ── Eliminar canal ────────────────────────────────────────────────────────────

@foro_bp.route("/canal/eliminar/<canal_id>", methods=["POST"])
@login_required
def eliminar_canal(canal_id):
    """Elimina el canal y todos sus posts (admin y gestor)."""
    if session.get("rol") not in ("admin", "gestor"):
        flash("Solo administradores y gestores pueden eliminar canales.", "danger")
        return redirect(url_for("foro.listar"))

    db         = get_db()
    canal_mdl  = ForoCanal(db)
    posts_mdl  = ForoPost(db)
    resp_mdl   = ForoRespuesta(db)

    canal = canal_mdl.obtener_por_id(canal_id)
    if not canal:
        flash("Canal no encontrado.", "danger")
        return redirect(url_for("foro.listar"))

    # Borrar todos los posts y respuestas del canal
    posts = posts_mdl.obtener_por_canal(canal_id)
    for p in posts:
        eliminar_imagenes(_fotos_doc(p), "foro")
        for r in resp_mdl.obtener_por_post(str(p["_id"])):
            eliminar_imagenes(_fotos_doc(r), "foro")
        resp_mdl.eliminar_por_post(str(p["_id"]))
        posts_mdl.eliminar(str(p["_id"]))

    canal_mdl.eliminar(canal_id)
    registrar_log(db, "registro", "eliminar_canal_foro", session["nombre"], f"Canal: {canal['nombre']}")
    flash(f"Canal '{canal['nombre']}' eliminado.", "info")
    return redirect(url_for("foro.listar"))


# ── Posts de un canal ─────────────────────────────────────────────────────────

@foro_bp.route("/canal/<canal_id>")
@login_required
def ver_canal(canal_id):
    """Muestra los posts de un canal con buscador."""
    db        = get_db()
    canal_mdl = ForoCanal(db)
    posts_mdl = ForoPost(db)
    resp_mdl  = ForoRespuesta(db)

    canal = canal_mdl.obtener_por_id(canal_id)
    if not canal:
        flash("Canal no encontrado.", "danger")
        return redirect(url_for("foro.listar"))

    filtros = posts_mdl.construir_filtros(request.args)
    posts   = posts_mdl.obtener_por_canal(canal_id, filtros)

    for p in posts:
        p["num_respuestas"] = resp_mdl.contar_por_post(str(p["_id"]))
    _anotar_fotos_autor(db, posts)

    return render_template("foro/canal.html", canal=canal, posts=posts, filtros=request.args)


# ── Detalle + responder ───────────────────────────────────────────────────────

@foro_bp.route("/detalle/<post_id>", methods=["GET", "POST"])
@login_required
def detalle(post_id):
    """
    GET:  muestra el post completo con todas sus respuestas.
    POST: procesa el formulario de nueva respuesta (requiere sesión).
    """
    db         = get_db()
    modelo     = ForoPost(db)
    modelo_resp = ForoRespuesta(db)
    post       = modelo.obtener_por_id(post_id)

    if not post:
        flash("Publicacion no encontrada.", "danger")
        return redirect(url_for("foro.listar"))

    if request.method == "POST":
        # El formulario de respuesta requiere sesión activa
        if "user_id" not in session:
            flash("Debes iniciar sesión para responder.", "warning")
            return redirect(url_for("auth.login"))

        contenido = request.form.get("contenido", "").strip()
        if not contenido:
            flash("La respuesta no puede estar vacia.", "danger")
            return redirect(url_for("foro.detalle", post_id=post_id))

        fotos = guardar_imagenes(request.files.getlist("fotos"), "foro")
        modelo_resp.crear(post_id, contenido, fotos,
                          session["user_id"], session["nombre"])
        registrar_log(db, "registro", "crear_respuesta_foro",
                      session["nombre"], f"Post ID: {post_id}")

        flash("Respuesta publicada.", "success")
        return redirect(url_for("foro.detalle", post_id=post_id) + "#respuestas")

    respuestas = modelo_resp.obtener_por_post(post_id)
    _anotar_fotos_autor(db, [post])
    _anotar_fotos_autor(db, respuestas)
    canal = ForoCanal(db).obtener_por_id(post.get("canal_id", "")) if post.get("canal_id") else None
    return render_template("foro/detalle.html", post=post, respuestas=respuestas, canal=canal)


# ── Crear post en canal ───────────────────────────────────────────────────────

@foro_bp.route("/canal/<canal_id>/nuevo", methods=["GET", "POST"])
@login_required
def nuevo(canal_id):
    """Formulario para crear un nuevo post dentro de un canal."""
    db        = get_db()
    canal_mdl = ForoCanal(db)
    canal     = canal_mdl.obtener_por_id(canal_id)

    if not canal:
        flash("Canal no encontrado.", "danger")
        return redirect(url_for("foro.listar"))

    if request.method == "POST":
        modelo    = ForoPost(db)
        titulo    = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()

        if not titulo or not contenido:
            flash("El título y el contenido son obligatorios.", "danger")
            return render_template("foro/formulario.html", post=None, canal=canal, accion="Publicar")

        fotos = guardar_imagenes(request.files.getlist("fotos"), "foro")
        modelo.crear(titulo, contenido, fotos, canal_id, session["user_id"], session["nombre"])
        registrar_log(db, "registro", "crear_post_foro",
                      session["nombre"], f"Canal: {canal['nombre']} | Título: {titulo}")

        flash("Publicacion creada correctamente.", "success")
        return redirect(url_for("foro.ver_canal", canal_id=canal_id))

    return render_template("foro/formulario.html", post=None, canal=canal, accion="Publicar")


# ── Edición ───────────────────────────────────────────────────────────────────

@foro_bp.route("/editar/<post_id>", methods=["GET", "POST"])
@login_required
def editar(post_id):
    """
    Editar un post.
    - Admin:   puede editar siempre.
    - Autor:   solo si todavia no hay respuestas (para no alterar el hilo).
    - Gestor:  NO puede editar (si puede borrar).
    """
    db     = get_db()
    modelo = ForoPost(db)
    post   = modelo.obtener_por_id(post_id)

    if not post:
        flash("Publicacion no encontrada.", "danger")
        return redirect(url_for("foro.listar"))

    es_propietario = post["usuario_id"] == session["user_id"]
    es_admin       = session.get("rol") == "admin"

    # Solo el autor de su propio post o el admin pueden editar
    if not es_admin and not es_propietario:
        flash("No tienes permisos para editar esta publicacion.", "danger")
        return redirect(url_for("foro.detalle", post_id=post_id))

    if request.method == "POST":
        titulo    = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()

        if not titulo or not contenido:
            flash("El título y el contenido son obligatorios.", "danger")
            return render_template("foro/formulario.html", post=post, accion="Guardar")

        datos = {"titulo": titulo, "contenido": contenido}

        fotos = list(post.get("fotos") or [])
        # Si habia imagen legado la tratamos como foto 0
        if post.get("imagen") and post["imagen"] not in fotos:
            fotos.insert(0, post["imagen"])

        a_borrar = request.form.getlist("borrar_fotos")
        if a_borrar:
            eliminar_imagenes(a_borrar, "foro")
            fotos = [f for f in fotos if f not in a_borrar]
            if post.get("imagen") in a_borrar:
                datos["imagen"] = None

        fotos.extend(guardar_imagenes(request.files.getlist("fotos"), "foro"))
        datos["fotos"] = fotos

        modelo.actualizar(post_id, datos)
        registrar_log(db, "registro", "editar_post_foro",
                      session["nombre"], f"ID: {post_id}")

        flash("Publicacion actualizada.", "success")
        return redirect(url_for("foro.detalle", post_id=post_id))

    canal = ForoCanal(db).obtener_por_id(post.get("canal_id", "")) if post.get("canal_id") else None
    return render_template("foro/formulario.html", post=post, canal=canal, accion="Guardar")


# ── Eliminación de post ───────────────────────────────────────────────────────

@foro_bp.route("/eliminar/<post_id>", methods=["POST"])
@login_required
def eliminar(post_id):
    """Elimina el post y todas sus respuestas tras verificar permisos."""
    db     = get_db()
    modelo = ForoPost(db)
    post   = modelo.obtener_por_id(post_id)

    if not post:
        flash("Publicacion no encontrada.", "danger")
        return redirect(url_for("foro.listar"))

    # Pueden borrar: el autor, el gestor o el admin
    es_propietario = post["usuario_id"] == session["user_id"]
    puede_borrar   = es_propietario or session.get("rol") in ("admin", "gestor")
    if not puede_borrar:
        flash("No tienes permisos para eliminar esta publicacion.", "danger")
        return redirect(url_for("foro.detalle", post_id=post_id))

    eliminar_imagenes(_fotos_doc(post), "foro")

    resp_modelo = ForoRespuesta(db)
    for r in resp_modelo.obtener_por_post(post_id):
        eliminar_imagenes(_fotos_doc(r), "foro")

    # Borrar respuestas y luego el post de MongoDB
    resp_modelo.eliminar_por_post(post_id)
    modelo.eliminar(post_id)

    registrar_log(db, "registro", "eliminar_post_foro",
                  session["nombre"], f"ID: {post_id}")

    flash("Publicacion eliminada.", "info")
    canal_id = post.get("canal_id")
    if canal_id:
        return redirect(url_for("foro.ver_canal", canal_id=canal_id))
    return redirect(url_for("foro.listar"))


# ── Eliminación de respuesta ──────────────────────────────────────────────────

@foro_bp.route("/respuesta/eliminar/<respuesta_id>", methods=["POST"])
@login_required
def eliminar_respuesta(respuesta_id):
    """Elimina una respuesta tras verificar permisos."""
    db          = get_db()
    modelo_resp = ForoRespuesta(db)
    respuesta   = modelo_resp.obtener_por_id(respuesta_id)

    if not respuesta:
        flash("Respuesta no encontrada.", "danger")
        return redirect(url_for("foro.listar"))

    # Pueden borrar: el autor de la respuesta, el gestor o el admin
    es_propietario = respuesta["usuario_id"] == session["user_id"]
    puede_borrar   = es_propietario or session.get("rol") in ("admin", "gestor")
    if not puede_borrar:
        flash("No tienes permisos para eliminar esta respuesta.", "danger")
        return redirect(url_for("foro.detalle", post_id=respuesta["post_id"]))

    eliminar_imagenes(_fotos_doc(respuesta), "foro")
    modelo_resp.eliminar(respuesta_id)
    registrar_log(db, "registro", "eliminar_respuesta_foro",
                  session["nombre"], f"ID: {respuesta_id}")

    flash("Respuesta eliminada.", "info")
    return redirect(url_for("foro.detalle", post_id=respuesta["post_id"]) + "#respuestas")
