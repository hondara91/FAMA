"""
scripts/cargar_ocio_prueba.py
Crea 20 eventos de ocio variados usando los usuarios ya existentes.
  · 10 Deporte  (50 %)
  ·  6 Cultural (30 %)
  ·  4 Otros    (20 %)

Fechas a partir de julio 2026 para que aparezcan como próximos eventos.
Cada evento lleva algunos usuarios ya inscritos para dar realismo.

Ejecutar dentro del contenedor:
    docker exec fama_web1 python scripts/cargar_ocio_prueba.py
"""
import os
import sys
from datetime import datetime

from pymongo import MongoClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config


# ─── Eventos ──────────────────────────────────────────────────────────────────
# Cada tupla: (tipo_evento, titulo, fecha, hora, lugar, aforo_maximo,
#              nombre_usuario_creador, descripcion, inscritos_nombres)

EVENTOS = [

    # ══════════════════════════════════════════════════════════════════════════
    # DEPORTE  (10)
    # ══════════════════════════════════════════════════════════════════════════
    (
        "Deporte",
        "Torneo de fútbol sala intercuarteles — San Fernando",
        "2026-07-05", "10:00",
        "Pabellón deportivo Base Aeronaval de San Fernando",
        32,
        "amarsan",
        "Torneo de fútbol sala abierto a todo el personal destinado en San Fernando "
        "y Rota. Se formarán equipos de 5 jugadores + portero. Fase de grupos y "
        "eliminatorias directas. Se entregará trofeo y medallas al equipo campeón. "
        "Inscripción por equipos hasta el 1 de julio. Árbitros del propio cuartel.",
        ["clopper", "jrodfer", "msanmor", "pjimort", "rferbla", "aalomed", "fguepin", "aruiser"],
    ),
    (
        "Deporte",
        "Ruta en bicicleta de carretera — costa de Cartagena",
        "2026-07-12", "08:00",
        "Parking Arsenal de Cartagena (puerta principal)",
        20,
        "clopper",
        "Salida ciclista de 70 km por la costa de Cartagena: Arsenal → Cabo de Palos "
        "→ La Manga → vuelta por el Mar Menor. Nivel medio, sin competición. "
        "Obligatorio casco y luces. Se esperará en los puntos de reagrupamiento. "
        "Avituallamientos en km 35. Llevar al menos 2 bidones de agua.",
        ["mgarrui", "ltorveg", "eromcas", "nvazdel", "imorrey", "aruiser"],
    ),
    (
        "Deporte",
        "Campeonato de natación en aguas abiertas — Ferrol",
        "2026-07-19", "09:30",
        "Playa de A Malata, Ferrol",
        40,
        "mgarrui",
        "Primera edición del campeonato de natación en aguas abiertas de la Base "
        "Naval de Ferrol. Distancias: 750 m (principiantes) y 1.500 m (avanzados). "
        "Clasificación por categorías: tropa, suboficiales y oficiales. "
        "Obligatorio traje de neopreno. Cronometraje oficial. Trofeos para los tres primeros.",
        ["jrodfer", "eromcas", "pjimort", "mhermun", "rferbla", "ltorveg"],
    ),
    (
        "Deporte",
        "Jornada de surf para todos los niveles — Cartagena",
        "2026-08-02", "09:00",
        "Playa de Calblanque, Cartagena",
        15,
        "ltorveg",
        "Jornada de iniciación y perfeccionamiento al surf organizada por personal "
        "de la Base Naval. Monitor federado presente todo el día. Tablas y "
        "neoprenos disponibles sin coste. Apta para todos los niveles, incluidos "
        "los que nunca han surfeado. Transporte en minibús desde el Arsenal a las 08:30.",
        ["clopper", "mgarrui", "msanmor", "cdiagon", "bsuaiba"],
    ),
    (
        "Deporte",
        "Trail running nocturno — Sierra de la Plata, Rota",
        "2026-08-15", "21:00",
        "Salida: Puerta Este Base Naval de Rota",
        25,
        "rferbla",
        "Carrera nocturna de 12 km por los senderos costeros de la Sierra de la Plata. "
        "Salida y llegada en la Base Naval de Rota. Frontal obligatorio. "
        "Nivel intermedio-alto, desnivel acumulado 350 m. Avituallamiento en km 6. "
        "Se entregará dorsal y camiseta técnica a todos los participantes inscritos.",
        ["nvazdel", "amarsan", "mhermun", "pcasflo", "aalomed", "aruiser"],
    ),
    (
        "Deporte",
        "Torneo de pádel por parejas — Madrid",
        "2026-09-06", "10:00",
        "Club Deportivo Cuartel General de la Armada, Madrid",
        24,
        "fnavram",
        "Torneo de pádel por parejas mixtas abierto al personal destinado en Madrid. "
        "Formato cuadro eliminatorio, 12 parejas máximo. Nivel recreativo, no federado. "
        "Pistas reservadas todo el día. Raquetas disponibles para préstamo. "
        "Inscripción antes del 1 de septiembre indicando nombre de compañero/a.",
        ["imorrey", "aruiser", "mhermun", "lmolcan", "bsuaiba", "fguepin", "cdiagon"],
    ),
    (
        "Deporte",
        "Clase de yoga y meditación semanal — Ferrol",
        "2026-09-13", "18:00",
        "Sala polivalente Residencia Militar Ferrol",
        20,
        "eromcas",
        "Clases semanales de yoga y técnicas de mindfulness para personal militar. "
        "Profesora titulada Yaneth González, especializada en gestión del estrés. "
        "Sesiones de 60 minutos todos los jueves. Traer esterilla o solicitar "
        "préstamo en recepción. Completamente gratuito. Abierto a familias del personal.",
        ["pcasflo", "nvazdel", "bsuaiba", "ltorveg", "mgarrui"],
    ),
    (
        "Deporte",
        "Jornada de buceo recreativo — Las Palmas",
        "2026-09-20", "08:00",
        "Club Náutico Las Palmas — muelle deportivo",
        12,
        "msanmor",
        "Inmersiones en el pecio del Arona y la Reserva Marina de Sardina del Norte. "
        "Mínimo certificación Open Water. Se hacen dos inmersiones (mañana y tarde). "
        "Equipo completo incluido en la tarifa del club (35 € por persona, no incluidos). "
        "Coordinación con instructores del Centro de Buceo de la Armada.",
        ["pjimort", "cdiagon", "clopper"],
    ),
    (
        "Deporte",
        "Torneo de tenis individual — San Fernando",
        "2026-10-03", "09:00",
        "Pistas de tenis ESBA, San Fernando",
        16,
        "mhermun",
        "Torneo de tenis individual en las pistas de la Escuela de Suboficiales. "
        "Cuadro de 16 jugadores, formato eliminatorio al mejor de tres sets. "
        "Nivel recreativo. Árbitros voluntarios. Trofeo para campeón y finalista. "
        "Inscripción antes del 28 de septiembre. Prestar raqueta si no tienes.",
        ["aalomed", "pcasflo", "amarsan", "rferbla", "lmolcan"],
    ),
    (
        "Deporte",
        "Ruta de senderismo — Picos de Europa desde Madrid",
        "2026-10-17", "06:00",
        "Salida: Estación de Autobuses Méndez Álvaro, Madrid",
        30,
        "imorrey",
        "Excursión de un día a los Picos de Europa. Ruta circular Lagos de Covadonga "
        "(14 km, nivel medio). Autobús privado incluido en el precio (15 € por persona). "
        "Almuerzo de bocadillo en el refugio de Vega de Ario. Regreso Madrid 22:00. "
        "Imprescindible calzado de montaña. Plazas muy limitadas.",
        ["fnavram", "aruiser", "mhermun", "bsuaiba", "fguepin", "lmolcan", "cdiagon"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # CULTURAL  (6)
    # ══════════════════════════════════════════════════════════════════════════
    (
        "Cultural",
        "Visita guiada al Museo Naval de Madrid",
        "2026-07-25", "11:00",
        "Museo Naval, Paseo del Prado 5, Madrid",
        20,
        "aruiser",
        "Visita guiada exclusiva para el personal de la Armada al Museo Naval de Madrid. "
        "El guía especializado mostrará la carta de Juan de la Cosa (1500), "
        "el astrolabio más antiguo del mundo y la colección de maquetas históricas. "
        "Duración: 2 horas. Entrada gratuita con TIP/carné militar. Grupo máximo 20 personas.",
        ["fnavram", "imorrey", "mhermun", "bsuaiba", "pcasflo", "nvazdel"],
    ),
    (
        "Cultural",
        "Concierto Banda de Música de la Armada — San Fernando",
        "2026-08-22", "20:00",
        "Plaza del Rey, San Fernando",
        200,
        "pcasflo",
        "La Banda de Música de la Infantería de Marina ofrecerá un concierto al aire libre "
        "en la Plaza del Rey de San Fernando. Programa: marchas militares, pasodobles "
        "y un bloque de música de cine. Entrada libre y gratuita para todo el público. "
        "Se recomienda llevar silla o manta. En caso de lluvia, se traslada al auditorio.",
        ["amarsan", "rferbla", "aalomed", "lmolcan", "fguepin", "eromcas", "mhermun"],
    ),
    (
        "Cultural",
        "Excursión al Castillo de la Concepción — Cartagena",
        "2026-09-12", "10:30",
        "Castillo de la Concepción, Cartagena (salida desde Arsenal)",
        25,
        "jrodfer",
        "Visita histórica al Castillo de la Concepción y el Parque Arqueológico de "
        "Cartagena. Guía especializada en historia militar romana y medieval. "
        "Incluye entrada al MURAM (Museo Regional de Arte Moderno). Duración: mañana completa. "
        "Transporte en minibús desde el Arsenal a las 10:00. Precio entrada: 6 €.",
        ["clopper", "mgarrui", "ltorveg", "cdiagon", "pjimort"],
    ),
    (
        "Cultural",
        "Noche de cine clásico bélico — Base Naval Rota",
        "2026-09-25", "21:30",
        "Cine del Casino de Suboficiales, Base Naval de Rota",
        60,
        "nvazdel",
        "Ciclo de cine bélico clásico: proyección de 'El puente sobre el río Kwai' "
        "(1957) en versión original subtitulada. Presentación a cargo del Teniente de "
        "Navío historiador D. Rafael Sánchez. Debate posterior sobre la figura del oficial "
        "en los conflictos del s. XX. Entrada libre. Se servirán bebidas en el bar del casino.",
        ["rferbla", "mhermun", "pcasflo", "aalomed", "lmolcan"],
    ),
    (
        "Cultural",
        "Visita a los astilleros históricos de Ferrol",
        "2026-10-10", "10:00",
        "Astilleros de Navantia, Ferrol — entrada por puerta B",
        30,
        "jrodfer",
        "Tour exclusivo por los astilleros de Navantia en Ferrol: diques históricos del "
        "siglo XVIII, sala de gálibos y los actuales procesos de construcción naval. "
        "Duración 3 horas. Requiere DNI o TIP en la entrada. Acceso restringido a personal "
        "en activo y familiares directos. Plazas muy limitadas, inscripción obligatoria.",
        ["amarsan", "eromcas", "mgarrui", "msanmor", "clopper", "jrodfer"],
    ),
    (
        "Cultural",
        "Exposición fotográfica 'La Armada en el mundo' — Madrid",
        "2026-11-05", "12:00",
        "Sala de exposiciones Cuartel General de la Armada, Madrid",
        100,
        "fnavram",
        "Inauguración de la exposición fotográfica sobre las misiones internacionales "
        "de la Armada Española en los últimos 25 años: Operación Atalanta, UNIFIL, "
        "EUNAVFOR MED y misiones humanitarias. Más de 80 fotografías de autores "
        "militares. Visita libre de 10:00 a 20:00 durante todo noviembre. Entrada gratuita.",
        ["imorrey", "aruiser", "fguepin", "bsuaiba", "lmolcan"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # OTROS  (4)
    # ══════════════════════════════════════════════════════════════════════════
    (
        "Otros",
        "Barbacoa de verano y convivencia — San Fernando",
        "2026-07-18", "13:00",
        "Zona verde del acuartelamiento de San Fernando",
        80,
        "aalomed",
        "Barbacoa anual de convivencia para el personal y sus familias. "
        "Carne, ensaladas y bebidas a cargo del rancho del cuartel. "
        "Actividades para niños: hinchables, gymkana y pintacaras. "
        "Colaboración voluntaria de 5 € por persona para gastos. "
        "Música en directo a cargo de un compañero guitarrista. ¡Toda la familia bienvenida!",
        ["amarsan", "pcasflo", "mhermun", "eromcas", "rferbla", "lmolcan", "bsuaiba", "fguepin"],
    ),
    (
        "Otros",
        "Torneo de ajedrez — Base Naval de Cartagena",
        "2026-08-29", "16:00",
        "Sala de reuniones — Residencia de Oficiales, Cartagena",
        20,
        "pjimort",
        "Torneo de ajedrez por eliminatorias, abierto a todo el personal del Arsenal. "
        "Sistema suizo a 5 rondas. Tiempo de juego: 15 minutos por jugador. "
        "Tableros y piezas disponibles. Clasificación general y por categorías. "
        "Trofeo al campeón y diploma para todos los participantes.",
        ["clopper", "mgarrui", "ltorveg", "cdiagon", "jrodfer"],
    ),
    (
        "Otros",
        "Noche de juegos de mesa — Ferrol",
        "2026-10-24", "19:00",
        "Sala de actividades Residencia Militar Ferrol, planta baja",
        30,
        "eromcas",
        "Tarde-noche de juegos de mesa para desconectar: Catan, Ticket to Ride, "
        "Dixit, Codenames y más de 20 títulos disponibles. Entrada libre, sin inscripción. "
        "Se puede traer juego propio. Bebidas y aperitivos a precio de coste. "
        "Se repite todos los últimos viernes de mes. ¡Bienvenidos nóvatos y expertos!",
        ["jrodfer", "mgarrui", "amarsan", "msanmor", "rferbla"],
    ),
    (
        "Otros",
        "Cena de Navidad del personal — Base Naval de Rota",
        "2026-12-19", "21:00",
        "Salón de actos del Casino de Oficiales, Base Naval de Rota",
        120,
        "rferbla",
        "Cena de Navidad anual para el personal y sus parejas. Menú de tres platos "
        "con mariscos de la bahía, música en directo y sorteo de regalos. "
        "Precio: 25 € por persona (incluye menú y consumición). Reserva de mesa hasta "
        "el 10 de diciembre. Dress code: uniforme de media gala o traje civil.",
        ["nvazdel", "lmolcan", "bsuaiba", "fguepin", "mhermun", "aalomed", "pcasflo",
         "amarsan", "aruiser", "imorrey"],
    ),
]


# ─── Script principal ─────────────────────────────────────────────────────────

def main():
    cliente = MongoClient(Config.MONGO_URI)
    db = cliente[Config.MONGO_DB_NAME]
    col_usuarios = db.usuarios
    col_ocio     = db.ocio

    # Caché nombre → ObjectId-string para no relanzar queries en el bucle
    cache_ids = {}
    for doc in col_usuarios.find({}, {"nombre": 1}):
        cache_ids[doc["nombre"]] = str(doc["_id"])

    print("\n=== CREANDO EVENTOS DE OCIO ===\n")
    creados   = 0
    conteo    = {"Deporte": 0, "Cultural": 0, "Otros": 0}

    for idx, ev in enumerate(EVENTOS):
        (tipo, titulo, fecha, hora, lugar, aforo,
         creador, descripcion, inscritos_nombres) = ev

        uid = cache_ids.get(creador)
        if not uid:
            print(f"  [ERROR] Creador '{creador}' no encontrado.")
            continue

        # Resolver IDs de inscritos ignorando los que no existan
        inscritos_ids = [
            cache_ids[n] for n in inscritos_nombres if n in cache_ids
        ]

        col_ocio.insert_one({
            "tipo_evento":        tipo,
            "titulo":             titulo,
            "fecha":              fecha,
            "hora":               hora,
            "lugar":              lugar,
            "aforo_maximo":       aforo,
            "descripcion":        descripcion,
            "inscritos":          inscritos_ids,
            "usuario_id":         uid,
            "nombre_usuario":     creador,
            "fecha_creacion":     datetime.now(),
            "fecha_modificacion": datetime.now(),
        })

        conteo[tipo] += 1
        creados += 1
        tag = f"[{tipo:<8}]"
        print(f"  [OK] #{idx + 1:02d} {tag}  {fecha}  {titulo[:48]:<48}  {len(inscritos_ids)} inscritos")

    cliente.close()
    print(f"\n{'=' * 65}")
    print(f"  Deporte  : {conteo['Deporte']:>2} eventos")
    print(f"  Cultural : {conteo['Cultural']:>2} eventos")
    print(f"  Otros    : {conteo['Otros']:>2} eventos")
    print(f"  Total    : {creados:>2} eventos")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    main()
