"""
routes/ocio.py - Rutas del modulo de Ocio (CRUD + inscripciones + calendario).

Gestiona eventos de ocio y el calendario unificado del personal militar.
"""
import json

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.ocio import Ocio
from utils.db import get_db
from utils.decorators import login_required
from utils.logs import actualizar_contadores, registrar_log

ocio_bp = Blueprint("ocio", __name__, url_prefix="/ocio")


@ocio_bp.route("/")
def listar():
    """Lista todos los eventos con buscador."""
    db = get_db()
    modelo = Ocio(db)
    filtros = modelo.construir_filtros(request.args)
    eventos = modelo.obtener_todos(filtros)
    return render_template("ocio/listar.html", eventos=eventos, filtros=request.args)


@ocio_bp.route("/calendario")
def calendario():
    """Vista de calendario con todos los eventos usando FullCalendar.js."""
    db = get_db()
    eventos_json = json.dumps(Ocio(db).obtener_para_calendario())
    return render_template("ocio/calendario.html", eventos_json=eventos_json)


@ocio_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    """Formulario para crear un nuevo evento de ocio."""
    if request.method == "POST":
        db = get_db()
        modelo = Ocio(db)

        datos = {
            "tipo_evento": request.form.get("tipo_evento"),
            "titulo": request.form.get("titulo", "").strip(),
            "fecha": request.form.get("fecha"),
            "hora": request.form.get("hora"),
            "lugar": request.form.get("lugar", "").strip(),
            "aforo_maximo": request.form.get("aforo_maximo", 0),
            "descripcion": request.form.get("descripcion", "").strip(),
        }

        modelo.crear(datos, session["user_id"], session["nombre"])
        registrar_log(db, "registro", "crear_evento", session["nombre"],
                      f"Evento: {datos['titulo']}, Fecha: {datos['fecha']}")
        actualizar_contadores(db)

        flash("Evento creado correctamente.", "success")
        return redirect(url_for("ocio.listar"))

    return render_template("ocio/formulario.html", evento=None, accion="Crear")


@ocio_bp.route("/editar/<evento_id>", methods=["GET", "POST"])
@login_required
def editar(evento_id):
    """Editar un evento existente."""
    db = get_db()
    modelo = Ocio(db)
    evento = modelo.obtener_por_id(evento_id)

    if not evento:
        flash("Evento no encontrado.", "danger")
        return redirect(url_for("ocio.listar"))

    es_propietario = evento["usuario_id"] == session["user_id"]
    es_privilegiado = session.get("rol") in ("admin", "gestor")
    if not es_propietario and not es_privilegiado:
        flash("No tienes permisos para editar este evento.", "danger")
        return redirect(url_for("ocio.listar"))

    if request.method == "POST":
        datos = {
            "tipo_evento": request.form.get("tipo_evento"),
            "titulo": request.form.get("titulo", "").strip(),
            "fecha": request.form.get("fecha"),
            "hora": request.form.get("hora"),
            "lugar": request.form.get("lugar", "").strip(),
            "aforo_maximo": int(request.form.get("aforo_maximo", 0)),
            "descripcion": request.form.get("descripcion", "").strip(),
        }
        modelo.actualizar(evento_id, datos)
        registrar_log(db, "registro", "editar_evento", session["nombre"], f"ID: {evento_id}")

        flash("Evento actualizado correctamente.", "success")
        return redirect(url_for("ocio.listar"))

    return render_template("ocio/formulario.html", evento=evento, accion="Editar")


@ocio_bp.route("/eliminar/<evento_id>", methods=["POST"])
@login_required
def eliminar(evento_id):
    """Eliminar un evento."""
    db = get_db()
    modelo = Ocio(db)
    evento = modelo.obtener_por_id(evento_id)

    if not evento:
        flash("Evento no encontrado.", "danger")
        return redirect(url_for("ocio.listar"))

    es_propietario = evento["usuario_id"] == session["user_id"]
    es_privilegiado = session.get("rol") in ("admin", "gestor")
    if not es_propietario and not es_privilegiado:
        flash("No tienes permisos para eliminar este evento.", "danger")
        return redirect(url_for("ocio.listar"))

    modelo.eliminar(evento_id)
    registrar_log(db, "registro", "eliminar_evento", session["nombre"], f"ID: {evento_id}")
    actualizar_contadores(db)

    flash("Evento eliminado.", "info")
    return redirect(url_for("ocio.listar"))


@ocio_bp.route("/inscribir/<evento_id>", methods=["POST"])
@login_required
def inscribir(evento_id):
    """Inscribir al usuario actual en un evento."""
    db = get_db()
    exito, mensaje = Ocio(db).inscribir_usuario(evento_id, session["user_id"])
    flash(mensaje, "success" if exito else "warning")
    return redirect(url_for("ocio.detalle", evento_id=evento_id))


@ocio_bp.route("/desinscribir/<evento_id>", methods=["POST"])
@login_required
def desinscribir(evento_id):
    """Cancelar la inscripcion del usuario en un evento."""
    Ocio(get_db()).desinscribir_usuario(evento_id, session["user_id"])
    flash("Inscripcion cancelada.", "info")
    return redirect(url_for("ocio.detalle", evento_id=evento_id))


@ocio_bp.route("/detalle/<evento_id>")
def detalle(evento_id):
    """Vista de detalle de un evento."""
    db = get_db()
    evento = Ocio(db).obtener_por_id(evento_id)

    if not evento:
        flash("Evento no encontrado.", "danger")
        return redirect(url_for("ocio.listar"))

    user_inscrito = session.get("user_id") in evento.get("inscritos", [])
    plazas_libres = evento.get("aforo_maximo", 0) - len(evento.get("inscritos", []))

    return render_template("ocio/detalle.html", evento=evento,
                           user_inscrito=user_inscrito, plazas_libres=plazas_libres)
