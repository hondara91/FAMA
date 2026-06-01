"""
utils/logs.py - Registro de eventos y exportacion de logs a PDF.

La coleccion 'logs' almacena dos tipos de entradas:
  'registro' -> acciones sobre usuarios o anuncios (crear, editar, eliminar)
  'control'  -> snapshots periodicos de contadores de la base de datos
"""
from datetime import datetime


def registrar_log(db, tipo, accion, usuario, detalle=""):
    """
    Inserta una entrada en la coleccion de logs.

    Parametros:
        tipo    -- 'registro' o 'control'
        accion  -- nombre corto de la operacion (ej: 'crear_vivienda')
        usuario -- nombre del usuario que ejecuto la accion
        detalle -- informacion adicional libre (opcional)
    """
    db.logs.insert_one({
        "tipo":    tipo,
        "accion":  accion,
        "usuario": usuario,
        "detalle": detalle,
        "fecha":   datetime.now(),
    })


def actualizar_contadores(db):
    """
    Guarda un snapshot de los contadores actuales de todas las colecciones.
    Se llama automaticamente tras cada operacion que crea o elimina documentos.
    """
    total_usuarios    = db.usuarios.count_documents({})
    total_viviendas   = db.viviendas.count_documents({})
    total_servicios   = db.servicios.count_documents({})
    total_compraventa = db.compraventa.count_documents({})
    total_ocio        = db.ocio.count_documents({})
    total_anuncios    = total_viviendas + total_servicios + total_compraventa + total_ocio

    db.logs.insert_one({
        "tipo":    "control",
        "accion":  "actualizar_contadores",
        "usuario": "sistema",
        "detalle": (
            f"Usuarios: {total_usuarios} | Anuncios totales: {total_anuncios} "
            f"(Viviendas: {total_viviendas}, Servicios: {total_servicios}, "
            f"Compraventa: {total_compraventa}, Ocio: {total_ocio})"
        ),
        "fecha": datetime.now(),
    })


def exportar_logs_pdf(logs, titulo="Logs FAMA"):
    """
    Genera un PDF con la lista de logs y devuelve un buffer BytesIO listo
    para send_file. Las importaciones de ReportLab son locales para no
    cargarlas en cada peticion.
    """
    import io
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4, title=titulo)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(titulo, styles["Title"]))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Normal"],
    ))
    elementos.append(Spacer(1, 20))

    datos = [["Fecha", "Tipo", "Accion", "Usuario", "Detalle"]]
    for log in logs:
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
            log.get("detalle", "")[:80],
        ])

    tabla = Table(datos, colWidths=[90, 60, 90, 80, 170])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("GRID",   (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(tabla)

    doc.build(elementos)
    buffer.seek(0)
    return buffer
