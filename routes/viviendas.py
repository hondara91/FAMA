"""
routes/viviendas.py - Rutas del modulo de Viviendas (CRUD completo).

Patron de permisos usado en editar y eliminar:
  - El propietario del anuncio siempre puede modificarlo.
  - Los roles 'gestor' y 'admin' pueden modificar cualquier anuncio.
  - Un usuario sin relacion con el anuncio recibe un error 403 implicito.
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.vivienda import Vivienda
from utils.db import get_db
from utils.decorators import login_required
from utils.logs import actualizar_contadores, registrar_log
from utils.uploads import eliminar_imagenes, guardar_imagenes

viviendas_bp = Blueprint("viviendas", __name__, url_prefix="/viviendas")


# ── Listado ───────────────────────────────────────────────────────────────────

@viviendas_bp.route("/")
def listar():
    """Muestra todos los anuncios con buscador. Accesible sin autenticacion."""
    db     = get_db()
    modelo = Vivienda(db)
    # construir_filtros() traduce los parametros GET a una query MongoDB
    filtros  = modelo.construir_filtros(request.args)
    anuncios = modelo.obtener_todos(filtros)
    # Se pasa 'filtros' para que el formulario del buscador recuerde los valores
    return render_template("viviendas/listar.html", anuncios=anuncios, filtros=request.args)


# ── Creacion ──────────────────────────────────────────────────────────────────

@viviendas_bp.route("/nuevo", methods=["GET", "POST"])
@login_required  # Solo usuarios autenticados pueden publicar
def nuevo():
    """Muestra el formulario vacio (GET) y persiste el nuevo anuncio (POST)."""
    if request.method == "POST":
        db     = get_db()
        modelo = Vivienda(db)

        # Recoger y limpiar todos los campos del formulario
        datos = {
            "tipo_oferta":   request.form.get("tipo_oferta"),
            "tipo_inmueble": request.form.get("tipo_inmueble"),
            "ciudad":        request.form.get("ciudad", "").strip(),
            "zona":          request.form.get("zona", "").strip(),
            "habitaciones":  request.form.get("habitaciones"),
            "banos":         request.form.get("banos"),
            "planta":        request.form.get("planta", "").strip(),
            "precio":        request.form.get("precio", "").strip(),
            # getlist() recoge multiples valores del mismo nombre (checkboxes de extras)
            "extras":        request.form.getlist("extras"),
            "telefono":      request.form.get("telefono", "").strip(),
            "descripcion":   request.form.get("descripcion", "").strip(),
        }

        datos["fotos"] = guardar_imagenes(request.files.getlist("fotos"), "viviendas")
        modelo.crear(datos, session["user_id"], session["nombre"])
        registrar_log(db, "registro", "crear_vivienda", session["nombre"],
                      f"Ciudad: {datos['ciudad']}, Tipo: {datos['tipo_oferta']}")
        actualizar_contadores(db)

        flash("Anuncio de vivienda publicado correctamente.", "success")
        return redirect(url_for("viviendas.listar"))

    # GET: formulario vacio; anuncio=None indica modo creacion en la plantilla
    return render_template("viviendas/formulario.html", anuncio=None, accion="Crear")


# ── Edicion ───────────────────────────────────────────────────────────────────

@viviendas_bp.route("/editar/<anuncio_id>", methods=["GET", "POST"])
@login_required
def editar(anuncio_id):
    """Muestra el formulario pre-rellenado (GET) y actualiza el anuncio (POST)."""
    db      = get_db()
    modelo  = Vivienda(db)
    anuncio = modelo.obtener_por_id(anuncio_id)

    # Verificar que el anuncio existe antes de continuar
    if not anuncio:
        flash("Anuncio no encontrado.", "danger")
        return redirect(url_for("viviendas.listar"))

    # ── Verificacion de permisos ──────────────────────────────────────────────
    es_propietario = anuncio["usuario_id"] == session["user_id"]
    es_privilegiado = session.get("rol") in ("admin", "gestor")
    if not es_propietario and not es_privilegiado:
        flash("No tienes permisos para editar este anuncio.", "danger")
        return redirect(url_for("viviendas.listar"))

    if request.method == "POST":
        datos = {
            "tipo_oferta":   request.form.get("tipo_oferta"),
            "tipo_inmueble": request.form.get("tipo_inmueble"),
            "ciudad":        request.form.get("ciudad", "").strip(),
            "zona":          request.form.get("zona", "").strip(),
            "habitaciones":  request.form.get("habitaciones"),
            "banos":         request.form.get("banos"),
            "planta":        request.form.get("planta", "").strip(),
            "precio":        request.form.get("precio", "").strip(),
            "extras":        request.form.getlist("extras"),
            "telefono":      request.form.get("telefono", "").strip(),
            "descripcion":   request.form.get("descripcion", "").strip(),
        }
        fotos = list(anuncio.get("fotos") or [])
        a_borrar = request.form.getlist("borrar_fotos")
        if a_borrar:
            eliminar_imagenes(a_borrar, "viviendas")
            fotos = [f for f in fotos if f not in a_borrar]
        fotos.extend(guardar_imagenes(request.files.getlist("fotos"), "viviendas"))
        datos["fotos"] = fotos
        modelo.actualizar(anuncio_id, datos)
        registrar_log(db, "registro", "editar_vivienda", session["nombre"], f"ID: {anuncio_id}")

        flash("Anuncio de vivienda actualizado correctamente.", "success")
        return redirect(url_for("viviendas.listar"))

    # GET: formulario pre-rellenado con los datos actuales; accion="Editar" para el boton
    return render_template("viviendas/formulario.html", anuncio=anuncio, accion="Editar")


# ── Borrado ───────────────────────────────────────────────────────────────────

@viviendas_bp.route("/eliminar/<anuncio_id>", methods=["POST"])
@login_required
def eliminar(anuncio_id):
    """Elimina el anuncio tras verificar que el usuario tiene permisos."""
    db      = get_db()
    modelo  = Vivienda(db)
    anuncio = modelo.obtener_por_id(anuncio_id)

    if not anuncio:
        flash("Anuncio no encontrado.", "danger")
        return redirect(url_for("viviendas.listar"))

    # Mismo patron de permisos que en editar
    es_propietario  = anuncio["usuario_id"] == session["user_id"]
    es_privilegiado = session.get("rol") in ("admin", "gestor")
    if not es_propietario and not es_privilegiado:
        flash("No tienes permisos para eliminar este anuncio.", "danger")
        return redirect(url_for("viviendas.listar"))

    eliminar_imagenes(anuncio.get("fotos") or [], "viviendas")
    modelo.eliminar(anuncio_id)
    registrar_log(db, "registro", "eliminar_vivienda", session["nombre"], f"ID: {anuncio_id}")
    actualizar_contadores(db)

    flash("Anuncio de vivienda eliminado.", "info")
    return redirect(url_for("viviendas.listar"))


# ── Detalle ───────────────────────────────────────────────────────────────────

@viviendas_bp.route("/detalle/<anuncio_id>")
def detalle(anuncio_id):
    """Vista de detalle de un anuncio. Accesible sin autenticacion."""
    db      = get_db()
    anuncio = Vivienda(db).obtener_por_id(anuncio_id)

    if not anuncio:
        flash("Anuncio no encontrado.", "danger")
        return redirect(url_for("viviendas.listar"))

    return render_template("viviendas/detalle.html", anuncio=anuncio)
