"""
routes/compraventa.py - Rutas del módulo de Compra-Venta (CRUD completo).

Incluye la seccion especial de merchandising de unidades de la Armada.
"""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.compraventa import Compraventa


def _parsear_fecha_exp(fecha_str):
    if not fecha_str or not fecha_str.strip():
        return None
    try:
        d = datetime.strptime(fecha_str.strip(), "%Y-%m-%d")
        return d.replace(hour=23, minute=59, second=59)
    except ValueError:
        return None
from utils.db import get_db
from utils.decorators import login_required
from utils.logs import actualizar_contadores, registrar_log
from utils.uploads import eliminar_imagenes, guardar_imagenes

compraventa_bp = Blueprint("compraventa", __name__, url_prefix="/compraventa")


@compraventa_bp.route("/")
def listar():
    """Lista todos los artículos de compraventa (excluye merchandising)."""
    import math
    PER_PAGE = 12
    db = get_db()
    modelo = Compraventa(db)
    filtros_q = modelo.construir_filtros(request.args)
    filtros_q["es_merchandising"] = False
    total = modelo.contar(filtros_q)
    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
    total_paginas = max(1, math.ceil(total / PER_PAGE))
    page = min(page, total_paginas)
    anuncios = modelo.obtener_todos(filtros_q, skip=(page - 1) * PER_PAGE, limit=PER_PAGE)
    filtros_form = {k: v for k, v in request.args.items() if k != 'page'}
    return render_template("compraventa/listar.html", anuncios=anuncios, filtros=filtros_form,
                           page=page, total_paginas=total_paginas)


@compraventa_bp.route("/armada")
def armada():
    """Seccion especial de merchandising de unidades de la Armada."""
    db = get_db()
    artículos = Compraventa(db).obtener_merchandising()
    return render_template("compraventa/armada.html", artículos=artículos)


@compraventa_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    """Formulario para publicar un nuevo articulo."""
    if request.method == "POST":
        db = get_db()
        modelo = Compraventa(db)

        es_merch = request.form.get("es_merchandising") == "on"
        precio = request.form.get("precio", "").strip()
        email_contacto = request.form.get("email_contacto", "").strip()
        if not precio:
            flash("El precio es obligatorio.", "danger")
            return render_template("compraventa/formulario.html", anuncio=None, accion="Crear")
        if not email_contacto:
            flash("El correo de contacto es obligatorio.", "danger")
            return render_template("compraventa/formulario.html", anuncio=None, accion="Crear")

        datos = {
            "nombre_articulo":   request.form.get("nombre_articulo", "").strip(),
            "uco":               request.form.get("uco", "").strip(),
            "precio":            precio,
            "descripcion":       request.form.get("descripcion", "").strip(),
            "es_merchandising":  es_merch,
            "unidad_armada":     request.form.get("unidad_armada", "").strip() if es_merch else "",
            "fecha_expiracion":  _parsear_fecha_exp(request.form.get("fecha_expiracion")),
            "email_contacto":    email_contacto,
            "telefono_contacto": request.form.get("telefono_contacto", "").strip(),
        }

        datos["fotos"] = guardar_imagenes(request.files.getlist("fotos"), "compraventa")
        modelo.crear(datos, session["user_id"], session["nombre"])
        registrar_log(db, "registro", "crear_compraventa", session["nombre"],
                      f"Articulo: {datos['nombre_articulo']}")
        actualizar_contadores(db)

        flash("Articulo publicado correctamente.", "success")
        return redirect(url_for("compraventa.armada" if es_merch else "compraventa.listar"))

    return render_template("compraventa/formulario.html", anuncio=None, accion="Crear")


@compraventa_bp.route("/editar/<anuncio_id>", methods=["GET", "POST"])
@login_required
def editar(anuncio_id):
    """Editar un articulo existente."""
    db = get_db()
    modelo = Compraventa(db)
    anuncio = modelo.obtener_por_id(anuncio_id)

    if not anuncio:
        flash("Articulo no encontrado.", "danger")
        return redirect(url_for("compraventa.listar"))

    es_propietario = anuncio["usuario_id"] == session["user_id"]
    es_privilegiado = session.get("rol") in ("admin", "gestor")
    if not es_propietario and not es_privilegiado:
        flash("No tienes permisos para editar este articulo.", "danger")
        return redirect(url_for("compraventa.listar"))

    if request.method == "POST":
        es_merch = request.form.get("es_merchandising") == "on"
        precio_edit = request.form.get("precio", "").strip()
        email_contacto_edit = request.form.get("email_contacto", "").strip()
        if not precio_edit:
            flash("El precio es obligatorio.", "danger")
            return render_template("compraventa/formulario.html", anuncio=anuncio, accion="Editar")
        if not email_contacto_edit:
            flash("El correo de contacto es obligatorio.", "danger")
            return render_template("compraventa/formulario.html", anuncio=anuncio, accion="Editar")

        datos = {
            "nombre_articulo":   request.form.get("nombre_articulo", "").strip(),
            "uco":               request.form.get("uco", "").strip(),
            "precio":            precio_edit,
            "descripcion":       request.form.get("descripcion", "").strip(),
            "es_merchandising":  es_merch,
            "unidad_armada":     request.form.get("unidad_armada", "").strip() if es_merch else "",
            "fecha_expiracion":  _parsear_fecha_exp(request.form.get("fecha_expiracion")),
            "email_contacto":    email_contacto_edit,
            "telefono_contacto": request.form.get("telefono_contacto", "").strip(),
        }
        fotos = list(anuncio.get("fotos") or [])
        a_borrar = request.form.getlist("borrar_fotos")
        if a_borrar:
            eliminar_imagenes(a_borrar, "compraventa")
            fotos = [f for f in fotos if f not in a_borrar]
        fotos.extend(guardar_imagenes(request.files.getlist("fotos"), "compraventa"))
        datos["fotos"] = fotos
        if session.get("rol") in ("admin", "gestor") and anuncio["usuario_id"] != session["user_id"]:
            from datetime import datetime
            datos["editado_por"] = session["nombre"]
            datos["fecha_edicion"] = datetime.now()
        modelo.actualizar(anuncio_id, datos)
        registrar_log(db, "registro", "editar_compraventa", session["nombre"], f"ID: {anuncio_id}")

        flash("Articulo actualizado correctamente.", "success")
        return redirect(url_for("compraventa.listar"))

    return render_template("compraventa/formulario.html", anuncio=anuncio, accion="Editar")


@compraventa_bp.route("/eliminar/<anuncio_id>", methods=["POST"])
@login_required
def eliminar(anuncio_id):
    """Eliminar un articulo."""
    db = get_db()
    modelo = Compraventa(db)
    anuncio = modelo.obtener_por_id(anuncio_id)

    if not anuncio:
        flash("Articulo no encontrado.", "danger")
        return redirect(url_for("compraventa.listar"))

    es_propietario = anuncio["usuario_id"] == session["user_id"]
    es_privilegiado = session.get("rol") in ("admin", "gestor")
    if not es_propietario and not es_privilegiado:
        flash("No tienes permisos para eliminar este articulo.", "danger")
        return redirect(url_for("compraventa.listar"))

    eliminar_imagenes(anuncio.get("fotos") or [], "compraventa")
    modelo.eliminar(anuncio_id)
    registrar_log(db, "registro", "eliminar_compraventa", session["nombre"], f"ID: {anuncio_id}")
    actualizar_contadores(db)

    flash("Articulo eliminado.", "info")
    return redirect(url_for("compraventa.listar"))


@compraventa_bp.route("/detalle/<anuncio_id>")
def detalle(anuncio_id):
    """Vista de detalle de un articulo."""
    db = get_db()
    anuncio = Compraventa(db).obtener_por_id(anuncio_id)

    if not anuncio:
        flash("Articulo no encontrado.", "danger")
        return redirect(url_for("compraventa.listar"))

    return render_template("compraventa/detalle.html", anuncio=anuncio)
