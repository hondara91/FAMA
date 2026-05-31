# Proyecto FAMA

Proyecto FAMA significa Foro de Apoyo Multipropósito de la Armada.

## Objetivo

Crear una web app para apoyo multipropósito del personal de la Armada.

La aplicación estará orientada a:
- Viviendas.
- Servicios.
- Compra-venta.
- Ocio y eventos.

## Stack técnico

- Backend: Python con Flask.
- Base de datos: MongoDB usando PyMongo.
- Frontend: HTML con plantillas Jinja2.
- Estilos: Bootstrap.
- Arquitectura: MVC.
- Despliegue: Docker y Docker Compose.
- Servidor previsto: Ubuntu Server con Docker Engine.
- Repositorio: GitHub.

## Estructura base del proyecto

Proyecto_FAMA/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── models/
├── routes/
├── static/
│   ├── css/
│   │   └── estilos.css
│   └── js/
│       └── scripts.js
├── templates/
│   ├── base.html
│   └── index.html
├── utils/
│   ├── config.py
│   └── db.py
└── documentacion/

## Infraestructura inicial

La aplicación debe poder ejecutarse con:

docker compose up --build

Debe levantar:
- Un contenedor web para Flask.
- Un contenedor para MongoDB.
- Un volumen persistente para MongoDB.
- La aplicación disponible en http://localhost:5000.

## Módulos principales

### 1. Viviendas

Módulo orientado al alquiler de pisos, intercambio vacacional y viviendas compartidas.

Campos:
- Tipo de oferta: alquiler, intercambio, compartir.
- Tipo de inmueble: piso, estudio, chalet, ático, finca.
- Ciudad.
- Zona o barrio.
- Habitaciones.
- Baños.
- Planta.
- Precio alquiler.
- Extras: garaje, ascensor, mascotas.
- Teléfono.
- Descripción.

### 2. Servicios

Módulo orientado a ofrecer o buscar servicios.

Campos:
- Qué necesitas: ofrecer o buscar.
- Categoría del servicio: viajes compartidos, clases de apoyo, trabajos.
- Título del anuncio.
- Precio.
- Modalidad: presencial u online.
- Teléfono de contacto.
- Ciudad.
- Descripción.

### 3. Compra-venta

Módulo orientado a compraventa de pequeña entidad.

Campos:
- Nombre del artículo.
- UCO.
- Precio.
- Descripción.

Debe incluir una sección específica para unidades de la Armada, donde se pueda vender merchandising como:
- Camisetas.
- Tazas.
- Pisacorbatas.
- Metopas.
- Otros artículos de unidad.

### 4. Ocio

Módulo orientado a eventos de ocio.

Campos:
- Tipo de evento: deporte, cultural, otros.
- Título.
- Fecha.
- Hora.
- Lugar.
- Aforo máximo.
- Descripción.

Los usuarios deben poder inscribirse en eventos.
Debe existir un calendario común de eventos.

## Funcionalidades comunes de los módulos

Cada módulo debe tener:
- Crear anuncio.
- Listar anuncios.
- Ver detalle.
- Editar anuncio.
- Eliminar anuncio.
- Buscador con filtros usando los campos del formulario.
- Mensajes flash al crear, editar o eliminar.
- Control de permisos según rol.

## Usuarios y roles

Habrá tres roles:

### Usuario normal

Puede:
- Registrarse.
- Iniciar sesión.
- Crear anuncios.
- Editar solo sus propios anuncios.
- Eliminar solo sus propios anuncios.
- Configurar una pregunta de recuperación.

### Gestor

Puede:
- Editar anuncios.
- Editar usuarios.
- Resetear contraseñas de usuarios a la contraseña por defecto: Password.

### Administrador

Puede:
- Editar todos los anuncios.
- Eliminar todos los anuncios.
- Editar usuarios.
- Eliminar usuarios.
- Asignar roles.
- Resetear contraseñas a Password.
- Acceder a logs.
- Acceder a estadísticas.

## Seguridad

- Las contraseñas deben guardarse con hash no reversible usando Werkzeug.
- No se deben guardar contraseñas en texto plano.
- Cuando un administrador o gestor resetea la contraseña de un usuario, ese usuario debe ver un mensaje flash al iniciar sesión indicando que debe cambiarla por seguridad.
- La contraseña por defecto tras reseteo será: Password.

## Logs

### Log de registro

Debe registrar:
- Creación de usuarios.
- Edición de usuarios.
- Creación de anuncios.
- Edición de anuncios.
- Fecha y hora.
- Usuario que realizó la acción.

### Log de control

Debe registrar:
- Número total de usuarios.
- Número total de anuncios.

Los logs deben:
- Poder exportarse a PDF.
- Poder eliminarse mediante un botón.

## Plantillas

Usar una plantilla base:

templates/base.html

Debe incluir:
- Cabecera.
- Menú.
- Bootstrap.
- Bloques Jinja2.
- Mensajes flash.
- Footer reutilizable.
- Diseño responsive.

El footer debe mostrar:

Proyecto FAMA - Foro de Apoyo Multipropósito de la Armada

## Documentación

La documentación se generará en formato .docx dentro de:

documentacion/

Debe incluir:
- Descripción del problema.
- Justificación de la solución propuesta.
- Arquitectura del sistema.
- Esquemas, diagramas y modelos de datos.
- Algoritmos relevantes.
- Manual de usuario.
- Documento explicativo con los métodos de cifrado utilizados y su razonamiento.

## Prioridad actual

Primero crear una base Docker portable:

- Dockerfile.
- docker-compose.yml.
- .dockerignore.
- requirements.txt.
- app.py.
- utils/config.py.
- utils/db.py.
- templates/base.html.
- templates/index.html.
- static/css/estilos.css.
- static/js/scripts.js.

Objetivo inicial:
Al ejecutar docker compose up --build, Flask debe arrancar correctamente y mostrar una página inicial confirmando conexión con MongoDB.
