"""
routes/compraventa.py - Rutas del modulo de Compra-Venta (CRUD completo).

Incluye la seccion especial de merchandising de unidades de la Armada.
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.compraventa import Compraventa
from utils.db import get_db
from utils.helpers import actualizar_contadores, login_required, registrar_log

compraventa_bp = Blueprint("compraventa", __name__, url_prefix="/compraventa")


@compraventa_bp.route("/")
def listar():
    """Lista todos los articulos de compraventa (excluye merchandising)."""
    db = get_db()
    modelo = Compraventa(db)
    filtros = modelo.construir_filtros(request.args)
    filtros["es_merchandising"] = False
    anuncios = modelo.obtener_todos(filtros)
    return render_template("compraventa/listar.html", anuncios=anuncios, filtros=request.args)


@compraventa_bp.route("/armada")
def armada():
    """Seccion especial de merchandising de unidades de la Armada."""
    db = get_db()
    articulos = Compraventa(db).obtener_merchandising()
    return render_template("compraventa/armada.html", articulos=articulos)


@compraventa_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    """Formulario para publicar un nuevo articulo."""
    if request.method == "POST":
        db = get_db()
        modelo = Compraventa(db)

        es_merch = request.form.get("es_merchandising") == "on"
        datos = {
            "nombre_articulo": request.form.get("nombre_articulo", "").strip(),
            "uco": request.form.get("uco", "").strip(),
            "precio": request.form.get("precio", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "es_merchandising": es_merch,
            "unidad_armada": request.form.get("unidad_armada", "").strip() if es_merch else "",
        }

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
        datos = {
            "nombre_articulo": request.form.get("nombre_articulo", "").strip(),
            "uco": request.form.get("uco", "").strip(),
            "precio": request.form.get("precio", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "es_merchandising": es_merch,
            "unidad_armada": request.form.get("unidad_armada", "").strip() if es_merch else "",
        }
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
