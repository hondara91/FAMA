"""
routes/servicios.py - Rutas del modulo de Servicios (CRUD completo).

Gestiona ofertas y busquedas de servicios entre el personal militar.
"""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.servicio import Servicio
from utils.db import get_db
from utils.decorators import login_required
from utils.logs import actualizar_contadores, registrar_log
from utils.uploads import eliminar_imagenes, guardar_imagenes


def validar_telefono(telefono):
    return telefono == "" or (telefono.isdigit() and len(telefono) == 9)


def _parsear_fecha_exp(fecha_str):
    if not fecha_str or not fecha_str.strip():
        return None
    try:
        d = datetime.strptime(fecha_str.strip(), "%Y-%m-%d")
        return d.replace(hour=23, minute=59, second=59)
    except ValueError:
        return None


servicios_bp = Blueprint("servicios", __name__, url_prefix="/servicios")


@servicios_bp.route("/")
def listar():
    """Lista todos los anuncios de servicios con buscador."""
    db = get_db()
    modelo = Servicio(db)
    filtros = modelo.construir_filtros(request.args)
    anuncios = modelo.obtener_todos(filtros)
    return render_template("servicios/listar.html", anuncios=anuncios, filtros=request.args)


@servicios_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    """Formulario para crear un nuevo anuncio de servicio."""
    if request.method == "POST":
        db = get_db()
        modelo = Servicio(db)

        telefono = request.form.get("telefono", "").strip()
        if not validar_telefono(telefono):
            flash("El teléfono debe contener exactamente 9 dígitos numéricos.", "danger")
            datos = {
                "tipo": request.form.get("tipo"),
                "categoria": request.form.get("categoria"),
                "titulo": request.form.get("titulo", "").strip(),
                "precio": request.form.get("precio", "").strip(),
                "modalidad": request.form.get("modalidad"),
                "telefono": telefono,
                "ciudad": request.form.get("ciudad", "").strip(),
                "descripcion": request.form.get("descripcion", "").strip(),
            }
            return render_template("servicios/formulario.html", anuncio=datos, accion="Crear")

        datos = {
            "tipo":       request.form.get("tipo"),
            "categoria":  request.form.get("categoria"),
            "titulo":     request.form.get("titulo", "").strip(),
            "precio":     request.form.get("precio", "").strip(),
            "modalidad":  request.form.get("modalidad"),
            "telefono":   telefono,
            "ciudad":     request.form.get("ciudad", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "fecha_expiracion": _parsear_fecha_exp(request.form.get("fecha_expiracion")),
        }

        datos["fotos"] = guardar_imagenes(request.files.getlist("fotos"), "servicios")
        modelo.crear(datos, session["user_id"], session["nombre"])
        registrar_log(db, "registro", "crear_servicio", session["nombre"],
                      f"Titulo: {datos['titulo']}, Categoria: {datos['categoria']}")
        actualizar_contadores(db)

        flash("Anuncio de servicio publicado correctamente.", "success")
        return redirect(url_for("servicios.listar"))

    return render_template("servicios/formulario.html", anuncio=None, accion="Crear")


@servicios_bp.route("/editar/<anuncio_id>", methods=["GET", "POST"])
@login_required
def editar(anuncio_id):
    """Editar un anuncio de servicio existente."""
    db = get_db()
    modelo = Servicio(db)
    anuncio = modelo.obtener_por_id(anuncio_id)

    if not anuncio:
        flash("Anuncio no encontrado.", "danger")
        return redirect(url_for("servicios.listar"))

    es_propietario = anuncio["usuario_id"] == session["user_id"]
    es_privilegiado = session.get("rol") in ("admin", "gestor")
    if not es_propietario and not es_privilegiado:
        flash("No tienes permisos para editar este anuncio.", "danger")
        return redirect(url_for("servicios.listar"))

    if request.method == "POST":
        telefono = request.form.get("telefono", "").strip()
        if not validar_telefono(telefono):
            flash("El teléfono debe contener exactamente 9 dígitos numéricos.", "danger")
            datos = {
                "tipo":       request.form.get("tipo"),
                "categoria":  request.form.get("categoria"),
                "titulo":     request.form.get("titulo", "").strip(),
                "precio":     request.form.get("precio", "").strip(),
                "modalidad":  request.form.get("modalidad"),
                "telefono":   telefono,
                "ciudad":     request.form.get("ciudad", "").strip(),
                "descripcion": request.form.get("descripcion", "").strip(),
                "fecha_expiracion": _parsear_fecha_exp(request.form.get("fecha_expiracion")),
                "fotos":      list(anuncio.get("fotos") or []),
            }
            return render_template("servicios/formulario.html", anuncio=datos, accion="Editar")

        datos = {
            "tipo":       request.form.get("tipo"),
            "categoria":  request.form.get("categoria"),
            "titulo":     request.form.get("titulo", "").strip(),
            "precio":     request.form.get("precio", "").strip(),
            "modalidad":  request.form.get("modalidad"),
            "telefono":   telefono,
            "ciudad":     request.form.get("ciudad", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "fecha_expiracion": _parsear_fecha_exp(request.form.get("fecha_expiracion")),
        }
        fotos = list(anuncio.get("fotos") or [])
        a_borrar = request.form.getlist("borrar_fotos")
        if a_borrar:
            eliminar_imagenes(a_borrar, "servicios")
            fotos = [f for f in fotos if f not in a_borrar]
        fotos.extend(guardar_imagenes(request.files.getlist("fotos"), "servicios"))
        datos["fotos"] = fotos
        if session.get("rol") in ("admin", "gestor") and anuncio["usuario_id"] != session["user_id"]:
            from datetime import datetime
            datos["editado_por"] = session["nombre"]
            datos["fecha_edicion"] = datetime.now()
        modelo.actualizar(anuncio_id, datos)
        registrar_log(db, "registro", "editar_servicio", session["nombre"], f"ID: {anuncio_id}")

        flash("Anuncio de servicio actualizado correctamente.", "success")
        return redirect(url_for("servicios.listar"))

    return render_template("servicios/formulario.html", anuncio=anuncio, accion="Editar")


@servicios_bp.route("/eliminar/<anuncio_id>", methods=["POST"])
@login_required
def eliminar(anuncio_id):
    """Eliminar un anuncio de servicio."""
    db = get_db()
    modelo = Servicio(db)
    anuncio = modelo.obtener_por_id(anuncio_id)

    if not anuncio:
        flash("Anuncio no encontrado.", "danger")
        return redirect(url_for("servicios.listar"))

    es_propietario = anuncio["usuario_id"] == session["user_id"]
    es_privilegiado = session.get("rol") in ("admin", "gestor")
    if not es_propietario and not es_privilegiado:
        flash("No tienes permisos para eliminar este anuncio.", "danger")
        return redirect(url_for("servicios.listar"))

    eliminar_imagenes(anuncio.get("fotos") or [], "servicios")
    modelo.eliminar(anuncio_id)
    registrar_log(db, "registro", "eliminar_servicio", session["nombre"], f"ID: {anuncio_id}")
    actualizar_contadores(db)

    flash("Anuncio de servicio eliminado.", "info")
    return redirect(url_for("servicios.listar"))


@servicios_bp.route("/detalle/<anuncio_id>")
def detalle(anuncio_id):
    """Vista de detalle de un anuncio de servicio."""
    db = get_db()
    modelo = Servicio(db)
    anuncio = modelo.obtener_por_id(anuncio_id)

    if not anuncio:
        flash("Anuncio no encontrado.", "danger")
        return redirect(url_for("servicios.listar"))

    return render_template("servicios/detalle.html", anuncio=anuncio)
