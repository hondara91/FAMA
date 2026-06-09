"""
scripts/cargar_compraventa_prueba.py
Crea 20 anuncios de compraventa (segunda mano) usando los usuarios
creados por cargar_viviendas_prueba.py.

Ejecutar dentro del contenedor:
    docker exec fama_web1 python scripts/cargar_compraventa_prueba.py
"""
import os
import struct
import sys
import zlib
from datetime import datetime, timedelta

from pymongo import MongoClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config


# ─── Generador de PNG sin dependencias externas ───────────────────────────────

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


def nombre_foto(idx: int, num: int, etiqueta: str) -> str:
    ts = datetime.now() + timedelta(seconds=idx * 3 + num)
    micro = 200000 + idx * 4000 + num * 600
    return f"{ts.strftime('%Y%m%d_%H%M%S')}_{micro:06d}_cv_{etiqueta}_{num}.png"


# ─── 20 anuncios de compraventa ───────────────────────────────────────────────
# (nombre_usuario, nombre_articulo, uco, precio, descripcion,
#  color_foto1_RGB, color_foto2_RGB)

ANUNCIOS = [
    (
        "amarsan",
        "Botas militares nuevas talla 43",
        "Base Naval de Ferrol",
        "45",
        "Botas de campaña reglamentarias talla 43, sin estrenar, en caja original. "
        "Me las regalaron pero no son mi talla. Suela Vibram, membrana impermeable, "
        "color negro. Recogida en Ferrol o envío a cargo del comprador.",
        ( 60,  40,  20), (120,  80,  40),
    ),
    (
        "clopper",
        "Tabla de surf 7'2 + funda",
        "Arsenal de Cartagena",
        "280",
        "Tabla de surf Mick Fanning Softboard 7'2 con funda acolchada incluida. "
        "Un año de uso, buen estado, algún golpe menor en el rail sin importancia. "
        "Ideal para iniciarse o días de olas pequeñas. Recogida en Cartagena.",
        ( 30, 150, 200), (255, 220,  60),
    ),
    (
        "mgarrui",
        "Patinete eléctrico Xiaomi Mi Scooter 3",
        "Arsenal de Cartagena",
        "190",
        "Patinete Xiaomi Mi Electric Scooter 3, autonomía 30 km, velocidad máx. "
        "25 km/h. 18 meses de uso, ruedas nuevas hace 2 meses, frenos revisados. "
        "Incluye candado antirrobo y bolsa de transporte. Factura disponible.",
        ( 20,  20,  20), (100, 100, 100),
    ),
    (
        "jrodfer",
        "Bicicleta de montaña Trek Marlin 5",
        "Base Naval de Ferrol",
        "350",
        "BTT Trek Marlin 5 talla M, cuadro aluminio, frenos de disco hidráulicos "
        "Shimano, horquilla suspensión 100 mm. Dos años de uso, bien mantenida, "
        "última revisión hace 3 meses. Se vende por traslado de destino.",
        ( 50, 150,  50), (200, 200, 200),
    ),
    (
        "ltorveg",
        "Uniforme de campaña OTAN talla S",
        "Arsenal de Cartagena",
        "35",
        "Traje de campaña completo (guerrera + pantalón) patrón pixelado OTAN, "
        "talla S, poco uso. En perfecto estado, sin manchas ni desgarros. "
        "Ideal como repuesto o para maniobras. Recogida en Cartagena.",
        ( 80, 110,  60), (160, 180, 120),
    ),
    (
        "msanmor",
        "Kayak individual Sevylor Quikpak K1",
        "Base Naval de Las Palmas",
        "120",
        "Kayak hinchable Sevylor Quikpak K1, capacidad 113 kg, incluye remo de "
        "aluminio partido, bomba y mochila de transporte. Perfecto estado, usado "
        "5-6 veces. Ideal para explorar la costa canaria en días libres.",
        (  0, 100, 200), (200, 230, 255),
    ),
    (
        "eromcas",
        "Mochila táctica 50L Mil-Tec",
        "Base Naval de Ferrol",
        "55",
        "Mochila militar Mil-Tec assault pack 50 litros, color verde oliva, sistema "
        "Molle, correas acolchadas con soporte lumbar. Excelente estado, poca "
        "suciedad lavable. Costó 90€ nueva. Envío incluido península.",
        ( 60,  90,  40), (120, 140,  80),
    ),
    (
        "pjimort",
        "Casco moto Shoei NXR2 talla L",
        "Base Naval de Las Palmas",
        "230",
        "Casco integral Shoei NXR2 talla L, color negro mate, homologación "
        "ECE 22.06, con pinlock incluido. 14 meses de uso, sin golpes ni caídas, "
        "interior lavado. Vendo por cambio de talla. Factura y caja originales.",
        ( 20,  20,  20), ( 80,  80,  80),
    ),
    (
        "cdiagon",
        "Set raquetas de pádel Head Delta Pro",
        "Base Naval de Las Palmas",
        "160",
        "Pack 2 raquetas Head Delta Pro + 3 pelotas Head en bote + paletero "
        "doble. Nivel iniciación-intermedio. Dos años de uso recreativo, "
        "grips cambiados hace 1 mes. Vendo porque me paso al tenis.",
        (255, 100,   0), (255, 200, 100),
    ),
    (
        "fnavram",
        "Tienda de campaña Coleman Darwin 4+",
        "Estado Mayor de la Armada — Madrid",
        "90",
        "Tienda Coleman Darwin 4+ para 4-5 personas, doble techo, costuras "
        "termoselladas, suelo cosido. Usada 3 veces de acampada, en perfecto "
        "estado con todas sus piquetas y varillas. Bolsa de transporte incluida.",
        (  0, 130,  60), (150, 200, 150),
    ),
    (
        "imorrey",
        "Botas montaña Gore-Tex Lowa Renegade talla 38",
        "Estado Mayor de la Armada — Madrid",
        "115",
        "Botas Lowa Renegade GTX mid talla 38, impermeables, suela Vibram. "
        "Temporada y media de uso, estado muy bueno. Se venden por cambio de "
        "número. Incluyen plantillas originales y caja. Envío peninsular.",
        (140,  80,  40), (200, 160, 100),
    ),
    (
        "aruiser",
        "Bicicleta eléctrica Decathlon E-ST 500",
        "Estado Mayor de la Armada — Madrid",
        "680",
        "E-bike Decathlon Rockrider E-ST 500 talla M, motor central 250W, "
        "batería 500 Wh (autonomía 70 km), frenos hidráulicos. 8 meses de uso, "
        "perfecto estado, incluye cargador y manual. Vendo por traslado.",
        (200, 150,  30), (240, 200,  80),
    ),
    (
        "mhermun",
        "Pelota rugby Gilbert Barbarian talla 5",
        "ESBA — San Fernando",
        "18",
        "Pelota de rugby Gilbert Barbarian match talla 5, muy poco uso, casi "
        "nueva. Se quedó en casa cuando me fui de destino. Ideal para "
        "entrenamiento o partidos informales. Envío incluido.",
        (200,  60,  30), (240, 120,  80),
    ),
    (
        "aalomed",
        "Saco de dormir Marmot Trestles Elite Eco 0°",
        "ESBA — San Fernando",
        "140",
        "Saco de dormir Marmot Trestles Elite Eco confort 0°C, formato "
        "momia, relleno sintético reciclado, cremallera izquierda. Talla "
        "regular. Usado en 2 campañas, lavado y en perfecto estado.",
        ( 30,  30, 160), (100, 100, 220),
    ),
    (
        "pcasflo",
        "Kit completo de buceo Mares Puck Pro",
        "ESBA — San Fernando",
        "320",
        "Equipo de buceo: ordenador Mares Puck Pro + regulador Mares Abyss "
        "22 Navy + chaleco jacket talla M. Todo revisado y en perfecto estado. "
        "Se vende junto por traslado a destino sin mar. Factura de todo.",
        (  0, 100, 200), (  0, 180, 240),
    ),
    (
        "rferbla",
        "Material escalada — arnés + cuerda 60m + varios",
        "Base Naval de Rota",
        "180",
        "Pack escalada: arnés Black Diamond Momentum talla M + cuerda Beal "
        "Apex 9.5mm 60m + 10 cintas exprés Petzl + casco Petzl Boreo. Todo "
        "en buen estado, revisado por monitor federado. Ideal iniciarse.",
        (200, 100,   0), (240, 160,  60),
    ),
    (
        "nvazdel",
        "Chaleco táctico portaplacas talla L",
        "Base Naval de Rota",
        "70",
        "Chaleco táctico portaplacas talla L, sistema Molle, 6 portacargadores "
        "frontales, panel dorsal. Color coyote. Sin uso operativo real, comprado "
        "para prácticas. En perfecto estado. Recogida en Rota.",
        (200, 160,  80), (240, 200, 120),
    ),
    (
        "lmolcan",
        "Paddle surf SUP Decathlon 10'",
        "BN El Puerto de Santa María",
        "310",
        "Tabla paddle surf hinchable Itiwit 10' con remo ajustable de fibra, "
        "bomba doble acción, leash y mochila. Dos temporadas de uso, sin pinchazos "
        "ni reparaciones. Perfecta para bahía y aguas tranquilas.",
        (  0, 180, 200), (100, 220, 240),
    ),
    (
        "bsuaiba",
        "Mancuernas ajustables Bowflex SelectTech 552",
        "BN El Puerto de Santa María",
        "220",
        "Par de mancuernas Bowflex SelectTech 552, ajuste de 2 a 24 kg en "
        "intervalos de 2 kg, mecanismo selector rápido. Como nuevas, apenas "
        "usadas (teletrabajo me quitó el tiempo). Con soporte de suelo.",
        (180,  40,  40), (220, 100, 100),
    ),
    (
        "fguepin",
        "PlayStation 5 Disc Edition + 3 juegos",
        "BN El Puerto de Santa María",
        "420",
        "PS5 edición disco en perfecto estado, mando DualSense + mando extra "
        "color blanco. Incluye FIFA 25, God of War Ragnarök y Hogwarts Legacy. "
        "Todos los juegos en físico con cajas. Vendo por falta de tiempo.",
        (255, 255, 255), (  0,  70, 180),
    ),
]


# ─── Script principal ─────────────────────────────────────────────────────────

def main():
    cliente = MongoClient(Config.MONGO_URI)
    db = cliente[Config.MONGO_DB_NAME]
    col_usuarios  = db.usuarios
    col_compraventa = db.compraventa

    carpeta_fotos = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "static", "uploads", "compraventa"
    )
    os.makedirs(carpeta_fotos, exist_ok=True)

    print("\n=== CREANDO ANUNCIOS DE COMPRAVENTA ===")
    creados = 0

    for idx, (nombre_usr, nombre_art, uco, precio, descripcion, c1, c2) in enumerate(ANUNCIOS):
        usuario = col_usuarios.find_one(
            {"nombre": {"$regex": f"^{nombre_usr}$", "$options": "i"}}
        )
        if not usuario:
            print(f"  [ERROR] Usuario '{nombre_usr}' no encontrado, saltando.")
            continue

        uid = str(usuario["_id"])

        # Generar dos fotos de color
        etiqueta = f"{nombre_usr}_{idx:02d}"
        fotos = []
        for num, (cr, cg, cb) in enumerate([c1, c2], start=1):
            nf = nombre_foto(idx, num, etiqueta)
            with open(os.path.join(carpeta_fotos, nf), "wb") as f:
                f.write(crear_png(cr, cg, cb, size=200))
            fotos.append(nf)

        fecha_creacion = datetime.now() - timedelta(days=25 - idx)
        fecha_exp = fecha_creacion + timedelta(days=60)

        col_compraventa.insert_one({
            "nombre_articulo":    nombre_art,
            "uco":                uco,
            "precio":             precio,
            "descripcion":        descripcion,
            "es_merchandising":   False,
            "unidad_armada":      "",
            "fotos":              fotos,
            "usuario_id":         uid,
            "nombre_usuario":     nombre_usr,
            "fecha_expiracion":   fecha_exp,
            "fecha_creacion":     fecha_creacion,
            "fecha_modificacion": fecha_creacion,
        })
        print(f"  [OK] #{idx + 1:02d} {nombre_art[:45]:<45} {precio}€  @{nombre_usr}")
        creados += 1

    cliente.close()
    print(f"\n{'=' * 60}")
    print(f"  Anuncios de compraventa creados: {creados}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
