"""
routes/foro.py - Rutas del modulo de Foro (publicaciones + respuestas + imagenes).

Rutas disponibles:
  GET  /foro/              -> listado de posts con buscador
  GET  /foro/detalle/<id>  -> post completo con hilo de respuestas
  POST /foro/detalle/<id>  -> anadir una respuesta al post
  GET/POST /foro/nuevo     -> crear post nuevo
  GET/POST /foro/editar/<id>          -> editar post propio
  POST /foro/eliminar/<id>            -> eliminar post propio
  POST /foro/respuesta/eliminar/<id>  -> eliminar respuesta propia

Subida de imagenes: PNG/JPG/JPEG/GIF/WEBP, max 5 MB.
Los archivos se guardan en static/uploads/foro/.
"""
import os
from datetime import datetime

from bson import ObjectId
from flask import (Blueprint, current_app, flash, redirect,
                   render_template, request, session, url_for)
from werkzeug.utils import secure_filename

from models.foro import ForoPost, ForoRespuesta
from utils.db import get_db
from utils.helpers import login_required, registrar_log

foro_bp = Blueprint("foro", __name__, url_prefix="/foro")

# Extensiones de imagen permitidas para las subidas
_EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "gif", "webp"}


# ── Utilidad de subida de imagen ──────────────────────────────────────────────

def _guardar_imagen(archivo):
    """
    Valida y guarda el archivo de imagen recibido del formulario.

    Comprueba que la extension sea permitida, genera un nombre unico
    basado en timestamp para evitar colisiones, y guarda el archivo
    en static/uploads/foro/.

    Devuelve el nombre del archivo guardado, o None si no hay archivo
    o la extension no es valida.
    """
    if not archivo or archivo.filename == "":
        return None

    # Extraer extension y validarla
    ext = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
    if ext not in _EXTENSIONES_PERMITIDAS:
        return None

    # Nombre unico: timestamp_microsegundos + nombre seguro original
    nombre = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{secure_filename(archivo.filename)}"

    # Crear el directorio si no existe (primera ejecucion o volumen nuevo)
    carpeta = os.path.join(current_app.static_folder, "uploads", "foro")
    os.makedirs(carpeta, exist_ok=True)

    archivo.save(os.path.join(carpeta, nombre))
    return nombre


def _eliminar_imagen(nombre):
    """Borra el archivo de imagen del disco si existe."""
    if not nombre:
        return
    ruta = os.path.join(current_app.static_folder, "uploads", "foro", nombre)
    if os.path.exists(ruta):
        os.remove(ruta)


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


# ── Listado ───────────────────────────────────────────────────────────────────

@foro_bp.route("/")
def listar():
    """Muestra todos los posts con buscador. Accesible sin autenticacion."""
    db     = get_db()
    modelo = ForoPost(db)
    resp   = ForoRespuesta(db)

    filtros = modelo.construir_filtros(request.args)
    posts   = modelo.obtener_todos(filtros)

    # Anotar el numero de respuestas en cada post para mostrarlo en la tarjeta
    for p in posts:
        p["num_respuestas"] = resp.contar_por_post(str(p["_id"]))
    _anotar_fotos_autor(db, posts)

    return render_template("foro/listar.html", posts=posts, filtros=request.args)


# ── Detalle + responder ───────────────────────────────────────────────────────

@foro_bp.route("/detalle/<post_id>", methods=["GET", "POST"])
def detalle(post_id):
    """
    GET:  muestra el post completo con todas sus respuestas.
    POST: procesa el formulario de nueva respuesta (requiere sesion).
    """
    db         = get_db()
    modelo     = ForoPost(db)
    modelo_resp = ForoRespuesta(db)
    post       = modelo.obtener_por_id(post_id)

    if not post:
        flash("Publicacion no encontrada.", "danger")
        return redirect(url_for("foro.listar"))

    if request.method == "POST":
        # El formulario de respuesta requiere sesion activa
        if "user_id" not in session:
            flash("Debes iniciar sesion para responder.", "warning")
            return redirect(url_for("auth.login"))

        contenido = request.form.get("contenido", "").strip()
        if not contenido:
            flash("La respuesta no puede estar vacia.", "danger")
            return redirect(url_for("foro.detalle", post_id=post_id))

        # Guardar imagen adjunta si se subio alguna
        imagen = _guardar_imagen(request.files.get("imagen"))

        modelo_resp.crear(post_id, contenido, imagen,
                          session["user_id"], session["nombre"])
        registrar_log(db, "registro", "crear_respuesta_foro",
                      session["nombre"], f"Post ID: {post_id}")

        flash("Respuesta publicada.", "success")
        return redirect(url_for("foro.detalle", post_id=post_id) + "#respuestas")

    respuestas = modelo_resp.obtener_por_post(post_id)
    _anotar_fotos_autor(db, [post])
    _anotar_fotos_autor(db, respuestas)
    return render_template("foro/detalle.html", post=post, respuestas=respuestas)


# ── Creacion ──────────────────────────────────────────────────────────────────

@foro_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    """Formulario para crear un nuevo post (GET) y persistirlo (POST)."""
    if request.method == "POST":
        db     = get_db()
        modelo = ForoPost(db)

        titulo    = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()

        if not titulo or not contenido:
            flash("El titulo y el contenido son obligatorios.", "danger")
            return render_template("foro/formulario.html", post=None, accion="Publicar")

        imagen = _guardar_imagen(request.files.get("imagen"))

        modelo.crear(titulo, contenido, imagen, session["user_id"], session["nombre"])
        registrar_log(db, "registro", "crear_post_foro",
                      session["nombre"], f"Titulo: {titulo}")

        flash("Publicacion creada correctamente.", "success")
        return redirect(url_for("foro.listar"))

    return render_template("foro/formulario.html", post=None, accion="Publicar")


# ── Edicion ───────────────────────────────────────────────────────────────────

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

    if not es_admin:
        if not es_propietario:
            # Gestor u otro usuario: sin permiso de edicion en el foro
            flash("No tienes permisos para editar esta publicacion.", "danger")
            return redirect(url_for("foro.detalle", post_id=post_id))
        # Autor: bloquear edicion si ya existe alguna respuesta
        num_respuestas = ForoRespuesta(db).contar_por_post(post_id)
        if num_respuestas > 0:
            flash("No puedes editar una publicacion que ya tiene respuestas.", "warning")
            return redirect(url_for("foro.detalle", post_id=post_id))

    if request.method == "POST":
        titulo    = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()

        if not titulo or not contenido:
            flash("El titulo y el contenido son obligatorios.", "danger")
            return render_template("foro/formulario.html", post=post, accion="Guardar")

        datos = {"titulo": titulo, "contenido": contenido}

        # Si se sube una imagen nueva, borrar la anterior y guardar la nueva
        nueva_imagen = _guardar_imagen(request.files.get("imagen"))
        if nueva_imagen:
            _eliminar_imagen(post.get("imagen"))
            datos["imagen"] = nueva_imagen
        elif request.form.get("borrar_imagen"):
            # El usuario marcó el checkbox para eliminar la imagen sin subir otra
            _eliminar_imagen(post.get("imagen"))
            datos["imagen"] = None

        modelo.actualizar(post_id, datos)
        registrar_log(db, "registro", "editar_post_foro",
                      session["nombre"], f"ID: {post_id}")

        flash("Publicacion actualizada.", "success")
        return redirect(url_for("foro.detalle", post_id=post_id))

    return render_template("foro/formulario.html", post=post, accion="Guardar")


# ── Eliminacion de post ───────────────────────────────────────────────────────

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

    # Borrar imagen del post del disco
    _eliminar_imagen(post.get("imagen"))

    # Borrar tambien las imagenes de todas las respuestas del post
    resp_modelo = ForoRespuesta(db)
    for r in resp_modelo.obtener_por_post(post_id):
        _eliminar_imagen(r.get("imagen"))

    # Borrar respuestas y luego el post de MongoDB
    resp_modelo.eliminar_por_post(post_id)
    modelo.eliminar(post_id)

    registrar_log(db, "registro", "eliminar_post_foro",
                  session["nombre"], f"ID: {post_id}")

    flash("Publicacion eliminada.", "info")
    return redirect(url_for("foro.listar"))


# ── Eliminacion de respuesta ──────────────────────────────────────────────────

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

    _eliminar_imagen(respuesta.get("imagen"))
    modelo_resp.eliminar(respuesta_id)
    registrar_log(db, "registro", "eliminar_respuesta_foro",
                  session["nombre"], f"ID: {respuesta_id}")

    flash("Respuesta eliminada.", "info")
    return redirect(url_for("foro.detalle", post_id=respuesta["post_id"]) + "#respuestas")
