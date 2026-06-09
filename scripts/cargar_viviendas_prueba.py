"""
scripts/cargar_viviendas_prueba.py
Crea 20 usuarios con ID de 7 letras y 20 anuncios de vivienda con fotos en
las ciudades: Ferrol, Cartagena, Las Palmas, Madrid, San Fernando, Rota y
El Puerto de Santa María.

Convencion de ID: 1ª letra del nombre + 3 primeras del 1º apellido
                  + 3 primeras del 2º apellido  (siempre 7 caracteres)

Ejecutar desde la raiz del proyecto:
    python scripts/cargar_viviendas_prueba.py
"""
import os
import struct
import sys
import zlib
from datetime import datetime, timedelta

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config

PASSWORD = "Fama1234"

# ─── 20 usuarios ─────────────────────────────────────────────────────────────
# (nombre/ID, nombre_real, apellidos, email, color_avatar_RGB)
USUARIOS = [
    ("amarsan", "Ana",       "Martínez Sánchez",    "ana.martinez.sanchez@fama.mil",    (231,  76,  60)),
    ("clopper", "Carlos",    "López Pérez",          "carlos.lopez.perez@fama.mil",      ( 52, 152, 219)),
    ("mgarrui", "María",     "García Ruiz",          "maria.garcia.ruiz@fama.mil",       ( 46, 204, 113)),
    ("jrodfer", "Javier",    "Rodríguez Fernández",  "javier.rodriguez.fernandez@fama.mil", (155, 89, 182)),
    ("ltorveg", "Laura",     "Torres Vega",          "laura.torres.vega@fama.mil",       (243, 156,  18)),
    ("msanmor", "Miguel",    "Sánchez Moreno",       "miguel.sanchez.moreno@fama.mil",   ( 26, 188, 156)),
    ("eromcas", "Elena",     "Romero Castro",        "elena.romero.castro@fama.mil",     (233,  30,  99)),
    ("pjimort", "Pedro",     "Jiménez Ortiz",        "pedro.jimenez.ortiz@fama.mil",     ( 52,  73,  94)),
    ("cdiagon", "Carmen",    "Díaz González",        "carmen.diaz.gonzalez@fama.mil",    ( 39, 174,  96)),
    ("fnavram", "Francisco", "Navarro Ramos",        "francisco.navarro.ramos@fama.mil", (230, 126,  34)),
    ("imorrey", "Isabel",    "Morales Reyes",        "isabel.morales.reyes@fama.mil",    (192,  57,  43)),
    ("aruiser", "Antonio",   "Ruiz Serrano",         "antonio.ruiz.serrano@fama.mil",    ( 41, 128, 185)),
    ("mhermun", "Marta",     "Hernández Muñoz",      "marta.hernandez.munoz@fama.mil",   ( 39, 174,  96)),
    ("aalomed", "Álvaro",    "Alonso Medina",        "alvaro.alonso.medina@fama.mil",    (142,  68, 173)),
    ("pcasflo", "Pilar",     "Castro Flores",        "pilar.castro.flores@fama.mil",     ( 23, 165, 137)),
    ("rferbla", "Raúl",      "Fernández Blanco",     "raul.fernandez.blanco@fama.mil",   (211,  84,   0)),
    ("nvazdel", "Nuria",     "Vázquez Delgado",      "nuria.vazquez.delgado@fama.mil",   (  0, 131, 143)),
    ("lmolcan", "Luis",      "Molina Cano",          "luis.molina.cano@fama.mil",        (183,  28,  28)),
    ("bsuaiba", "Beatriz",   "Suárez Ibáñez",        "beatriz.suarez.ibanez@fama.mil",   ( 74, 144, 226)),
    ("fguepin", "Fernando",  "Guerrero Pino",        "fernando.guerrero.pino@fama.mil",  (119, 179,  91)),
]

# ─── 20 anuncios de vivienda ──────────────────────────────────────────────────
# Cada tupla: (nombre_usuario, tipo_oferta, tipo_inmueble, ciudad, zona,
#              habitaciones, banos, planta, precio, extras, telefono, descripcion,
#              color_foto1_RGB, color_foto2_RGB)
ANUNCIOS = [
    # ── Ferrol (3) ──────────────────────────────────────────────────────────
    (
        "amarsan", "alquiler", "Piso", "Ferrol", "Esteiro",
        "2", "1", "3", "650",
        ["garaje", "ascensor"],
        "981234567",
        "Piso luminoso en el barrio de Esteiro, a 10 minutos andando de la Base Naval "
        "de Ferrol. Salón amplio, cocina reformada y dos habitaciones exteriores. "
        "Comunidad tranquila con ascensor y plaza de garaje incluida.",
        (100, 149, 237), (220, 198, 153),
    ),
    (
        "jrodfer", "intercambio", "Chalet", "Ferrol", "Caranza",
        "4", "2", "1", "1200",
        ["garaje", "jardín", "mascotas"],
        "981345678",
        "Chalet adosado en Caranza con jardín privado y garaje doble. Cuatro "
        "habitaciones, dos baños completos y terraza cubierta. Interesado en "
        "intercambio con vivienda en Cádiz, San Fernando o Rota. Se valoran mascotas.",
        (110, 180, 100), (200, 150,  80),
    ),
    (
        "eromcas", "compartir", "Piso", "Ferrol", "Centro",
        "1", "1", "2", "350",
        ["ascensor"],
        "981456789",
        "Se ofrece habitación individual en piso compartido en el centro de Ferrol. "
        "Piso de 3 habitaciones, actualmente ocupado por dos militares. Cocina y "
        "baño comunes. Buen ambiente, se busca persona ordenada y responsable.",
        (180,  90, 130), (240, 210, 170),
    ),
    # ── Cartagena (3) ───────────────────────────────────────────────────────
    (
        "clopper", "alquiler", "Piso", "Cartagena", "Los Mateos",
        "3", "2", "4", "700",
        ["ascensor", "trastero"],
        "968123456",
        "Espacioso piso de tres habitaciones en Los Mateos, próximo al Arsenal "
        "Militar de Cartagena. Dos baños, cocina americana y amplio salón con "
        "vistas al mar. Trastero en planta baja incluido en el precio.",
        ( 60, 130, 200), (240, 220, 170),
    ),
    (
        "mgarrui", "alquiler", "Atico", "Cartagena", "Barrio Peral",
        "2", "1", "6", "800",
        ["ascensor", "terraza"],
        "968234567",
        "Ático con terraza panorámica en Barrio Peral. Vistas espectaculares al "
        "puerto histórico de Cartagena. Dos habitaciones, baño reformado y cocina "
        "equipada. Ideal para pareja o soltero destinado en la Base Naval.",
        (200,  80,  60), (255, 200, 100),
    ),
    (
        "ltorveg", "alquiler", "Estudio", "Cartagena", "Santa Lucía",
        "1", "1", "1", "420",
        [],
        "968345678",
        "Estudio bien comunicado en Santa Lucía, a 5 minutos en coche del Arsenal. "
        "Totalmente amueblado y equipado. Perfecto para un destino corto o personal "
        "que acaba de llegar a Cartagena sin familia.",
        (100, 200, 180), (230, 180, 120),
    ),
    # ── Las Palmas (3) ──────────────────────────────────────────────────────
    (
        "msanmor", "alquiler", "Piso", "Las Palmas", "Las Canteras",
        "2", "1", "3", "780",
        ["ascensor"],
        "928123456",
        "Piso a dos manzanas de la playa de Las Canteras. Salón con balcón, cocina "
        "independiente y dos habitaciones con armarios empotrados. Zona con todos "
        "los servicios y excelentes comunicaciones con la Base Naval.",
        ( 30, 160, 220), (255, 220,  80),
    ),
    (
        "pjimort", "intercambio", "Chalet", "Las Palmas", "Tafira",
        "3", "2", "1", "0",
        ["garaje", "jardín"],
        "928234567",
        "Chalet en Tafira con jardín y garaje. Ofrezco para intercambio con vivienda "
        "en la península, preferiblemente Ferrol, El Ferrol del Caudillo o zona de "
        "Cádiz. Tres habitaciones dobles, dos baños y gran salón-comedor.",
        (180, 140,  50), (120, 200, 100),
    ),
    (
        "cdiagon", "compartir", "Piso", "Las Palmas", "Guanarteme",
        "1", "1", "2", "380",
        ["mascotas"],
        "928345678",
        "Habitación en piso de cuatro personas en Guanarteme, a 5 minutos del "
        "mar. Piso amplio y bien ventilado. Se admiten mascotas pequeñas. "
        "Compañeros tranquilos, ambiente respetuoso.",
        (100, 180, 240), (240, 160,  80),
    ),
    # ── Madrid (3) ──────────────────────────────────────────────────────────
    (
        "fnavram", "alquiler", "Piso", "Madrid", "Moratalaz",
        "1", "1", "5", "920",
        ["ascensor"],
        "917123456",
        "Piso de una habitación en Moratalaz, bien comunicado con metro y autobús "
        "hacia el centro y las instalaciones militares. Cocina renovada, baño "
        "completo y salón con luz natural. Edificio con ascensor y portero.",
        (180,  60, 120), (220, 200, 150),
    ),
    (
        "imorrey", "alquiler", "Piso", "Madrid", "Vallecas",
        "2", "1", "3", "1100",
        ["ascensor", "garaje"],
        "917234567",
        "Piso de dos habitaciones en Villa de Vallecas con plaza de garaje. "
        "Bien comunicado con el barrio militar de Carabanchel y zona de Campamento. "
        "Edificio moderno con ascensor y zona comunitaria.",
        ( 80, 160,  80), (240, 220, 180),
    ),
    (
        "aruiser", "alquiler", "Estudio", "Madrid", "Carabanchel",
        "1", "1", "2", "780",
        ["ascensor"],
        "917345678",
        "Estudio totalmente amueblado en Carabanchel, ideal para destino en la "
        "capital. Cerca de varios cuarteles. Calefacción central incluida. "
        "Comunidad tranquila, segundo piso con ascensor.",
        ( 60,  80, 160), (200, 190, 230),
    ),
    # ── San Fernando (3) ────────────────────────────────────────────────────
    (
        "mhermun", "alquiler", "Piso", "San Fernando", "La Magdalena",
        "2", "1", "1", "590",
        ["mascotas"],
        "956123456",
        "Piso soleado en La Magdalena, barrio muy demandado por personal de la "
        "Armada. Dos habitaciones, salón, cocina y baño. A 10 minutos a pie del "
        "acuartelamiento. Se admiten mascotas con fianza adicional.",
        (220, 100,  60), (240, 210, 160),
    ),
    (
        "aalomed", "intercambio", "Piso", "San Fernando", "Camposoto",
        "3", "2", "2", "0",
        ["garaje"],
        "956234567",
        "Piso de tres habitaciones en Camposoto con garaje incluido. Ofrezco "
        "intercambio con piso similar en Ferrol, Cartagena o Rota. Bien cuidado, "
        "vecindario familiar y tranquilo, a 15 minutos de la playa de Camposoto.",
        (100, 180, 130), (230, 190, 100),
    ),
    (
        "pcasflo", "compartir", "Piso", "San Fernando", "Centro",
        "1", "1", "3", "300",
        ["ascensor"],
        "956345678",
        "Habitación disponible en piso del centro de San Fernando. Comparto con "
        "otra compañera de la Armada. Piso luminoso, limpio y bien equipado. "
        "Zona de parking gratuito cerca. Fianza de un mes.",
        (160,  80, 200), (210, 200, 240),
    ),
    # ── Rota (2) ────────────────────────────────────────────────────────────
    (
        "rferbla", "alquiler", "Piso", "Rota", "Costanilla",
        "2", "1", "2", "580",
        ["ascensor", "terraza"],
        "956456789",
        "Piso con terraza en Costanilla, Rota. Excelente ubicación a 8 minutos "
        "de la Base Naval de Rota. Dos habitaciones, salón con salida a terraza "
        "y cocina equipada. Edificio con ascensor y comunidad cuidada.",
        (200, 130,  40), (240, 220, 160),
    ),
    (
        "nvazdel", "alquiler", "Chalet", "Rota", "Urbanización Los Pinos",
        "4", "2", "1", "1100",
        ["garaje", "jardín", "piscina"],
        "956567890",
        "Chalet en urbanización Los Pinos con piscina comunitaria, jardín privado "
        "y garaje. Cuatro habitaciones, dos baños y gran salón con chimenea. "
        "Urbanización tranquila con seguridad, ideal para familias con niños.",
        ( 50, 150, 100), (180, 220, 170),
    ),
    # ── El Puerto de Santa María (3) ────────────────────────────────────────
    (
        "lmolcan", "alquiler", "Piso", "El Puerto de Santa María", "Las Redes",
        "2", "1", "3", "640",
        ["ascensor"],
        "956678901",
        "Piso en Las Redes, El Puerto de Santa María, a 20 minutos de la Base "
        "Naval de Rota. Dos habitaciones exteriores, salón amplio y cocina "
        "renovada. Transporte público frecuente a la base. Edificio con ascensor.",
        (100, 160, 220), (230, 200, 150),
    ),
    (
        "bsuaiba", "alquiler", "Atico", "El Puerto de Santa María", "El Tejar",
        "2", "2", "5", "750",
        ["terraza", "ascensor"],
        "956789012",
        "Ático dúplex en El Tejar con dos terrazas y vistas al río Guadalete. "
        "Dos habitaciones, dos baños, salón a doble altura y cocina americana. "
        "Edificio moderno con ascensor, a 25 minutos de la Base Naval de Rota.",
        (240,  80,  80), (255, 200, 120),
    ),
    (
        "fguepin", "compartir", "Piso", "El Puerto de Santa María", "Centro",
        "1", "1", "1", "290",
        [],
        "956890123",
        "Habitación en piso del centro del Puerto, compartido con dos militares "
        "destinados en Rota. Piso de 4 habitaciones con salón y dos baños. "
        "Perfecto para recién llegados que buscan ahorrar en alojamiento.",
        (120, 200,  80), (210, 230, 190),
    ),
]


# ─── Generador de PNG sin dependencias externas ───────────────────────────────

def _chunk(name: bytes, data: bytes) -> bytes:
    c = name + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def crear_png(r: int, g: int, b: int, size: int = 200) -> bytes:
    """Devuelve los bytes de un PNG cuadrado de color sólido."""
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
    """Genera un nombre de archivo con formato igual al que usa uploads.py."""
    ts = datetime.now() + timedelta(seconds=idx * 2 + num)
    micro = 100000 + idx * 3000 + num * 500
    return f"{ts.strftime('%Y%m%d_%H%M%S')}_{micro:06d}_vivienda_{etiqueta}_{num}.png"


# ─── Script principal ─────────────────────────────────────────────────────────

def main():
    cliente = MongoClient(Config.MONGO_URI)
    db = cliente[Config.MONGO_DB_NAME]
    col_usuarios = db.usuarios
    col_viviendas = db.viviendas

    carpeta_perfiles = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "static", "uploads", "perfiles"
    )
    carpeta_viviendas = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "static", "uploads", "viviendas"
    )
    os.makedirs(carpeta_perfiles, exist_ok=True)
    os.makedirs(carpeta_viviendas, exist_ok=True)

    # ── Crear usuarios ────────────────────────────────────────────────────────
    print("\n=== CREANDO USUARIOS ===")
    user_ids = {}   # nombre → ObjectId (string)

    for nombre, nombre_real, apellidos, email, (r, g, b) in USUARIOS:
        if col_usuarios.find_one({"nombre": {"$regex": f"^{nombre}$", "$options": "i"}}):
            doc = col_usuarios.find_one({"nombre": {"$regex": f"^{nombre}$", "$options": "i"}})
            user_ids[nombre] = str(doc["_id"])
            print(f"  [SKIP] {nombre} ya existe")
            continue

        nombre_foto_avatar = f"avatar_{nombre}.png"
        ruta_avatar = os.path.join(carpeta_perfiles, nombre_foto_avatar)
        with open(ruta_avatar, "wb") as f:
            f.write(crear_png(r, g, b, size=80))

        resultado = col_usuarios.insert_one({
            "nombre":               nombre,
            "nombre_real":          nombre_real,
            "apellidos":            apellidos,
            "email":                email,
            "password":             generate_password_hash(PASSWORD),
            "rol":                  "usuario",
            "foto_perfil":          nombre_foto_avatar,
            "pregunta_seguridad":   None,
            "respuesta_seguridad":  None,
            "debe_cambiar_password": False,
            "activo":               True,
            "validado":             True,
            "email_verificado":     True,
            "fecha_registro":       datetime.now(),
        })
        user_ids[nombre] = str(resultado.inserted_id)
        print(f"  [OK] {nombre} | {nombre_real} {apellidos} | {email}")

    # ── Crear anuncios de vivienda ────────────────────────────────────────────
    print("\n=== CREANDO ANUNCIOS DE VIVIENDA ===")
    creados = 0

    for idx, anuncio_data in enumerate(ANUNCIOS):
        (
            nombre_usr, tipo_oferta, tipo_inmueble, ciudad, zona,
            habitaciones, banos, planta, precio, extras, telefono, descripcion,
            color1, color2,
        ) = anuncio_data

        uid = user_ids.get(nombre_usr)
        if not uid:
            print(f"  [ERROR] Usuario '{nombre_usr}' no encontrado, saltando anuncio.")
            continue

        # Generar dos fotos PNG de colores distintos para el anuncio
        etiqueta = f"{nombre_usr}_{idx:02d}"
        fotos = []
        for num, (cr, cg, cb) in enumerate([(color1), (color2)], start=1):
            nf = nombre_foto(idx, num, etiqueta)
            ruta = os.path.join(carpeta_viviendas, nf)
            with open(ruta, "wb") as f:
                f.write(crear_png(cr, cg, cb, size=200))
            fotos.append(nf)

        fecha_creacion = datetime.now() - timedelta(days=30 - idx)
        fecha_exp = fecha_creacion + timedelta(days=90)

        col_viviendas.insert_one({
            "tipo_oferta":        tipo_oferta,
            "tipo_inmueble":      tipo_inmueble,
            "ciudad":             ciudad,
            "zona":               zona,
            "habitaciones":       habitaciones,
            "banos":              banos,
            "planta":             planta,
            "precio":             precio,
            "extras":             extras,
            "telefono":           telefono,
            "descripcion":        descripcion,
            "fotos":              fotos,
            "usuario_id":         uid,
            "nombre_usuario":     nombre_usr,
            "fecha_expiracion":   fecha_exp,
            "fecha_creacion":     fecha_creacion,
            "fecha_modificacion": fecha_creacion,
        })
        print(f"  [OK] #{idx + 1:02d} {tipo_oferta.upper()} · {tipo_inmueble} · {ciudad} · {precio}€ · @{nombre_usr}")
        creados += 1

    cliente.close()
    print(f"\n{'=' * 55}")
    print(f"  Usuarios procesados : {len(USUARIOS)}")
    print(f"  Anuncios creados    : {creados}")
    print(f"  Contraseña usuarios : {PASSWORD}")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()
