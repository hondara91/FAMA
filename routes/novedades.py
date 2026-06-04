"""
routes/novedades.py - Modulo de Novedades de FAMA.

Permite a administradores y gestores publicar novedades de servicio.
Al visitar la pagina se registra la fecha de visita en la sesión del usuario
para que el indicador del boton deje de iluminarse.

Campos de una novedad:
  tipo          (obligatorio): curso | comision de servicio | otros
  destino       (opcional)
  empleo        (opcional)
  localidad     (opcional)
  fecha_inicio  (opcional)
  fecha_fin     (opcional)
  observaciones (opcional)

Rutas:
  GET  /novedades/              -> listado (marca como vistas)
  POST /novedades/nueva         -> publicar (admin o gestor)
  POST /novedades/eliminar/<id> -> eliminar (admin o gestor)
"""
from datetime import date as date_type, datetime

from bson import ObjectId
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from utils.db import get_db
from utils.decorators import gestor_required, login_required

novedades_bp = Blueprint("novedades", __name__, url_prefix="/novedades")

# Valores validos para el campo 'tipo'
TIPOS_NOVEDAD = ["Curso", "Comision de servicio", "Otros"]


@novedades_bp.route("/")
@login_required
def listar():
    """
    Muestra todas las novedades ordenadas de mas reciente a mas antigua.
    Actualiza 'novedades_vistas_hasta' en la sesión para desactivar el indicador.
    """
    db = get_db()
    novedades = list(db.novedades.find().sort("fecha_creacion", -1))

    # Guardar timestamp de visita para que el indicador deje de brillar
    session["novedades_vistas_hasta"] = datetime.now().isoformat()

    return render_template("novedades/listar.html", novedades=novedades,
                           tipos=TIPOS_NOVEDAD)


@novedades_bp.route("/nueva", methods=["POST"])
@login_required
@gestor_required  # Admin y gestor pueden publicar novedades
def nueva():
    """Crea una nueva novedad con los campos del formulario."""
    db   = get_db()
    tipo = request.form.get("tipo", "").strip()

    # El campo 'tipo' es obligatorio
    if not tipo:
        flash("El tipo de novedad es obligatorio.", "danger")
        return redirect(url_for("novedades.listar"))

    # Recoger campos opcionales; solo se guardan si tienen contenido
    def campo(nombre):
        valor = request.form.get(nombre, "").strip()
        return valor if valor else None

    hoy = date_type.today().isoformat()
    fecha_inicio = campo("fecha_inicio")
    fecha_fin    = campo("fecha_fin")

    if fecha_inicio and fecha_inicio < hoy:
        flash("La fecha de inicio no puede ser una fecha pasada.", "danger")
        return redirect(url_for("novedades.listar"))
    if fecha_fin and fecha_fin < hoy:
        flash("La fecha de fin no puede ser una fecha pasada.", "danger")
        return redirect(url_for("novedades.listar"))
    if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
        flash("La fecha de fin no puede ser anterior a la fecha de inicio.", "danger")
        return redirect(url_for("novedades.listar"))

    novedad = {
        "tipo":          tipo,
        "destino":       campo("destino"),
        "empleo":        campo("empleo"),
        "localidad":     campo("localidad"),
        "fecha_inicio":  fecha_inicio,
        "fecha_fin":     fecha_fin,
        "observaciones": campo("observaciones"),
        "autor":         session["nombre"],
        "fecha_creacion": datetime.now(),
    }

    db.novedades.insert_one(novedad)
    flash("Novedad publicada correctamente.", "success")
    return redirect(url_for("novedades.listar"))


@novedades_bp.route("/eliminar/<novedad_id>", methods=["POST"])
@login_required
@gestor_required  # Admin y gestor pueden eliminar novedades
def eliminar(novedad_id):
    """Elimina una novedad por su ObjectId."""
    db = get_db()
    db.novedades.delete_one({"_id": ObjectId(novedad_id)})
    flash("Novedad eliminada.", "info")
    return redirect(url_for("novedades.listar"))
