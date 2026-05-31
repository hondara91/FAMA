"""
utils/helpers.py - Funciones auxiliares transversales de FAMA.

Contiene:
  - Decoradores de control de acceso (login, rol admin, rol gestor).
  - Registro de eventos en la coleccion de logs de MongoDB.
  - Actualizacion de contadores del log de control.
  - Exportacion de logs a PDF con ReportLab.
"""
from functools import wraps
from datetime import datetime

from flask import session, redirect, url_for, flash


# ── Decoradores de control de acceso ─────────────────────────────────────────
#
# Los decoradores se apilan sobre las rutas en este orden recomendado:
#   @login_required    <- primero: si no esta logado, no tiene sentido comprobar rol
#   @admin_required    <- segundo: comprueba el rol una vez confirmada la sesion
#
# @wraps conserva el nombre y docstring de la funcion original (f.__name__),
# imprescindible para que Flask no detecte endpoints duplicados al apilar decoradores.

def login_required(f):
    """Redirige al login si el usuario no ha iniciado sesion."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Comprueba que 'user_id' existe en la sesion de Flask (cookie firmada)
        if "user_id" not in session:
            flash("Debes iniciar sesion para acceder.", "warning")
            return redirect(url_for("auth.login"))
        # Si la sesion es valida, ejecuta la funcion de vista original
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Permite el acceso solo a usuarios con rol 'admin'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Solo el rol exactamente 'admin' puede acceder; 'gestor' no es suficiente
        if session.get("rol") != "admin":
            flash("Acceso restringido a administradores.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


def gestor_required(f):
    """Permite el acceso a usuarios con rol 'gestor' o 'admin'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 'admin' incluye todos los permisos de 'gestor' (jerarquia de roles)
        if session.get("rol") not in ("admin", "gestor"):
            flash("Acceso restringido a gestores y administradores.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


# ── Registro de logs ──────────────────────────────────────────────────────────
#
# La coleccion 'logs' almacena dos tipos de entradas:
#   'registro' -> acciones sobre usuarios o anuncios (crear, editar, eliminar)
#   'control'  -> snapshots periodicos de contadores de la base de datos

def registrar_log(db, tipo, accion, usuario, detalle=""):
    """
    Inserta una entrada en la coleccion de logs.

    Parametros:
        tipo    -- 'registro' o 'control' (clasifica el log en la vista admin)
        accion  -- nombre corto de la operacion realizada (ej: 'crear_vivienda')
        usuario -- nombre del usuario que ejecuto la accion
        detalle -- informacion adicional libre (opcional)
    """
    db.logs.insert_one({
        "tipo": tipo,
        "accion": accion,
        "usuario": usuario,
        "detalle": detalle,
        "fecha": datetime.now(),  # Timestamp del momento exacto de la accion
    })


def actualizar_contadores(db):
    """
    Guarda un snapshot de los contadores actuales de todas las colecciones.

    Se llama automaticamente despues de cada operacion que crea o elimina
    documentos, para mantener un historial de la evolucion de los datos.
    """
    # Contar documentos en cada coleccion de negocio
    total_usuarios    = db.usuarios.count_documents({})
    total_viviendas   = db.viviendas.count_documents({})
    total_servicios   = db.servicios.count_documents({})
    total_compraventa = db.compraventa.count_documents({})
    total_ocio        = db.ocio.count_documents({})

    # Suma de todos los modulos de anuncios (excluye usuarios)
    total_anuncios = total_viviendas + total_servicios + total_compraventa + total_ocio

    # Insertar el snapshot con tipo 'control' para distinguirlo de los logs de accion
    db.logs.insert_one({
        "tipo": "control",
        "accion": "actualizar_contadores",
        "usuario": "sistema",  # Accion automatica, no iniciada por ningun usuario
        "detalle": (
            f"Usuarios: {total_usuarios} | Anuncios totales: {total_anuncios} "
            f"(Viviendas: {total_viviendas}, Servicios: {total_servicios}, "
            f"Compraventa: {total_compraventa}, Ocio: {total_ocio})"
        ),
        "fecha": datetime.now(),
    })


# ── Exportacion de logs a PDF ─────────────────────────────────────────────────

def exportar_logs_pdf(logs, titulo="Logs FAMA"):
    """
    Genera un PDF con la lista de logs y devuelve un buffer de bytes listo
    para enviarse como descarga HTTP con Flask's send_file.

    Las importaciones de ReportLab son locales para no cargar la libreria
    en cada peticion, solo cuando se solicita la exportacion.
    """
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    # Buffer en memoria: evita escribir un archivo temporal en disco
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=titulo)
    styles = getSampleStyleSheet()
    elementos = []  # Lista de "flowables" que ReportLab renderizara en orden

    # ── Cabecera del documento ────────────────────────────────────────────────
    elementos.append(Paragraph(titulo, styles["Title"]))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Normal"],
    ))
    elementos.append(Spacer(1, 20))

    # ── Construccion de la tabla de datos ─────────────────────────────────────
    # Primera fila = cabecera de columnas
    datos = [["Fecha", "Tipo", "Accion", "Usuario", "Detalle"]]

    for log in logs:
        # Formatear la fecha si es un objeto datetime; convertir a string si no
        fecha = (
            log.get("fecha", "").strftime("%d/%m/%Y %H:%M")
            if isinstance(log.get("fecha"), datetime)
            else str(log.get("fecha", ""))
        )
        datos.append([
            fecha,
            log.get("tipo", ""),
            log.get("accion", ""),
            log.get("usuario", ""),
            log.get("detalle", "")[:80],  # Limitar el detalle para que quepa en la celda
        ])

    # Anchos de columna en puntos (suma total ~490 pt para A4 con margenes)
    tabla = Table(datos, colWidths=[90, 60, 90, 80, 170])

    # ── Estilo visual de la tabla ─────────────────────────────────────────────
    tabla.setStyle(TableStyle([
        # Fila de cabecera: fondo azul marino FAMA y texto blanco
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
        # Filas alternas en blanco y gris claro para facilitar la lectura
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("GRID",   (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(tabla)

    # Construir el PDF y rebobinar el buffer al inicio para que send_file lo lea
    doc.build(elementos)
    buffer.seek(0)
    return buffer
