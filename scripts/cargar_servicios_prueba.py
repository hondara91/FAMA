"""
scripts/cargar_servicios_prueba.py
Crea 20 anuncios de servicios usando los usuarios ya existentes:
  · 14 (70 %) → Viajes compartidos entre las bases (sin Rota-San Fernando)
  ·  6 (30 %) → Servicios: declaración de la renta, reparación de PC,
                            consultoría legal

Ejecutar dentro del contenedor:
    docker exec fama_web1 python scripts/cargar_servicios_prueba.py
"""
import os
import struct
import sys
import zlib
from datetime import datetime, timedelta

from pymongo import MongoClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config


# ─── PNG sin dependencias ─────────────────────────────────────────────────────

def _chunk(name: bytes, data: bytes) -> bytes:
    c = name + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def crear_png(r: int, g: int, b: int, size: int = 200) -> bytes:
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    fila = bytes([0]) + bytes([r, g, b] * size)
    idat = zlib.compress(fila * size)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


def nombre_foto(idx: int, num: int, slug: str) -> str:
    ts = datetime.now() + timedelta(seconds=idx * 3 + num)
    micro = 300000 + idx * 5000 + num * 700
    return f"{ts.strftime('%Y%m%d_%H%M%S')}_{micro:06d}_srv_{slug}_{num}.png"


# ─── 14 viajes compartidos (70 %) ────────────────────────────────────────────
# (usuario, tipo, categoria, titulo, precio, modalidad, telefono, ciudad,
#  descripcion, color_foto_RGB)

VIAJES = [
    (
        "amarsan", "ofrecer", "Viajes compartidos",
        "Plaza libre San Fernando → Ferrol (viernes tarde)",
        "30", "presencial", "956111001", "San Fernando",
        "Salgo todos los viernes entre 16:00 y 17:00 desde San Fernando hacia Ferrol "
        "en coche particular (Seat León, 4 plazas). Viaje directo por autovía, "
        "aproximadamente 8 horas. Gastos de gasolina y peajes a repartir. "
        "Contactar antes del miércoles para confirmar plaza.",
        ( 30, 100, 200),
    ),
    (
        "clopper", "ofrecer", "Viajes compartidos",
        "Rota → Madrid los domingos por la tarde",
        "25", "presencial", "956222002", "Rota",
        "Realizo el trayecto Rota-Madrid cada dos domingos, salida a las 15:00 desde "
        "el parking de la Base Naval. Volkswagen Passat, 3 plazas disponibles. "
        "Parada en Jerez para repostar. Precio aproximado según combustible.",
        (200,  80,  40),
    ),
    (
        "mgarrui", "ofrecer", "Viajes compartidos",
        "Cartagena → Ferrol — puente de diciembre",
        "45", "presencial", "968333003", "Cartagena",
        "Organizo viaje para el puente del 6 de diciembre, salida viernes noche "
        "desde Arsenal de Cartagena. Skoda Octavia con maletero grande, "
        "2 plazas libres. Ruta por Valencia-Zaragoza-Burgos. Se comparten gastos.",
        (180,  60, 160),
    ),
    (
        "jrodfer", "ofrecer", "Viajes compartidos",
        "Ferrol → Madrid — inicio de semana",
        "35", "presencial", "981444004", "Ferrol",
        "Salgo los lunes muy temprano (05:30) desde Base Naval de Ferrol hacia Madrid. "
        "Llego a Atocha/Retiro antes del mediodía. Toyota Corolla, 2 plazas. "
        "Autopista AP-9 + AP-6. Gastos a partes iguales entre los ocupantes.",
        ( 50, 130, 200),
    ),
    (
        "ltorveg", "ofrecer", "Viajes compartidos",
        "Madrid → San Fernando — Semana Santa",
        "40", "presencial", "917555005", "Madrid",
        "Viaje de regreso a San Fernando en Semana Santa, salida jueves por la tarde "
        "desde Getafe. Nissan Qashqai, 3 plazas. Ruta Sevilla-Cádiz, llegada "
        "viernes mañana. Precio orientativo según precio del carburante.",
        (240, 180,  30),
    ),
    (
        "msanmor", "buscar", "Viajes compartidos",
        "Busco plaza Ferrol → Cartagena cualquier fin de semana",
        "0", "presencial", "928666006", "Ferrol",
        "Busco plaza en coche para el trayecto Ferrol-Cartagena cualquier viernes "
        "o sábado de octubre. Destino Arsenal de Cartagena. Pago mi parte de "
        "gasolina y peajes sin problema. Equipaje ligero, sin mascotas.",
        (100, 180,  80),
    ),
    (
        "eromcas", "ofrecer", "Viajes compartidos",
        "Ferrol → San Fernando — cierre de permisos agosto",
        "38", "presencial", "981777007", "Ferrol",
        "Vuelta al sur al final del período de permisos de agosto. Salida domingo "
        "desde Ferrol a las 07:00, llegada San Fernando noche. Ford Kuga, "
        "2 plazas libres. Se comparten gastos de autopista y gasolina al 50 %.",
        (200, 100,  50),
    ),
    (
        "pjimort", "ofrecer", "Viajes compartidos",
        "Madrid → Cartagena todos los viernes",
        "22", "presencial", "917888008", "Madrid",
        "Regreso a Cartagena todos los viernes por la tarde, salida desde "
        "Vallecas a las 18:30. Peugeot 308, 3 plazas disponibles. Viaje "
        "por A-3, sin peaje de pago. Aproximadamente 4 horas de trayecto.",
        ( 60,  60, 200),
    ),
    (
        "cdiagon", "ofrecer", "Viajes compartidos",
        "Cartagena → Madrid — lunes laborables",
        "20", "presencial", "968999009", "Cartagena",
        "Incorporación a Madrid cada lunes desde Arsenal de Cartagena, salida "
        "a las 06:00. Renault Mégane, 2 plazas. Viaje por A-30 y A-3. "
        "Llego a Madrid capital antes de las 11:00. Gastos compartidos.",
        (220, 140,  30),
    ),
    (
        "fnavram", "ofrecer", "Viajes compartidos",
        "Madrid → Ferrol — puentes y fines de semana largos",
        "40", "presencial", "917000010", "Madrid",
        "Ofrezco plazas en mis viajes periódicos Madrid-Ferrol. Salida viernes tarde "
        "desde Barrio del Pilar, llegada Ferrol sábado madrugada. Hyundai Tucson, "
        "2 plazas. Autopista A-6. Gastos a partes iguales entre todos.",
        ( 30, 150, 100),
    ),
    (
        "imorrey", "ofrecer", "Viajes compartidos",
        "San Fernando → Cartagena — un viernes al mes",
        "28", "presencial", "956101011", "San Fernando",
        "Viajo a Cartagena el primer viernes de cada mes, salida a las 14:00 desde "
        "ESBA San Fernando. Seat Ateca, 3 plazas libres. Ruta Almería, "
        "aproximadamente 5 horas. Se reparten gastos de combustible y peajes.",
        (150,  50, 200),
    ),
    (
        "aruiser", "ofrecer", "Viajes compartidos",
        "Rota → Ferrol — permiso de verano",
        "50", "presencial", "956202012", "Rota",
        "Viaje largo Rota-Ferrol en julio para el permiso de verano. Salida sábado "
        "mañana temprano, con parada a comer en Salamanca. Dacia Duster, "
        "2-3 plazas. Autopista pagada en peaje. Gastos compartidos entre todos.",
        (200,  30,  80),
    ),
    (
        "mhermun", "ofrecer", "Viajes compartidos",
        "Madrid → Rota — incorporación después de permisos",
        "35", "presencial", "917303013", "Madrid",
        "Regreso a Rota el primer domingo de septiembre tras permisos de verano. "
        "Salida desde Madrid Atocha a las 08:00. Kia Sportage, 3 plazas. "
        "Ruta por Córdoba, llegada Rota por la tarde. Gastos a medias.",
        ( 80, 180,  30),
    ),
    (
        "aalomed", "ofrecer", "Viajes compartidos",
        "Ferrol → Cartagena — puente de noviembre",
        "42", "presencial", "981404014", "Ferrol",
        "Viaje Ferrol-Cartagena aprovechando el puente de Todos los Santos. "
        "Salida jueves noche desde Base Naval de Ferrol. Volvo V60, maletero "
        "grande. 2 plazas disponibles. Ruta por Burgos-Valencia. Gastos al 50 %.",
        ( 40, 120, 180),
    ),
]

# ─── 6 servicios profesionales (30 %) ────────────────────────────────────────

SERVICIOS = [
    (
        "pcasflo", "ofrecer", "Trabajos",
        "Declaración de la Renta — gestoría para personal militar",
        "40", "presencial", "956505015", "San Fernando",
        "Soy técnica en administración con 8 años de experiencia gestionando "
        "declaraciones de IRPF para personal de las FAS. Conozco a fondo las "
        "deducciones específicas por destinos, dietas, complementos de guardia "
        "y traslados forzosos. Primera consulta gratuita. Atención presencial "
        "en San Fernando o por videollamada. Precio 40 € por declaración.",
        (  0, 120, 200),
    ),
    (
        "rferbla", "ofrecer", "Trabajos",
        "Reparación de ordenadores y portátiles — domicilio o taller",
        "30", "presencial", "956606016", "Rota",
        "Técnico informático con titulación FPII en Sistemas Microinformáticos. "
        "Reparo portátiles, PC de sobremesa y Mac: cambio de pantalla, teclado, "
        "batería, disco SSD, instalación Windows/Linux, eliminación de virus. "
        "Desplazamiento gratuito en Rota y El Puerto de Santa María. "
        "Diagnóstico sin compromiso. Presupuesto previo siempre.",
        ( 50,  50, 180),
    ),
    (
        "nvazdel", "ofrecer", "Trabajos",
        "Consultoría legal — derecho administrativo y militar",
        "0", "online", "956707017", "Rota",
        "Oficial de la Armada con licenciatura en Derecho y Máster en Derecho "
        "Administrativo. Ofrezco orientación legal gratuita a compañeros en "
        "materias de derecho militar, recursos administrativos, expedientes "
        "disciplinarios, solicitudes de destino y reclamaciones ante la "
        "Administración. Consultas por correo o videollamada. Sin coste.",
        (160,  20,  80),
    ),
    (
        "lmolcan", "ofrecer", "Trabajos",
        "Declaración de la Renta online — entrega en 48 h",
        "35", "online", "956808018", "El Puerto de Santa María",
        "Gestiono tu declaración de la Renta de forma completamente online. "
        "Envíame tus datos fiscales por correo seguro y en 48 horas recibes "
        "el borrador revisado y presentado. Especialidad en rentas con "
        "múltiples pagadores, complementos FAS y propiedades en alquiler. "
        "Precio fijo 35 €, sin sorpresas. Más de 150 declaraciones realizadas.",
        ( 30, 170, 100),
    ),
    (
        "bsuaiba", "ofrecer", "Trabajos",
        "Reparación de ordenadores — servicio rápido en 24 h",
        "25", "presencial", "956909019", "El Puerto de Santa María",
        "Técnica certificada Microsoft y Apple. Especialidad en recuperación de "
        "datos, formateos con copia de seguridad, instalación de programas y "
        "optimización de equipos lentos. Trabajo desde casa, recogida y entrega "
        "a domicilio en El Puerto de Santa María y Rota. Presupuesto gratis. "
        "Más de 5 años de experiencia.",
        (220,  80, 160),
    ),
    (
        "fguepin", "ofrecer", "Trabajos",
        "Asesoría legal gratuita — trámites, recursos y contratos",
        "0", "online", "956010020", "El Puerto de Santa María",
        "Suboficial con Grado en Derecho y experiencia en asesoría jurídica "
        "dentro de la Armada. Ayudo con redacción de contratos de arrendamiento, "
        "recursos ante DGT, reclamaciones a seguros, consultas sobre herencias "
        "y trámites notariales. Totalmente gratuito para compañeros. "
        "Disponible por WhatsApp o videollamada. Sin compromiso.",
        ( 80, 160, 220),
    ),
]


# ─── Script principal ─────────────────────────────────────────────────────────

def main():
    cliente = MongoClient(Config.MONGO_URI)
    db = cliente[Config.MONGO_DB_NAME]
    col_usuarios = db.usuarios
    col_servicios = db.servicios

    carpeta_fotos = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "static", "uploads", "servicios"
    )
    os.makedirs(carpeta_fotos, exist_ok=True)

    todos = [("VIAJE",    v) for v in VIAJES] + \
            [("SERVICIO", s) for s in SERVICIOS]

    print("\n=== CREANDO ANUNCIOS DE SERVICIOS ===\n")
    creados = 0

    for idx, (etiq, datos) in enumerate(todos):
        (nombre_usr, tipo, categoria, titulo, precio,
         modalidad, telefono, ciudad, descripcion, color) = datos

        usuario = col_usuarios.find_one(
            {"nombre": {"$regex": f"^{nombre_usr}$", "$options": "i"}}
        )
        if not usuario:
            print(f"  [ERROR] Usuario '{nombre_usr}' no encontrado.")
            continue

        uid = str(usuario["_id"])
        slug = f"{nombre_usr}_{idx:02d}"
        nf = nombre_foto(idx, 1, slug)
        with open(os.path.join(carpeta_fotos, nf), "wb") as f:
            f.write(crear_png(*color, size=200))

        fecha_creacion = datetime.now() - timedelta(days=20 - idx)
        fecha_exp = fecha_creacion + timedelta(days=60)

        col_servicios.insert_one({
            "tipo":               tipo,
            "categoria":          categoria,
            "titulo":             titulo,
            "precio":             precio,
            "modalidad":          modalidad,
            "telefono":           telefono,
            "ciudad":             ciudad,
            "descripcion":        descripcion,
            "fotos":              [nf],
            "usuario_id":         uid,
            "nombre_usuario":     nombre_usr,
            "fecha_expiracion":   fecha_exp,
            "fecha_creacion":     fecha_creacion,
            "fecha_modificacion": fecha_creacion,
        })

        tag = f"[{etiq}]"
        print(f"  [OK] #{idx + 1:02d} {tag:<10} {titulo[:50]:<50}  @{nombre_usr}")
        creados += 1

    cliente.close()
    print(f"\n{'=' * 65}")
    print(f"  Viajes compartidos : 14")
    print(f"  Servicios          :  6")
    print(f"  Total creados      : {creados}")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    main()
