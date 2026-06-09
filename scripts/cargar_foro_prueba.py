"""
scripts/cargar_foro_prueba.py
Crea 5 canales temáticos del foro con posts y respuestas cruzadas
entre los usuarios ya existentes. Temática 100 % militar/vida en base.

  Canal 1 · Trámites y Gestión     (3 posts · 15 respuestas)
  Canal 2 · Formación y Ascensos   (4 posts · 18 respuestas)
  Canal 3 · Vida en la Base        (3 posts · 13 respuestas)
  Canal 4 · Destinos y Traslados   (3 posts · 12 respuestas)
  Canal 5 · Idiomas                (3 posts · 11 respuestas)

Ejecutar dentro del contenedor:
    docker exec fama_web1 python scripts/cargar_foro_prueba.py
"""
import os
import sys
from datetime import datetime, timedelta

from pymongo import MongoClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config

# ─────────────────────────────────────────────────────────────────────────────
# DATOS
# ─────────────────────────────────────────────────────────────────────────────

CANALES = [
    {
        "nombre":      "Trámites y Gestión",
        "descripcion": "Consultas sobre gestiones administrativas, documentación, "
                       "medallas, pasaportes, complementos y cualquier trámite con la Armada.",
        "color":  "primary",
        "icono":  "briefcase",
        "creador": "amarsan",
    },
    {
        "nombre":      "Formación y Ascensos",
        "descripcion": "Temarios, convocatorias, academias preparadoras, "
                       "convalidaciones y todo lo relacionado con la carrera profesional.",
        "color":  "success",
        "icono":  "book",
        "creador": "jrodfer",
    },
    {
        "nombre":      "Vida en la Base",
        "descripcion": "Convivencia, servicios, recomendaciones locales, guardería, "
                       "talleres, médicos y todo lo que facilita el día a día en el destino.",
        "color":  "warning",
        "icono":  "anchor",
        "creador": "eromcas",
    },
    {
        "nombre":      "Destinos y Traslados",
        "descripcion": "Experiencias en diferentes bases, concursos de traslados, "
                       "conciliación familiar y consejos para el personal que llega nuevo.",
        "color":  "info",
        "icono":  "map",
        "creador": "msanmor",
    },
    {
        "nombre":      "Idiomas",
        "descripcion": "STANAG, inglés, francés, academias recomendadas, cursos online "
                       "y cualquier recurso para mejorar el nivel de idiomas.",
        "color":  "secondary",
        "icono":  "chat-dots",
        "creador": "nvazdel",
    },
]

# Estructura:  canal_idx (0-4), autor, titulo, contenido, días_atrás,
#              lista de (autor_resp, contenido_resp, horas_después_del_post)
POSTS = [

    # ══════════════════════════════════════════════════════════════════════════
    # CANAL 0 · Trámites y Gestión
    # ══════════════════════════════════════════════════════════════════════════
    (
        0, "amarsan",
        "Medalla de campaña EUNAVFOR MED — sigo sin recibirla tras 8 meses",
        "Hola a todos. Participé en la Operación EUNAVFOR MED Irini el año pasado, "
        "regresé hace ya ocho meses y la medalla de campaña todavía no me ha llegado. "
        "He preguntado en la Sección de Personal de mi base y me dicen que está en trámite, "
        "pero nadie sabe darme una fecha. ¿Alguien ha pasado por lo mismo o sabe a quién "
        "hay que dirigirse para agilizarlo? He visto que hay compañeros que la han recibido "
        "en menos tiempo. Gracias.",
        45,
        [
            ("jrodfer",
             "A mí me pasó algo parecido con la medalla de ATALANTA. Al final tuve que "
             "presentar una solicitud formal a través de la Unidad al AJEMA. El proceso "
             "es lento pero funciona. ¿Has comprobado que tu unidad haya enviado correctamente "
             "el listado de participantes a la DIVOPER?",
             3),
            ("mhermun",
             "El año pasado estuve en la misma situación. Me dijeron que el retraso era por "
             "un error en el número de TIP que habían remitido. Te recomiendo revisar que tu "
             "ficha personal en SIPERDEF está actualizada y sin errores.",
             8),
            ("pcasflo",
             "En mi caso tardó casi un año. Lo que hice fue acudir directamente al Negociado "
             "de Condecoraciones en Madrid. Puedes enviarles un escrito por vía telemática "
             "adjuntando la certificación de participación que te habrá dado tu mando. "
             "Eso lo acelera bastante.",
             24),
            ("rferbla",
             "Yo la recibí a los 11 meses. Paciencia y persiste por los canales reglamentarios. "
             "Lo de pcasflo es el camino correcto. Guarda una copia de todo lo que envíes.",
             30),
        ],
    ),
    (
        0, "clopper",
        "¿Cómo se tramita el complemento de zona de difícil cobertura?",
        "Buenos días. Me acaban de destinar a una base que según la normativa entra "
        "dentro de las llamadas 'zonas de difícil cobertura'. Tengo entendido que hay "
        "un complemento económico asociado pero en mi nueva unidad nadie me sabe explicar "
        "cómo se solicita ni cuánto es aproximadamente. ¿Alguien lo ha tramitado y puede "
        "orientarme? ¿Es automático o hay que pedirlo expresamente?",
        38,
        [
            ("nvazdel",
             "No es automático, hay que solicitarlo. El fundamento legal está en el "
             "RD 1932/1998 y modificaciones posteriores. Lo tramita la Habilitación de "
             "tu unidad. Necesitas presentar solicitud, certificado de destino y copia "
             "de la resolución de tu nombramiento.",
             5),
            ("imorrey",
             "Confirmo lo que dice nvazdel. A mí me lo tramitaron en unos 3 meses. "
             "El importe varía según el grupo de cotización y la zona concreta. "
             "Pide a habilitación que te facilite la tabla de zonas actualizada.",
             12),
            ("aalomed",
             "Una cosa importante: el complemento no es retroactivo si te has demorado "
             "en solicitarlo. En cuanto tomes posesión del destino, presenta la solicitud "
             "cuanto antes para que empiece a computar desde el primer día.",
             20),
        ],
    ),
    (
        0, "ltorveg",
        "Retraso enorme en la renovación del pasaporte de servicio",
        "Solicité la renovación del pasaporte de servicio hace cuatro meses y sigo "
        "esperando. Tengo una comisión de servicio en el extranjero prevista para el "
        "mes que viene y empiezo a estar nervioso. ¿Hay alguna vía para acelerar el "
        "trámite cuando hay una necesidad urgente demostrable? ¿A quién se puede llamar "
        "en el Ministerio?",
        22,
        [
            ("fnavram",
             "En situaciones urgentes por comisión de servicio inminente hay un procedimiento "
             "de tramitación urgente. Tu mando debe remitir un escrito a la Dirección General "
             "de Personal indicando la fecha de la comisión. Suele resolverse en 2-3 semanas.",
             4),
            ("aruiser",
             "Yo tuve el mismo problema antes de una misión en Djibouti. Al final me lo "
             "gestionó directamente el 2.º Comandante de mi buque. Si tienes buena relación "
             "con tu jefe inmediato, ponle en situación cuanto antes.",
             9),
            ("cdiagon",
             "Aparte del escrito urgente, llama al teléfono de la unidad de pasaportes del "
             "Ministerio. A veces hay documentación pendiente por su parte y ni te avisan. "
             "Me pasó a mí: el trámite estaba parado porque faltaba una fotocopia compulsada.",
             15),
            ("mgarrui",
             "¿Ya te lo han resuelto? Si sigues sin noticias, el Defensor del Militar también "
             "puede intervenir en casos de retrasos administrativos injustificados.",
             28),
        ],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # CANAL 1 · Formación y Ascensos
    # ══════════════════════════════════════════════════════════════════════════
    (
        1, "msanmor",
        "Dudas sobre el temario oficial para el ascenso a Cabo 1.º — convocatoria 2026",
        "Hola compañeros. Estoy preparando el ascenso a Cabo 1.º y tengo algunas "
        "dudas sobre el temario publicado en la última convocatoria. Concretamente "
        "en el bloque de Organización de la Defensa Nacional, ¿se incluye la nueva "
        "Ley Orgánica 5/2005 con las modificaciones de 2023 o solo el texto original? "
        "Y en el bloque de Armamento, ¿hasta qué nivel de detalle hay que conocer el "
        "funcionamiento del fusil HK G36?",
        60,
        [
            ("pjimort",
             "Para el bloque jurídico ten en cuenta que las convocatorias recientes sí "
             "incluyen las modificaciones de 2023. Te recomiendo la guía de estudio que "
             "edita el propio Ministerio: la actualizan cada año y viene con los cambios "
             "destacados en amarillo.",
             6),
            ("eromcas",
             "Yo pasé el ascenso a Cabo 1.º hace dos años. Para el HK G36 te piden "
             "conocer las partes principales, el ciclo de funcionamiento y los posibles "
             "problemas de tiro. No piden desarme completo en el teórico, eso es solo para "
             "la parte práctica.",
             14),
            ("jrodfer",
             "Muy buena pregunta lo de las modificaciones legales. Yo me lo pregunté igual. "
             "Al final, en mi convocatoria solo cayeron preguntas del texto original pero "
             "un compañero de la siguiente ya tuvo que saber las reformas. No te la juegues "
             "y estudia con las modificaciones.",
             22),
            ("rferbla",
             "Para el temario completo y actualizado búscate el grupo de Telegram "
             "'Ascenso C1 Armada 2026'. Hay compañeros que comparten apuntes y esquemas "
             "muy buenos. Me ayudó bastante cuando yo me preparé.",
             36),
            ("aalomed",
             "Una cosa que nadie dice: dedica tiempo al bloque de Seguridad e Higiene "
             "en el trabajo. Cada año mete entre 3 y 5 preguntas y mucha gente lo descuida "
             "porque parece un bloque menor. A mí casi me cuesta el aprobado.",
             48),
        ],
    ),
    (
        1, "cdiagon",
        "¿Qué academia preparadora recomendáis para el ascenso a Sargento en Madrid?",
        "Llevo destinada en Madrid dos años y este año me quiero presentar a la "
        "oposición interna para Sargento. He visto varias academias en la zona "
        "(Marte, Ares, Athenas preparadores...) pero no conozco a nadie de primera "
        "mano que las haya probado. ¿Alguno tiene experiencia reciente con alguna "
        "de ellas? Busco algo presencial, no online, porque me cuesta mucho la "
        "autodisciplina estudiando solo.",
        52,
        [
            ("fnavram",
             "Yo fui a la Academia Marte hace tres años para el mismo proceso. Buena "
             "organización y los profesores conocen bien el temario específico de la Armada. "
             "Lo único malo es que las clases son muy densas y si fallas un día te pierdes "
             "materia importante.",
             8),
            ("imorrey",
             "Athenas tiene buena fama entre los de tierra pero no sé si tienen profesores "
             "especializados en Armada. Para los bloques jurídicos son muy buenos. "
             "Para los técnicos específicos de marina yo buscaría algo más especializado.",
             16),
            ("aruiser",
             "Te recomiendo que antes de apuntarte a ninguna, preguntes en tu unidad si "
             "hay clases de preparación internas. En mi base organizaban clases los sábados "
             "impartidas por suboficiales que ya habían pasado el proceso. Gratuitas y "
             "muy enfocadas.",
             30),
            ("lmolcan",
             "Academia Ares la conozco. Tienen un grupo específico de fuerzas armadas "
             "y los resultados son bastante buenos. Pregunta por el grupo de tarde, "
             "suele tener gente más motivada.",
             44),
        ],
    ),
    (
        1, "pjimort",
        "Convalidación del Grado en Administración de Empresas dentro de la escala",
        "Tengo el Grado en ADE obtenido de forma privada mientras estaba en activo. "
        "Quiero saber si hay algún procedimiento para que se reconozca dentro del "
        "escalafón o si me da alguna ventaja en los concursos de méritos para destinos. "
        "He leído algo sobre equiparación de titulaciones pero no encuentro nada "
        "concreto en la normativa.",
        40,
        [
            ("nvazdel",
             "Sí existe procedimiento. Debes presentar una solicitud de reconocimiento "
             "ante la Dirección de Enseñanza Naval con la documentación del título. "
             "Para destinos sí computa como mérito en determinadas plazas que lo exigen "
             "o valoran. No es automático, tienes que solicitarlo.",
             10),
            ("bsuaiba",
             "Yo hice algo parecido con un Máster en Recursos Humanos. El proceso tardó "
             "unos 6 meses pero mereció la pena: en el siguiente concurso de traslados "
             "me puntuó como mérito específico para una plaza de gestión logística.",
             24),
            ("mhermun",
             "Ojo con las fechas de las convocatorias de reconocimiento. Hay una ventana "
             "al año, normalmente entre octubre y noviembre. Si te la pierdes tienes que "
             "esperar al siguiente año.",
             38),
        ],
    ),
    (
        1, "eromcas",
        "¿Se puede estudiar el Grado en la UNED compaginándolo con el servicio activo?",
        "Llevo pensando hace tiempo matricularme en la UNED para sacar el Grado en "
        "Derecho, pero no sé cómo gestionar los exámenes presenciales cuando estás "
        "en servicio activo, especialmente si coinciden con guardias o maniobras. "
        "¿Alguien lo ha hecho o lo está haciendo? ¿Os han dado facilidades en la unidad?",
        30,
        [
            ("aalomed",
             "Llevo tres años con el Grado en Historia en la UNED. Es perfectamente "
             "compatible si tienes disciplina. Para los exámenes presenciales puedes "
             "solicitar permiso de asuntos propios o incluso permiso reglamentario "
             "si lo planificas con antelación. La clave es avisar al mando con mucha anticipación.",
             7),
            ("pcasflo",
             "En la UNED hay centros asociados en casi todas las ciudades con base naval. "
             "En San Fernando hay uno y suelen ser comprensivos con el personal militar. "
             "Muchos compañeros estudian allí. Incluso a veces organizan grupos de estudio.",
             18),
            ("rferbla",
             "Mi experiencia: el primer año es el más duro por la adaptación. A partir "
             "del segundo ya sabes cómo funciona y te organizas mejor. No intentes coger "
             "demasiadas asignaturas al principio: con 4 ó 5 por año vas bien.",
             27),
        ],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # CANAL 2 · Vida en la Base
    # ══════════════════════════════════════════════════════════════════════════
    (
        2, "mhermun",
        "Academias de inglés en Ferrol — ¿cuál os ha funcionado mejor?",
        "Recién llegada a Ferrol destinada en la BN. Quiero mejorar mi inglés porque "
        "tengo pendiente el STANAG 2222 para el año que viene. ¿Hay alguna academia "
        "buena en la ciudad que conozcáis de primera mano? También me valdría algo "
        "en modalidad semi-presencial. Agradezco cualquier recomendación.",
        35,
        [
            ("jrodfer",
             "Yo estuve dos años en Ferrol y fui a la Academia Británica en la calle "
             "Real. Buenos profesores nativos y conocen bien el formato STANAG porque "
             "tienen muchos militares como alumnos. Los grupos son reducidos, lo que "
             "ayuda mucho.",
             5),
            ("amarsan",
             "La academia que menciona jrodfer es buena. Hay otra opción: el Centro de "
             "Idiomas de la Universidad de A Coruña tiene extensión en Ferrol y el precio "
             "es más asequible. Yo hice B2 allí hace tres años.",
             12),
            ("eromcas",
             "Para el STANAG específicamente te diría que busques profesor particular "
             "especializado en ese examen. Las academias generales a veces no conocen "
             "bien el formato militar. En el grupo de Facebook 'STANAG Armada' suelen "
             "recomendar preparadores.",
             20),
            ("nvazdel",
             "El EOI de Ferrol también es una opción muy válida y económica. Tienes que "
             "ir en septiembre a hacer la prueba de nivel y te ubican en el curso adecuado. "
             "Yo hice B1 allí y me sirvió de base para luego ir a una academia más enfocada.",
             31),
        ],
    ),
    (
        2, "rferbla",
        "Mecánico de confianza en Cartagena — recomendaciones",
        "Llevo unos meses en Cartagena y necesito un mecánico de confianza para "
        "el mantenimiento de mi coche. En las cadenas del polígono me han dado "
        "presupuestos que me parecen excesivos para lo que necesito (cambio de "
        "frenos y revisión general). ¿Alguno conoce algún taller de confianza "
        "en la zona del Arsenal o Los Mateos?",
        28,
        [
            ("clopper",
             "Pregunta por el taller de Paco en la calle Serreta, detrás del mercado "
             "central. Es conocido entre los de la base y tiene precios razonables. "
             "Trabaja mucho con personal militar. Llámale antes porque está muy ocupado.",
             6),
            ("mgarrui",
             "Yo llevo 3 años yendo al Taller Hermanos Ruiz en el polígono industrial "
             "de Santa Ana. Son honestos con los presupuestos y no te meten mano si no "
             "hace falta. Para frenos y revisión general son perfectos.",
             13),
            ("ltorveg",
             "Comparto la recomendación de los Hermanos Ruiz. Trabajan bien y si les "
             "dices que eres de la base suelen hacer algo de descuento. Pide cita con "
             "antelación, están muy liados.",
             22),
        ],
    ),
    (
        2, "pcasflo",
        "¿Hay guardería cerca del acuartelamiento de San Fernando?",
        "Llego a San Fernando el mes que viene con mi pareja y una niña de 2 años. "
        "Necesito encontrar guardería antes de incorporarme. ¿Hay alguna dentro de "
        "la base o cercana a ella? ¿Sabéis si el Patronato de Viviendas gestiona "
        "algo al respecto? No conozco nada de la zona.",
        20,
        [
            ("amarsan",
             "Hay una escuela infantil dentro del acuartelamiento gestionada por el "
             "Patronato. Plazas limitadas, así que en cuanto tengas la resolución de "
             "destino pide información. Suelen dar prioridad al personal destinado en "
             "la propia base.",
             4),
            ("mhermun",
             "La guardería del Patronato es la mejor opción porque el precio es "
             "subvencionado. Si no hay plazas disponibles, la zona de La Magdalena "
             "tiene varias guarderías privadas a precios razonables y a 5-10 minutos "
             "del acuartelamiento.",
             11),
            ("aalomed",
             "Mi mujer trabaja en la guardería del Patronato de San Fernando. Te puedo "
             "pasar el teléfono de dirección por mensaje privado si quieres. Es mejor "
             "que llames directamente que hacer el trámite por escrito, va más rápido.",
             19),
            ("eromcas",
             "Aparte de la guardería, hay un colegio concertado a 300 metros del "
             "acuartelamiento que también tiene aula de dos años. Muchos niños de familias "
             "militares van ahí. Se llama Colegio Sagrada Familia y tiene buenas referencias.",
             26),
        ],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # CANAL 3 · Destinos y Traslados
    # ══════════════════════════════════════════════════════════════════════════
    (
        3, "imorrey",
        "¿Alguien ha pedido traslado por conciliación familiar desde Rota?",
        "Mi marido acaba de ser destinado a Madrid y llevamos ya un año con destinos "
        "separados. Estoy en Rota y él en el Cuartel General. Quiero pedir traslado "
        "por conciliación familiar pero no sé exactamente qué documentación necesito "
        "ni cuánto tiempo suele tardar la resolución. ¿Alguien ha pasado por algo similar?",
        50,
        [
            ("nvazdel",
             "Existe la figura del 'destino por unión familiar' regulado en la normativa "
             "de destinos. Necesitarás: libro de familia, destino del cónyuge, informe "
             "de tu mando y solicitud formal a través de la cadena. El plazo de resolución "
             "suele ser entre 3 y 6 meses, depende de plazas disponibles.",
             8),
            ("pcasflo",
             "Mi caso fue parecido. Lo resolví en 4 meses. Lo más importante es que el "
             "destino solicitado esté dentro de la misma guarnición que tu cónyuge o a "
             "menos de 30 km. Si no hay plazas disponibles te pueden ofrecer una comisión "
             "de servicio temporal mientras se resuelve la definitiva.",
             18),
            ("aalomed",
             "Apunta también a la posibilidad de solicitar teletrabajo parcial mientras "
             "se resuelve el traslado. Desde 2022 hay más facilidades para personal con "
             "circunstancias familiares acreditadas. Pregunta en la sección de personal.",
             32),
            ("rferbla",
             "Mucho ánimo. Yo estuve año y medio separado de mi familia antes de que se "
             "resolviera. El proceso es lento pero al final funciona. Documenta bien todo "
             "y no te desanimes si hay una primera respuesta negativa.",
             45),
        ],
    ),
    (
        3, "lmolcan",
        "¿Cómo está el ambiente en Las Palmas para alguien que llega solo?",
        "Me acaban de dar destino en la Base Naval de Las Palmas y llego soltero y "
        "sin conocer a nadie allí. ¿Cómo es el ambiente social entre el personal? "
        "¿Hay buena integración entre los de nueva incorporación? También me pregunto "
        "cómo está el tema de la vivienda para alguien que llega solo, si hay residencia "
        "disponible o hay que buscarse las habichuelas desde el principio.",
        42,
        [
            ("msanmor",
             "Llevo 2 años en Las Palmas y el ambiente es genial. El personal es muy "
             "acogedor con los nuevos, especialmente en la zona de suboficiales. Hay "
             "bastantes actividades organizadas en la base los fines de semana. "
             "En verano es difícil aburrirse con el mar a 10 minutos.",
             7),
            ("pjimort",
             "Para la vivienda: hay residencia militar en la base pero las plazas están "
             "muy demandadas. Si no consigues plaza, la zona de Guanarteme es la favorita "
             "del personal militar soltero, buena relación calidad-precio y cerca de la base.",
             16),
            ("cdiagon",
             "Nada más llegar apúntate a las actividades del club deportivo de la base. "
             "Es la forma más rápida de conocer gente. El equipo de fútbol sala y el de "
             "volleyball son muy activos y siempre necesitan gente.",
             24),
        ],
    ),
    (
        3, "bsuaiba",
        "Diferencias reales entre destino en Madrid y destino en Cartagena",
        "Tengo opción de elegir entre dos destinos: uno en el Cuartel General de Madrid "
        "y otro en el Arsenal de Cartagena. Tengo familia y dos hijos en edad escolar. "
        "Desde el punto de vista de calidad de vida familiar, ¿cuál recomendaríais? "
        "No me refiero solo a lo profesional sino a colegio, vivienda, coste de vida, etc.",
        33,
        [
            ("fnavram",
             "Tengo experiencia en los dos. Madrid es más caro pero más servicios. "
             "Cartagena tiene una calidad de vida fantástica para familias: colegios "
             "buenos, la ciudad es manejable, el clima es excelente y el coste de vida "
             "mucho más bajo que Madrid. Para criar niños yo elegiría Cartagena sin dudarlo.",
             9),
            ("aruiser",
             "Depende también de las perspectivas profesionales de tu pareja. Si tiene "
             "trabajo o posibilidades laborales en Madrid, eso pesa mucho. En Cartagena "
             "las opciones para civiles son más limitadas.",
             21),
            ("mgarrui",
             "Vivo en Cartagena con familia desde hace 4 años. El colegio de mis hijos "
             "es excelente y pagamos 700€ por un piso grande en Los Mateos que en Madrid "
             "nos costaría el doble. El clima además es imbatible.",
             35),
        ],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # CANAL 4 · Idiomas
    # ══════════════════════════════════════════════════════════════════════════
    (
        4, "nvazdel",
        "Preparación para el STANAG 6001 nivel 2222 — experiencias y recursos",
        "Tengo que presentarme al STANAG 6001 en nivel SLP 2222 el año que viene. "
        "Llevo un B1 en inglés y sé que necesito subir bastante el nivel, especialmente "
        "en la parte oral y de comprensión auditiva. ¿Qué recursos o métodos os han "
        "funcionado mejor para preparar específicamente este examen? ¿Academia, "
        "particular, online...?",
        48,
        [
            ("jrodfer",
             "El STANAG 2222 es alcanzable desde B1 pero necesitas mínimo un año de "
             "preparación intensa. Yo lo hice con academia presencial (2 horas semanales) "
             "más práctica diaria con podcasts en inglés. La parte de lectura es "
             "la más fácil si tienes base, enfócate en la oral y la auditiva.",
             10),
            ("amarsan",
             "Para el listening te recomiendo BBC Learning English y el podcast "
             "'English at Work'. Para el speaking, busca un intercambio de idiomas "
             "con un nativo: hay apps como Tandem o HelloTalk que funcionan muy bien "
             "y son gratuitas.",
             22),
            ("mhermun",
             "El CESEDEN tiene un programa de inglés militar específico con material "
             "adaptado al vocabulario de las FAS. Vale la pena descargarse los manuales "
             "aunque no hagas el curso presencial. Tienen mucho vocabulario táctico y "
             "de procedimientos que sale en el STANAG.",
             38),
            ("imorrey",
             "Yo tardé 14 meses desde B1 hasta el 2222. Clave: consistencia diaria "
             "aunque sea 20-30 minutos. Ver series en inglés con subtítulos en inglés "
             "(no en castellano) me ayudó muchísimo con el listening.",
             52),
        ],
    ),
    (
        4, "fguepin",
        "¿Merece la pena el curso de inglés online del CESEDEN?",
        "He visto que el CESEDEN oferta cursos de inglés online para el personal "
        "en activo. No tengo referencias de nadie que lo haya hecho. ¿Es buena "
        "la calidad? ¿Os ha servido para subir el nivel de forma real o es más "
        "bien un complemento? Estoy en nivel A2 y me parece interesante si de "
        "verdad está bien hecho.",
        25,
        [
            ("nvazdel",
             "El curso del CESEDEN está bien estructurado para los niveles básicos "
             "(A1-B1). Para A2 te vendría muy bien. La plataforma no es la más "
             "moderna pero el contenido es sólido y está enfocado en el vocabulario "
             "que usamos en el día a día militar.",
             8),
            ("lmolcan",
             "Hice el nivel A2-B1 del CESEDEN hace dos años. Me ayudó bastante con "
             "la gramática y el vocabulario básico. Para el oral es insuficiente solo "
             "con eso, pero como base complementaria va bien.",
             17),
            ("bsuaiba",
             "Lo que tiene de bueno el CESEDEN es que está adaptado a los horarios "
             "militares y entienden si en un período de maniobras no puedes avanzar. "
             "Para A2 es una buena opción. Combínalo con algo de práctica oral fuera.",
             28),
        ],
    ),
    (
        4, "pcasflo",
        "Francés militar — ¿alguien lo ha estudiado para misiones OTAN?",
        "Tengo prevista una misión en el marco de la OTAN en zona francófona "
        "en los próximos años. Quiero aprovechar el tiempo para aprender francés "
        "al menos a nivel funcional. No sé prácticamente nada. ¿Hay algún recurso "
        "o curso específico para el español que aprende francés con fines militares?",
        18,
        [
            ("rferbla",
             "Para emprir desde cero con fines militares, Duolingo te sirve para las "
             "bases del idioma en los primeros meses. A partir de A2-B1 necesitarás "
             "algo más específico. El Ejército de Tierra tiene material de francés "
             "militar en su web que también sirve para la Armada.",
             6),
            ("aalomed",
             "El SHAPE (Cuartel General de la OTAN en Mons) tiene cursos de francés "
             "para personal de otros países miembros. Si tu misión es de larga duración "
             "y coordinada con la OTAN, pregunta en tu unidad si hay posibilidad de "
             "acceder a esos recursos antes del despliegue.",
             16),
            ("fguepin",
             "Hay una aplicación gratuita llamada 'AnkiDroid' con mazos de vocabulario "
             "militar francés creados por usuarios. Es un método de tarjetas de memoria "
             "muy efectivo para aprender vocabulario específico. Busca en la comunidad "
             "los mazos de 'vocabulaire militaire français'.",
             25),
            ("cdiagon",
             "Si tienes tiempo antes del despliegue, la Alianza Francesa tiene cursos "
             "intensivos de verano que en 3-4 semanas te llevan de 0 a A2-B1. "
             "Hay sedes en Madrid, Cartagena y Sevilla.",
             33),
        ],
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Script principal
# ─────────────────────────────────────────────────────────────────────────────

def main():
    cliente = MongoClient(Config.MONGO_URI)
    db = cliente[Config.MONGO_DB_NAME]

    # Caché nombre_usuario → {_id: str, ...}
    cache = {
        doc["nombre"]: str(doc["_id"])
        for doc in db.usuarios.find({}, {"nombre": 1})
    }

    print("\n=== CREANDO CANALES DEL FORO ===\n")

    # ── Crear canales ─────────────────────────────────────────────────────────
    canal_ids = []
    for c in CANALES:
        uid = cache.get(c["creador"])
        if not uid:
            print(f"  [ERROR] Creador '{c['creador']}' no encontrado.")
            canal_ids.append(None)
            continue
        res = db.foro_canales.insert_one({
            "nombre":         c["nombre"],
            "descripcion":    c["descripcion"],
            "color":          c["color"],
            "icono":          c["icono"],
            "usuario_id":     uid,
            "nombre_usuario": c["creador"],
            "fecha_creacion": datetime.now(),
        })
        canal_ids.append(str(res.inserted_id))
        print(f"  [CANAL] {c['nombre']}")

    # ── Crear posts y respuestas ──────────────────────────────────────────────
    print("\n=== CREANDO POSTS Y RESPUESTAS ===\n")
    total_posts = 0
    total_resp  = 0

    for canal_idx, autor, titulo, contenido, dias_atras, respuestas in POSTS:
        cid = canal_ids[canal_idx]
        uid = cache.get(autor)
        if not cid or not uid:
            print(f"  [ERROR] Canal o autor no disponible para '{titulo[:40]}'")
            continue

        fecha_post = datetime.now() - timedelta(days=dias_atras)

        post_id = str(db.foro_posts.insert_one({
            "titulo":             titulo,
            "contenido":          contenido,
            "fotos":              [],
            "imagen":             None,
            "canal_id":           cid,
            "usuario_id":         uid,
            "nombre_usuario":     autor,
            "fecha_creacion":     fecha_post,
            "fecha_modificacion": fecha_post,
        }).inserted_id)

        total_posts += 1
        print(f"  [POST]  {titulo[:60]}")

        for autor_r, contenido_r, horas_d in respuestas:
            uid_r = cache.get(autor_r)
            if not uid_r:
                continue
            fecha_r = fecha_post + timedelta(hours=horas_d)
            db.foro_respuestas.insert_one({
                "post_id":        post_id,
                "contenido":      contenido_r,
                "fotos":          [],
                "imagen":         None,
                "usuario_id":     uid_r,
                "nombre_usuario": autor_r,
                "fecha_creacion": fecha_r,
            })
            total_resp += 1
            print(f"           ↳ @{autor_r}")

    cliente.close()
    print(f"\n{'=' * 60}")
    print(f"  Canales creados   : {len([x for x in canal_ids if x])}")
    print(f"  Posts creados     : {total_posts}")
    print(f"  Respuestas creadas: {total_resp}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
