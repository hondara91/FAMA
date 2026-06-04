# Registro cronologico de cambios - Proyecto FAMA

Este archivo recoge los cambios realizados en el proyecto con fecha y hora.
Formato usado: `AAAA-MM-DD HH:MM:SS ZONA`.

## 2026-05-30 10:15:00 CEST

### Definicion del proyecto FAMA

- Se define el nombre del proyecto: FAMA (Foro de Apoyo Multiproposito de la Armada).
- Se establece el objetivo: aplicacion web interna de apoyo al personal de la Armada.
- Se identifican los cuatro modulos principales: Viviendas, Servicios, Compra-venta, Ocio.
- Se define el stack tecnico: Python + Flask, MongoDB, Bootstrap, Docker, Ubuntu Server.
- Se define la arquitectura: patron MVC.
- Se documenta el proyecto en `CONTEXTO_PROYECTO_FAMA.md`.

## 2026-05-30 11:00:00 CEST

### Instalacion de Docker Desktop en macOS

- Se descarga Docker Desktop para macOS desde la web oficial.
- Se instala y se arranca Docker Desktop.
- Se verifica la instalacion: `Docker version 29.5.2`.
- Se verifica Docker Compose integrado: `Docker Compose version v5.1.3`.

## 2026-05-30 11:30:00 CEST

### Instalacion de Python 3.14 en macOS

- Se descarga e instala `Python 3.14.0` para macOS desde python.org.
- Se verifica la instalacion con `python3 --version`: `Python 3.14.0`.
- Se confirma que `pip` queda disponible junto con la instalacion.

## 2026-05-30 12:00:00 CEST

### Creacion de la estructura de directorios del proyecto

- Se crea el directorio raiz del proyecto: `FAMA/`.
- Se crea la estructura base orientada a MVC:
  - `models/` — para los modelos de datos MongoDB (pendiente de poblar).
  - `routes/` — para los controladores Flask (Blueprints).
  - `templates/` — para las plantillas Jinja2.
  - `static/css/` — para las hojas de estilo.
  - `static/js/` — para los scripts de cliente.
  - `utils/` — para modulos de configuracion y conexion a base de datos.
  - `documentacion/` — para la documentacion del proyecto.
- Se crean los ficheros `__init__.py` en `routes/` y `utils/` para registrarlos como paquetes Python.
- Se inicializa el fichero `.gitignore` para excluir entornos virtuales, cache y ficheros sensibles.

## 2026-05-30 12:45:00 CEST

### Creacion del entorno virtual local inicial

- Se crea el entorno virtual local en `.venv/` con `python3 -m venv .venv`.
- Se activa el entorno: `source .venv/bin/activate`.
- Se actualiza `pip` a la ultima version disponible.
- Se instalan manualmente Flask y pymongo para validar compatibilidad con Python 3.14.
- Se confirma que Flask y pymongo funcionan correctamente bajo Python 3.14.

## 2026-05-31 15:23:36 CEST

### Cambio de puerto de acceso externo

- Se configura el acceso desde la maquina anfitriona por `http://localhost:8000`.
- Se mantiene Flask escuchando internamente en el puerto `5000`.
- Se actualiza `docker-compose.yml` para publicar `8000:5000`.
- Se mantiene `FLASK_PORT` en `5000`.
- Se mantiene `EXPOSE` en `5000` dentro del `Dockerfile`.

## 2026-05-31 15:22:25 CEST

### Creacion del registro de cambios

- Se crea este archivo para documentar de forma cronologica la evolucion del proyecto.
- A partir de este punto, los cambios relevantes se iran anotando aqui.

### Base inicial Docker + Flask + MongoDB

- Se crea `Dockerfile` para construir una imagen Python portable basada en `python:3.12-slim`.
- Se crea `docker-compose.yml` con dos servicios:
  - `web`: aplicacion Flask expuesta inicialmente en `http://localhost:5000`.
  - `mongo`: base de datos MongoDB con volumen persistente `mongo_data`.
- Se crea `.dockerignore` para excluir archivos temporales, entornos virtuales, cache y metadatos locales.
- Se crea `requirements.txt` con dependencias iniciales:
  - `Flask`
  - `pymongo`
- Se crea `app.py` como punto de entrada de la aplicacion Flask.
- Se crea `utils/config.py` para centralizar la configuracion mediante variables de entorno.
- Se crea `utils/db.py` para gestionar la conexion con MongoDB y comprobar el estado mediante `ping`.
- Se crea `routes/main.py` como controlador inicial de la ruta `/`.
- Se crean `routes/__init__.py` y `utils/__init__.py` para preparar los paquetes Python.
- Se crea `templates/base.html` como plantilla base con Bootstrap y recursos estaticos.
- Se crea `templates/index.html` como pagina inicial de Proyecto FAMA.
- Se crea `static/css/estilos.css` con estilos iniciales de la interfaz.
- Se crea `static/js/scripts.js` con una carga inicial minima de JavaScript.

### Validaciones realizadas

- Se comprueba que la estructura del proyecto contiene los archivos esperados.
- Se valida la sintaxis Python con `python3 -m py_compile`.
- No se pudo ejecutar `docker compose up --build` porque Docker no esta disponible en el entorno actual.

## 2026-05-31 15:42:04 CEST

### Validacion con Docker disponible

- Se comprueba que Docker esta instalado: `Docker version 29.5.2`.
- Se comprueba que Docker Compose esta instalado: `Docker Compose version v5.1.3`.
- Se valida la configuracion con `docker compose config`.
- Se construye y arranca la pila con Docker Compose.
- Se confirma que `fama_mongo` queda en estado `healthy`.
- Se confirma que `fama_web` queda publicado como `0.0.0.0:8000->5000/tcp`.
- Se verifica `http://localhost:8000/` con respuesta HTTP `200`.
- Se confirma en la pagina inicial el estado `Flask funcionando`.
- Se confirma en la pagina inicial el estado `Conexion con MongoDB activa`.

## 2026-05-31 17:22:15 CEST

### Cambio de nombre del contenedor MongoDB

- Se cambia el nombre del contenedor MongoDB de `fama_mongo` a `fama_mongo1`.
- Se mantiene el servicio Docker Compose llamado `mongo`.
- Se mantiene `MONGO_URI` apuntando a `mongodb://mongo:27017/`, porque `mongo` es el nombre del servicio usado como DNS interno.
- No se cambian los puertos: externo `8000` e interno Flask `5000`.

## 2026-05-31 17:28:02 CEST

### Cambio de nombre del contenedor web

- Se cambia el nombre del contenedor web de `fama_web` a `fama_web1`.
- Se mantiene el servicio Docker Compose llamado `web`.
- Se mantienen los comandos basados en servicio, como `docker compose exec web`.
- No se cambian los puertos: externo `8000` e interno Flask `5000`.


## 2026-05-31 15:50:58 CEST

### Entorno virtual dentro de Docker

- Se actualiza `Dockerfile` para crear un entorno virtual Python en `/opt/venv`.
- Se define `VIRTUAL_ENV=/opt/venv`.
- Se añade `/opt/venv/bin` al `PATH` del contenedor.
- Se instalan las dependencias de `requirements.txt` dentro del entorno virtual.
- Se mantiene Flask escuchando internamente en el puerto `5000`.

## 2026-05-31 HH:MM:SS CEST

### Creación del entorno virtual local

- Se crea un entorno virtual local en `.venv`.
- Se activa el entorno virtual con `source .venv/bin/activate`.
- Se actualiza `pip`.
- Se instalan las dependencias desde `requirements.txt`.
- Se mantiene Docker como entorno principal de ejecución.
- El entorno virtual local se usará para validaciones, desarrollo y ejecución de comandos Python fuera del contenedor.

## 2026-05-31 16:32:18 CEST

### Igualacion de version Python entre venv local y Docker

- Se detecta que el entorno virtual local usa `Python 3.14.0` y el `Dockerfile` usaba `python:3.12-slim`.
- Se actualiza `Dockerfile`: imagen base cambiada de `python:3.12-slim` a `python:3.14-slim`.
- Se verifica que la imagen `python:3.14-slim` existe en Docker Hub y se descarga correctamente.
- Ambos entornos (`.venv` local y contenedor Docker `web`) quedan alineados en `Python 3.14`.

## 2026-05-31 HH:MM:SS CEST

### Limpieza y organización de entornos virtuales

- Se revisa la estructura local del proyecto FAMA.
- Se confirma que `.venv` está dentro de la carpeta raíz del proyecto, pero no contiene el código de la aplicación.
- Se confirma que el código del proyecto se encuentra al mismo nivel que `.venv`, en carpetas como `routes/`, `templates/`, `static/`, `utils/` y en el archivo `app.py`.
- Se elimina el entorno virtual duplicado `.venv-1`.
- Se mantiene `.venv` como único entorno virtual local para desarrollo en Mac y uso desde VS Code.
- Se confirma que `.venv/` y `.venv-1/` están incluidos en `.gitignore`.
- Se confirma que `.venv/` y `.venv-1/` están incluidos en `.dockerignore`.

### Organización dentro de Docker

- Se confirma que el proyecto dentro del contenedor se organiza en dos rutas separadas:
  - `/opt/venv`: entorno virtual interno del contenedor.
  - `/app`: código fuente del Proyecto FAMA.
- Se confirma que el proyecto no se copia dentro de `/opt/venv`.
- Se mantiene `/opt/venv` únicamente para Python y dependencias.
- Se mantiene `/app` como carpeta de trabajo de la aplicación.
- Se confirma que el `Dockerfile` usa `WORKDIR /app`.
- Se confirma que el `Dockerfile` define `VIRTUAL_ENV=/opt/venv`.
- Se confirma que el `PATH` del contenedor prioriza `/opt/venv/bin`.
- Se mantiene `CMD ["python", "app.py"]`, ejecutándose con el Python del entorno virtual interno.
- Se mantiene Flask escuchando internamente en el puerto `5000`.
- Se mantiene el acceso externo desde el equipo anfitrión mediante `http://localhost:8000`.

### Creación del repositorio Git local

- Se crea un repositorio Git local dentro de la carpeta raíz `FAMA`.
- El repositorio se crea mediante `git init`.
- Se confirma que Git se almacena internamente en `FAMA/.git/`.
- Se revisa el estado del repositorio con `git status`.
- Se comprueba que `.venv/` no aparece como archivo pendiente de seguimiento, confirmando que `.gitignore` funciona correctamente.
- Se añaden los archivos del proyecto al área de preparación mediante `git add .`.
- Se crea el primer commit del proyecto con el mensaje `Base inicial Proyecto FAMA`.

### Preparación para conexión con GitHub

- Se inicia el proceso para conectar el repositorio local con GitHub.
- Se aclara que no debe usarse la pantalla `Import your project to GitHub`, ya que el proyecto ya existe localmente.
- Se indica que debe crearse un repositorio nuevo vacío desde GitHub.
- Se recomienda usar el nombre `FAMA` para el repositorio remoto.
- Se establece que, una vez creado el repositorio remoto, se conectará con:

```bash
git branch -M main
git remote add origin https://github.com/hondara91/FAMA.git
git push -u origin main

## 2026-05-31 17:35:58 CEST

### Eliminacion del contenedor residual fama_web

- Se detecta conflicto al arrancar otro proyecto Docker con caracteristicas similares.
- El error indica que el nombre `/fama_web` ya esta en uso por un contenedor anterior.
- Se comprueba que el contenedor `fama_web` sigue activo (estado `Up`) de una ejecucion previa al renombrado.
- Se para y elimina el contenedor residual con `docker stop fama_web && docker rm fama_web`.
- El proyecto FAMA no se ve afectado: `docker-compose.yml` ya usa `container_name: fama_web1`.
- El proximo `docker compose up` levantara el contenedor con el nombre correcto `fama_web1`.

## 2026-05-31 17:48:32 CEST

### Cambio de puerto externo de MongoDB a 27018

- Se detecta conflicto en el puerto `27017` con otro proyecto Docker en ejecucion.
- Se actualiza `docker-compose.yml`: puerto externo de MongoDB cambiado de `27017` a `27018`.
- El mapeo queda como `27018:27017` (host `27018` → contenedor `27017`).
- Flask sigue conectandose a MongoDB por la red interna de Docker en el puerto `27017`, sin cambios.
- Para conectarse con MongoDB Compass usar el puerto `27018` en lugar del estandar `27017`.

## 2026-05-31 17:55:27 CEST

### Limpieza de contenedores residuales y arranque limpio

- Se detecta contenedor residual `fama_mongo` en estado `Created` bloqueando el arranque.
- Se elimina el contenedor residual con `docker rm fama_mongo`.
- Se ejecuta `docker compose down` para parar y eliminar contenedores y red existentes.
- Se ejecuta `docker compose up -d` con la configuracion actualizada.
- Se confirma arranque correcto de ambos contenedores:
  - `fama_mongo1`: estado `healthy`, puerto `27018:27017`.
  - `fama_web1`: estado `Up`, puerto `8000:5000`.
- Aplicacion disponible en `http://localhost:8000`.

## 2026-05-31 HH:MM:SS CEST

### Integracion completa de modulos funcionales (migracion desde Proyecto_FAMA_1.0)

Se incorporan al proyecto FAMA todos los modulos de negocio desarrollados en
Proyecto_FAMA_1.0, respetando y mejorando la politica de organizacion, calidad
y facilidad de seguimiento de errores propia del proyecto FAMA base.
Los contenedores Docker (`fama_web1`, `fama_mongo1`) y los puertos (`8000`, `27018`)
no se modifican para evitar conflictos con Proyecto_FAMA_1.0.

#### utils/helpers.py (nuevo)

- Se crea `utils/helpers.py` con las funciones auxiliares transversales:
  - Decoradores de control de acceso: `login_required`, `admin_required`, `gestor_required`.
  - `registrar_log`: inserta entradas de auditoria en la coleccion `logs` de MongoDB.
  - `actualizar_contadores`: guarda un snapshot de contadores en el log de control.
  - `exportar_logs_pdf`: genera un PDF de logs con ReportLab (A4, tabla formateada).

#### utils/db.py (actualizado)

- Se añade `get_db = get_database` como alias corto para uso en rutas y modelos.
- Se conserva la implementacion superior de FAMA base: lazy init, timeout 3 s, `PyMongoError`.

#### models/ (nuevo directorio)

- Se crea `models/__init__.py` para registrar el paquete.
- Se crean los cinco modelos de datos, cada uno encapsulando su logica de negocio:
  - `models/usuario.py`: creacion con hash de contrasenia, autenticacion, roles,
    reseteo de contrasenia, pregunta de seguridad y soft-delete.
  - `models/vivienda.py`: CRUD de anuncios de vivienda con buscador por filtros.
  - `models/servicio.py`: CRUD de anuncios de servicios con buscador por filtros.
  - `models/compraventa.py`: CRUD de articulos, seccion especial de merchandising Armada.
  - `models/ocio.py`: CRUD de eventos, inscripciones/desinscripciones con control de aforo,
    colores por tipo de evento y formato para FullCalendar.js.

#### routes/ (nuevas rutas)

- `routes/auth.py`: registro, login, logout, cambio de contrasenia, recuperacion por
  pregunta de seguridad.
- `routes/viviendas.py`: listado con buscador, crear, editar, eliminar, detalle.
  Control de permisos: propietario o rol privilegiado (gestor/admin).
- `routes/servicios.py`: misma estructura CRUD que viviendas.
- `routes/compraventa.py`: CRUD con ruta adicional `/armada` para merchandising.
- `routes/ocio.py`: CRUD de eventos mas rutas de inscripcion/desinscripcion y calendario.
- `routes/admin.py`: panel de estadisticas, gestion de usuarios (editar, cambiar rol,
  resetear contrasenia, desactivar), logs con filtrado, eliminacion selectiva y exportacion PDF.
- `routes/main.py` (actualizado): dashboard con los 4 ultimos anuncios de cada modulo
  y conserva el healthcheck de MongoDB.

#### app.py (actualizado)

- Se registran los siete blueprints: `main`, `auth`, `viviendas`, `servicios`,
  `compraventa`, `ocio`, `admin`.
- Se añade `context_processor` que inyecta `now` (fecha actual) en todas las plantillas.
- Se conserva la instancia global `app = create_app()` para compatibilidad con gunicorn.

#### requirements.txt (actualizado)

- Se añaden `Werkzeug==3.0.3` (hash de contrasenias), `reportlab==4.2.2` (PDF)
  y `python-docx==1.1.2`.
- Se actualiza `pymongo` de `4.7.3` a `4.8.0`.

#### templates/ (actualizadas y nuevas)

- `templates/base.html`: barra de navegacion naval completa con dropdowns para
  Compra-Venta y Ocio, menu de usuario con badge de rol, mensajes flash con
  autocerrado, footer con año dinamico.
- `templates/index.html`: hero con indicador de estado MongoDB, tarjetas de modulos
  con efecto hover, dashboard de ultimos anuncios por modulo.
- Nuevas: `auth/` (4 plantillas), `viviendas/` (3), `servicios/` (3),
  `compraventa/` (4 incluyendo Tienda Armada), `ocio/` (4 incluyendo calendario
  FullCalendar), `admin/` (4: panel, usuarios, editar usuario, logs).

#### static/ (actualizados)

- `static/css/estilos.css`: identidad visual naval completa (navbar degradado azul marino,
  hero, tarjetas de modulo con hover, hero Armada, footer, tablas admin, responsive).
- `static/js/scripts.js`: `confirmarEliminacion()` para formularios de borrado,
  autocerrado de alertas flash a los 5 segundos.

#### crear_admin.py (nuevo)

- Script idempotente para crear el usuario `admin@fama.es` / `Admin1234`.
- Usa `Config.MONGO_URI` y `Config.MONGO_DB_NAME` (sin duplicar variables de entorno).
- Ejecutar una sola vez tras el primer arranque: `python crear_admin.py`.

#### .env.example (nuevo)

- Plantilla documentada con todas las variables de entorno requeridas.

#### Validaciones realizadas

- Sintaxis Python verificada con `python3 -m py_compile` en los 17 archivos `.py`.
- Estructura de directorios completa: `models/`, `routes/`, `utils/`, `templates/`
  (con subdirectorios por modulo) y `static/`.
- Docker-compose sin cambios: `fama_web1` en puerto `8000`, `fama_mongo1` en puerto
  `27018`, sin conflicto con Proyecto_FAMA_1.0.

## 2026-05-31 HH:MM:SS CEST

### Documentacion inline: comentarios en todos los archivos de codigo y plantillas

Se añaden comentarios explicativos en los 17 archivos Python y en los principales
templates HTML, distinguiendo que hace cada seccion, por que se toman ciertas
decisiones y como se relacionan los componentes entre si.

#### Python

- `app.py`: proposito de cada import, seccion de blueprints, explicacion del
  `context_processor` e instancia global para gunicorn.
- `utils/db.py`: patron singleton/lazy-init, por que `serverSelectionTimeoutMS=3000`,
  cuando usar `get_db` vs `get_database`.
- `utils/helpers.py`: por que `@wraps`, diferencia admin vs gestor, tipos de log
  `'registro'` vs `'control'`, secciones del PDF con ReportLab.
- `models/usuario.py`: hash de contrasenias, normalizacion a minusculas de la
  respuesta de seguridad, anti-enumeracion en `autenticar()`, soft-delete.
- `models/ocio.py`: estructura del array `inscritos`, operadores `$push`/`$pull`,
  proyeccion MongoDB, colores FullCalendar.
- `models/vivienda.py`, `servicio.py`, `compraventa.py`: campos comentados,
  logica `$regex` en buscadores, nota sobre `es_merchandising`.
- `routes/auth.py`: flujo completo por ruta, construccion de sesion, flag
  `debe_cambiar_password`.
- `routes/admin.py`: jerarquia de roles, `$in` en delete_many, diferencia
  gestor/admin por accion.
- `routes/viviendas.py`: patron de permisos (propietario o privilegiado),
  `getlist('extras')` para checkboxes multiples.
- `routes/main.py`: por que `limit(4)`, orden ascendente en eventos de ocio.
- `crear_admin.py`: idempotencia del script, uso de `Config.MONGO_URI`.

#### HTML (Jinja2)

- `templates/base.html`: logica de `active` en navbar, cuando se muestra Panel Admin,
  categorizacion de mensajes flash, `now` del context_processor en el footer.
- `templates/index.html`: hero con estado MongoDB, macro `cabecera_seccion`,
  filtro de merchandising en compraventa, orden ascendente en eventos.
- `templates/viviendas/listar.html`: buscador con persistencia de filtros,
  patron de permisos en botones editar/eliminar.
- `templates/viviendas/formulario.html`: modo crear vs editar con `accion`,
  pre-relleno de campos en edicion, `getlist` para checkboxes.
- `templates/ocio/detalle.html`: tres estados de inscripcion, barra de progreso
  de aforo, bloque de acciones solo para propietario o privilegiado.
- `templates/ocio/calendario.html`: uso de `| safe` en JSON, opciones de
  FullCalendar, `eventClick` para navegar al detalle.
- `templates/admin/usuarios.html`: colores de rol, significado de activo/inactivo,
  bloque exclusivo de admin para cambio de rol y desactivacion.
- `templates/admin/logs.html`: formulario envolvente para checkboxes, checkbox
  maestro, filtro activo, exportacion PDF del conjunto filtrado.
- `templates/admin/panel.html`: generacion de tarjetas con bucle, acceso a logs
  restringido solo a admin.

## 2026-05-31 HH:MM:SS CEST

### Cambio de nomenclatura: "Militar" → "Multipropósito"

- Se sustituye "Foro de Apoyo Militar de la Armada" por
  "Foro de Apoyo Multipropósito de la Armada" para reflejar
  el caracter multiuso de la plataforma.
- Archivos modificados:
  - `templates/base.html`: footer.
  - `templates/index.html`: subtitulo del hero.
- Se usa la entidad HTML `&oacute;` para garantizar la correcta
  visualizacion de la o acentuada independientemente de la
  codificacion del servidor.

## 2026-05-31 HH:MM:SS CEST

### Ajuste visual: botones del hero con la misma anchura

- Se envuelven los botones "Registrarse" e "Iniciar sesion" del hero
  de `templates/index.html` en un contenedor `d-inline-flex gap-2`.
- Se añade `flex-fill` a ambos botones para que se repartan el espacio
  disponible por igual y queden exactamente a la misma anchura.
- Se conserva el formato original: "Registrarse" en `btn-light` (blanco
  solido) e "Iniciar sesion" en `btn-outline-light` (transparente con borde).
- En movil los botones se apilan en columna (`flex-column`) y en pantallas
  `sm+` se muestran en fila (`flex-sm-row`).

## 2026-05-31 HH:MM:SS CEST

### Nuevo modulo: Foro de publicaciones

Se implementa el modulo Foro siguiendo la organizacion, estilo visual y
politica de calidad del resto de modulos del proyecto FAMA.

#### Nuevos archivos

- `models/foro.py`: dos clases de modelo sobre colecciones MongoDB separadas:
  - `ForoPost`: publicaciones principales (titulo, contenido, imagen opcional,
    autor, fechas de creacion y modificacion).
  - `ForoRespuesta`: respuestas anidadas a un post (post_id de referencia,
    contenido, imagen opcional, autor, fecha).
  - Metodos: CRUD completo, buscador con `$or` y `$regex`, conteo de
    respuestas por post, borrado masivo de respuestas al eliminar un post.

- `routes/foro.py`: blueprint con prefijo `/foro` y las siguientes rutas:
  - `GET  /foro/`                         listado con buscador por texto y autor.
  - `GET  /foro/detalle/<id>`             post completo con hilo de respuestas.
  - `POST /foro/detalle/<id>`             anadir respuesta al hilo.
  - `GET/POST /foro/nuevo`                crear publicacion nueva.
  - `GET/POST /foro/editar/<id>`          editar publicacion propia.
  - `POST /foro/eliminar/<id>`            eliminar post y todas sus respuestas.
  - `POST /foro/respuesta/eliminar/<id>`  eliminar una respuesta concreta.
  - Subida de imagenes: PNG/JPG/JPEG/GIF/WEBP, max 5 MB, guardadas en
    `static/uploads/foro/` con nombre unico basado en timestamp.
  - `_guardar_imagen()` y `_eliminar_imagen()`: utilidades internas de
    gestion de archivos en disco.
  - Control de permisos: propietario o rol `gestor`/`admin` en todas las
    operaciones de modificacion y borrado.

- `templates/foro/listar.html`: tarjetas con miniatura de imagen, titulo,
  vista previa del contenido, autor, fecha y contador de respuestas.
- `templates/foro/detalle.html`: post completo con imagen, hilo de respuestas
  con sus propias imagenes y formulario de respuesta al final.
- `templates/foro/formulario.html`: formulario de creacion/edicion con campo
  de titulo, textarea de contenido, subida de imagen y opcion de borrar
  la imagen existente en modo edicion.

#### Archivos modificados

- `utils/config.py`: se añade `MAX_CONTENT_LENGTH = 5 MB` para que Flask
  rechace automaticamente archivos que superen el limite permitido.
- `app.py`: se importa y registra `foro_bp`.
- `templates/base.html`: se añade entrada "Foro" al navbar con icono
  `bi-chat-dots` y clase `active` dinamica.
- `templates/index.html`: el boton FORO del hero pasa a apuntar a
  `foro.listar` en lugar de `auth.login`.
- `static/uploads/foro/`: directorio creado para almacenar las imagenes
  subidas por los usuarios del foro.

#### Validaciones realizadas

- Sintaxis Python verificada con `python3 -m py_compile` en todos los
  archivos nuevos y modificados.

## 2026-05-31 HH:MM:SS CEST

### Ajuste de permisos del modulo Foro

Se redefinieron las reglas de acceso a las acciones de edicion y borrado
en el foro para reflejar la politica operativa correcta:

| Accion         | Autor                  | Gestor | Admin |
|----------------|------------------------|--------|-------|
| Editar post    | Si, solo sin respuestas| No     | Si    |
| Borrar post    | Si                     | Si     | Si    |
| Borrar respuesta| Si                    | Si     | Si    |

#### Cambios en `routes/foro.py`

- `editar()`: el permiso de edicion se restringe a admin siempre y al
  autor solo si `ForoRespuesta.contar_por_post()` devuelve 0. El gestor
  pierde el permiso de edicion.
- `eliminar()`: se recupera el gestor en la lista de roles que pueden
  borrar posts (`admin` o `gestor` o autor).
- `eliminar_respuesta()`: idem, gestor puede borrar respuestas.

#### Cambios en plantillas

- `templates/foro/listar.html`: boton editar condicionado a
  `session.rol == 'admin'` o `(autor y num_respuestas == 0)`;
  boton borrar condicionado a autor, gestor o admin.
- `templates/foro/detalle.html`: misma logica para el post principal;
  boton borrar de cada respuesta condicionado a autor, gestor o admin.

## 2026-05-31 HH:MM:SS CEST

### Botones hero siempre visibles + nuevo modulo Novedades

#### Botones NOVEDADES y FORO en el hero

- Se elimina la condicion `{% if not session.user_id %}` para que ambos
  botones sean siempre visibles independientemente del estado de sesion.
- El boton NOVEDADES es dinamico:
  - Sin novedades nuevas: mismo estilo que FORO (`btn-outline-light`).
  - Con novedades sin ver: amarillo (`btn-warning`) con icono `bell-fill`.
- El enlace Novedades del navbar sigue la misma logica: texto amarillo
  y negrita + icono relleno si `hay_novedades` es True.

#### Nuevo modulo Novedades (`routes/novedades.py`)

- `GET  /novedades/`          listado de novedades; al visitar actualiza
  `session["novedades_vistas_hasta"]` para desactivar el indicador.
- `POST /novedades/nueva`     publicar novedad (solo admin).
- `POST /novedades/eliminar/<id>` eliminar novedad (solo admin).

#### Tracking de novedades no vistas

- `app.py` context_processor ampliado con `hay_novedades` (bool):
  - Si el usuario tiene `novedades_vistas_hasta` en sesion, compara la
    fecha de la ultima novedad de MongoDB con ese timestamp.
  - Si no tiene timestamp (primera visita), hay_novedades=True si existe
    alguna novedad en la coleccion.
  - Errores de conexion quedan silenciados para no romper la aplicacion.

#### Novedades en el navbar

- `templates/base.html`: se anade el enlace "Novedades" antes de
  "Viviendas" con clase `active` dinamica y color amarillo condicional.

## 2026-05-31 HH:MM:SS CEST

### Rediseno del modulo Novedades: nuevos campos y permisos de gestor

Se amplian los campos del modelo de novedad y se extienden los permisos
de publicacion al rol gestor.

#### Permisos

- Publicar y eliminar novedades: **admin y gestor** (antes solo admin).
- El decorador `@admin_required` se sustituye por `@gestor_required`
  en las rutas `nueva` y `eliminar` de `routes/novedades.py`.

#### Nuevos campos del documento novedad

| Campo          | Tipo    | Obligatorio |
|----------------|---------|-------------|
| tipo           | select  | Si          |
| destino        | texto   | No          |
| empleo         | texto   | No          |
| localidad      | texto   | No          |
| fecha_inicio   | fecha   | No          |
| fecha_fin      | fecha   | No          |
| observaciones  | textarea| No          |

- Los campos opcionales se guardan como `None` si estan vacios, y
  la plantilla los omite completamente en la vista (`{% if n.campo %}`).
- `TIPOS_NOVEDAD = ["Curso", "Comision de servicio", "Otros"]` definido
  en la ruta y pasado a la plantilla para el select del formulario.

#### Cambios en la plantilla

- Formulario: grid de 6 campos opcionales + select de tipo obligatorio.
- Vista de cada novedad: franja de color segun tipo (azul/verde/gris),
  badge de tipo, campos visibles solo si tienen valor, pie con autor y fecha.

## 2026-05-31 22:12:21 CEST

### Actualizacion visual de identidad FAMA

- Se incorpora el logo de FAMA en la barra de navegacion superior.
- Se elimina el texto `FAMA` del navbar para dejar solo el logo.
- Se ajusta el tamano, posicion vertical y separacion del logo respecto a los enlaces del menu.
- Se incorpora el logo en el bloque principal de inicio.
- Se elimina el titulo textual `FAMA` del hero y se mantiene el subtitulo `Foro de Apoyo Multiproposito de la Armada`.
- Se ajusta el tamano del logo central, su desplazamiento horizontal y la altura del bloque azul principal.
- Se genera y usa una version del logo con fondo transparente: `static/img/logofama-transparente.png`.
- Se realizan pruebas de mejora sobre los bordes del logo y se conserva una variante experimental con contorno azul: `static/img/logofama-contorno-azul.png`.

### Fotos de perfil de usuario

- Se anade el campo `foto_perfil` al modelo de usuario para nuevas cuentas.
- Se crea la ruta `/auth/perfil` para que cada usuario pueda subir, cambiar o eliminar su foto de perfil.
- Se crea la plantilla `templates/auth/perfil.html`.
- Las fotos de perfil se guardan en `static/uploads/perfiles/`.
- Se actualiza la sesion de usuario para incluir `foto_perfil` tras iniciar sesion o cambiar la foto.
- Se anade acceso a `Mi perfil` en el desplegable del usuario del navbar.
- Se muestra la foto de perfil del usuario en el navbar cuando existe.

### Integracion de avatares en el foro

- Se actualiza `routes/foro.py` para resolver la foto de perfil actual de cada autor mediante `usuario_id`.
- Se muestran avatares en el listado de publicaciones del foro.
- Se muestran avatares en el detalle de cada publicacion.
- Se muestran avatares en las respuestas del foro.
- Se incorpora un avatar por defecto para usuarios sin foto de perfil.
- Se anaden estilos CSS reutilizables para avatares en varios tamanos.

### Validaciones realizadas

- Se valida la sintaxis Python con:

```bash
python3 -m py_compile routes/auth.py routes/foro.py models/usuario.py
```

- La validacion termina sin errores.

## 2026-05-31 22:40:40 CEST

### Ampliacion del registro del ultimo bloque de cambios

Se completa el registro anterior dejando constancia detallada de todos los
archivos modificados o anadidos desde el ultimo cambio documentado,
independientemente de si los cambios fueron realizados por Codex, por el
usuario o por otra herramienta durante la sesion de desarrollo.

#### Archivos modificados

- `models/usuario.py`
  - Se incorpora `foto_perfil` al documento de usuario creado durante el registro.

- `routes/auth.py`
  - Se anaden utilidades internas para guardar y eliminar fotos de perfil.
  - Se validan extensiones permitidas: PNG, JPG, JPEG, GIF y WEBP.
  - Se guarda la imagen subida en `static/uploads/perfiles/`.
  - Se anade `session["foto_perfil"]` al iniciar sesion.
  - Se crea la ruta `/auth/perfil` para subir, cambiar y borrar la foto del usuario.

- `routes/foro.py`
  - Se anade `_anotar_fotos_autor()` para resolver la foto actual del autor.
  - El listado del foro anota `foto_autor` en cada publicacion.
  - El detalle del foro anota `foto_autor` en la publicacion principal y en cada respuesta.

- `templates/base.html`
  - El navbar pasa a mostrar el logo grafico de FAMA en lugar del texto con icono.
  - El desplegable de usuario muestra foto de perfil si existe.
  - Se anade enlace a `Mi perfil`.

- `templates/index.html`
  - El hero principal usa el logo grafico de FAMA.
  - Se mantiene el texto `Foro de Apoyo Multiproposito de la Armada`.
  - Se elimina el encabezado textual `FAMA`.

- `templates/foro/listar.html`
  - Se muestra avatar del autor en cada tarjeta de publicacion.
  - Se mantiene miniatura independiente para imagen adjunta del post.

- `templates/foro/detalle.html`
  - Se muestra avatar del autor en la cabecera de la publicacion.
  - Se muestra avatar del autor en cada respuesta.

- `static/css/estilos.css`
  - Se anaden estilos para el logo del navbar.
  - Se anaden estilos para el logo del hero central.
  - Se ajusta el hero central en altura y padding vertical.
  - Se anaden estilos reutilizables de avatar en tamanos nav, sm, md, lg y xl.
  - Se anade estilo de avatar por defecto para usuarios sin foto.

#### Archivos anadidos

- `templates/auth/perfil.html`
  - Nueva pantalla de perfil con previsualizacion de avatar.
  - Formulario de subida de foto.
  - Accion para eliminar la foto existente.

- `static/img/logofama.png`
  - Logo original incorporado al proyecto.

- `static/img/logofama-transparente.png`
  - Version del logo con fondo transparente, usada por la interfaz.

- `static/img/logofama-contorno-azul.png`
  - Variante experimental con contorno azul conservada para comparacion.

#### Estado de validacion

- Se mantiene como validacion realizada:

```bash
python3 -m py_compile routes/auth.py routes/foro.py models/usuario.py
```

- La validacion de sintaxis Python termino sin errores.

## 2026-05-31 22:46:31 CEST

### Prueba de ilustracion en el modulo Viviendas

- Se genera una ilustracion tipo acuarela para representar el modulo Viviendas.
- Se guarda el asset en `static/img/viviendas-ilustracion.png`.
- Se sustituye temporalmente el icono Bootstrap de la tarjeta `Viviendas` en la portada por la nueva ilustracion.
- Se anade la clase CSS `fama-modulo-img` para controlar tamano, recorte circular y encaje visual dentro de la tarjeta.
- El cambio afecta a `templates/index.html` y `static/css/estilos.css`.

## 2026-05-31 22:50:22 CEST

### Prueba de ilustracion en el modulo Servicios

- Se genera una ilustracion tipo acuarela para representar el modulo Servicios.
- Se guarda el asset en `static/img/servicios-ilustracion.png`.
- Se sustituye temporalmente el icono Bootstrap de la tarjeta `Servicios` en la portada por la nueva ilustracion.
- Se reutiliza la clase CSS `fama-modulo-img` para mantener coherencia visual con la tarjeta de Viviendas.
- El cambio afecta a `templates/index.html`.

## 2026-05-31 22:55:48 CEST

### Prueba de ilustracion de coches en Compra-Venta

- Se genera una ilustracion tipo acuarela centrada en coches para representar la tarjeta de Compra-Venta.
- Se guarda el asset en `static/img/compraventa-coches-ilustracion.png`.
- Se sustituye temporalmente el icono Bootstrap de la tarjeta `Compra-Venta` en la portada por la nueva ilustracion.
- Se reutiliza la clase CSS `fama-modulo-img` para mantener coherencia visual con Viviendas y Servicios.
- El cambio afecta a `templates/index.html`.

## 2026-05-31 23:04:55 CEST

### Correccion de ubicacion de la ilustracion de coches

- Se mueve la ilustracion `static/img/compraventa-coches-ilustracion.png` desde la tarjeta `Compra-Venta` a la tarjeta `Servicios`.
- Se restaura en `Compra-Venta` el icono Bootstrap original de tienda (`bi-shop`).
- El cambio afecta a `templates/index.html`.

## 2026-05-31 23:16:41 CEST

### Imagen de futbol en el modulo Ocio

- Se usa `static/img/futball.png` como imagen de la tarjeta `Ocio` en la portada.
- La tarjeta reutiliza la clase `fama-modulo-img` para mantener el mismo tamano y recorte circular que el resto de modulos ilustrados.
- El cambio queda reflejado en `templates/index.html`.

## 2026-06-01 CEST

### Reorganizacion del codigo utilitario

- Se elimina `utils/helpers.py` y su contenido se divide en dos modulos especializados:
  - `utils/decorators.py`: decoradores de control de acceso (`login_required`, `admin_required`, `gestor_required`).
  - `utils/logs.py`: funciones de auditoria (`registrar_log`, `actualizar_contadores`, `exportar_logs_pdf`).
- Se actualiza cada fichero que importaba `utils/helpers` para usar los nuevos modulos.
- Se mueve `crear_admin.py` a `scripts/crear_admin.py`.
- Se eliminan `node_modules/`, `package.json` y `package-lock.json` (artefactos de un `npm install resend` accidental).
- Se añade `node_modules/` a `.gitignore`.
- Se añade `static/uploads/perfiles/.gitkeep` para que Git rastree la carpeta de perfiles vacia.

### Subida de multiples fotos

Se implementa soporte para adjuntar varias imagenes en los modulos Viviendas, Servicios, Compraventa y Foro.

#### Nuevo fichero

- `utils/uploads.py`: centraliza la logica de subida y borrado de archivos.
  - `guardar_imagenes(archivos, subcarpeta)`: valida extension, genera nombre unico y guarda en `static/uploads/<subcarpeta>/`.
  - `eliminar_imagenes(nombres, subcarpeta)`: borra del disco los archivos indicados.
  - Todas las rutas que antes duplicaban esta logica pasan a usar estas funciones.

#### Modelos actualizados

- Se sustituye el campo `imagen` (string) por `fotos: []` (lista) en los modelos:
  - `models/vivienda.py`
  - `models/servicio.py`
  - `models/compraventa.py`
  - `models/foro.py` (`ForoPost` y `ForoRespuesta`): se conserva `imagen=None` para compatibilidad con posts antiguos.

#### Rutas actualizadas

- `routes/viviendas.py`, `routes/servicios.py`, `routes/compraventa.py`, `routes/foro.py`:
  - Lectura de lista de archivos con `request.files.getlist('fotos')`.
  - Al eliminar un anuncio se borran automaticamente sus imagenes del disco.

#### Plantillas actualizadas

- Formularios: `enctype="multipart/form-data"` + `<input multiple>` + miniaturas con checkbox de borrado individual en modo edicion.
- Detalles: imagen simple si hay 1 foto; carousel Bootstrap si hay mas de una.
- Listados: `card-img-top` con badge de conteo cuando hay mas de una foto.
- `templates/index.html`: miniatura 44×44 px en las mini-cards del dashboard de inicio.

#### Carpetas de uploads

- `static/uploads/viviendas/`
- `static/uploads/servicios/`
- `static/uploads/compraventa/`
- `static/uploads/foro/`
- `static/uploads/perfiles/`

### Canales en el modulo Foro

Se reorganiza el Foro con un sistema de canales tematicos.

#### Modelo nuevo

- `ForoCanal` en `models/foro.py` sobre la coleccion `foro_canales`.
  - Campos: `nombre`, `descripcion`, `color` (clase Bootstrap), `icono` (Bootstrap Icon), `usuario_id`, `fecha_creacion`.
- `ForoPost` incorpora el campo obligatorio `canal_id`.

#### Rutas

| Metodo | URL | Descripcion |
|--------|-----|-------------|
| GET | `/foro/` | Lista de canales (tarjetas con color e icono) |
| GET/POST | `/foro/canal/nuevo` | Crear canal |
| GET | `/foro/canal/<id>` | Posts del canal |
| GET/POST | `/foro/canal/<id>/nuevo` | Nuevo post en el canal |
| POST | `/foro/canal/eliminar/<id>` | Borrar canal y todos sus posts |

#### Permisos

| Accion | Permisos |
|--------|----------|
| Crear canal | Cualquier usuario autenticado |
| Eliminar canal | Admin y gestor |
| Editar post | Autor (el suyo) + admin (todos) |
| Borrar post | Autor (el suyo) + admin y gestor (todos) |
| Borrar respuesta | Autor (la suya) + admin y gestor (todas) |

#### Plantillas nuevas

- `templates/foro/listar.html`: rejilla de tarjetas de canal con color e icono.
- `templates/foro/canal.html`: listado de posts de un canal.
- `templates/foro/nuevo_canal.html`: formulario con preview en tiempo real de color e icono.

#### Migracion de datos

Para asignar canal a posts existentes sin `canal_id`:

```js
db.foro_posts.updateMany({canal_id: {$exists: false}}, {$set: {canal_id: "<id_canal>"}})
```

### Nuevo flujo de registro y validacion de usuarios

Se redisena el alta de usuarios para incluir verificacion de email y aprobacion manual por el admin.

#### Flujo completo

1. El usuario rellena solo **nombre + email** (sin contrasenia ni pregunta de seguridad).
2. El sistema crea la cuenta con `email_verificado=False, validado=False` y una contrasenia interna aleatoria.
3. **Resend** envia un email de verificacion con enlace firmado (token `itsdangerous`, expira en 24 h).
4. El usuario hace clic → `email_verificado=True`.
5. El admin ve el badge **"Pendiente"** en el panel y pulsa el boton de aprobacion.
6. Al aprobar: se genera una contrasenia temporal aleatoria (10 caracteres), se envia por email y se marca `debe_cambiar_password=True`.
7. El usuario hace login con la contrasenia temporal y queda forzado a cambiarla en el primer acceso.

#### Nuevos campos en la coleccion `usuarios`

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `email_verificado` | Boolean | `False` hasta que el usuario hace clic en el enlace |
| `validado` | Boolean | `False` hasta la aprobacion manual del admin |
| `debe_cambiar_password` | Boolean | `True` tras la aprobacion; se desactiva al cambiar contrasenia |

#### Archivos modificados o creados

- `models/usuario.py`: `crear()` sin campo contrasenia, `generar_password_temporal()`, `establecer_password_temporal()`, `verificar_email_usuario()`, `validar_usuario()`.
- `routes/auth.py`: registro simplificado a nombre + email, ruta `/auth/verificar-email/<token>`, mensajes de login diferenciados por estado de cuenta.
- `routes/admin.py`: ruta `/admin/usuarios/validar/<user_id>` que genera la contrasenia temporal y envia el email de aprobacion.
- `utils/email.py` (nuevo): `enviar_verificacion_email()`, `enviar_aprobacion_cuenta()`.
- `utils/config.py`: variables `RESEND_API_KEY`, `MAIL_FROM`, `APP_URL`.
- `.env`: API key de Resend, dominio `noreply@appfama.es`.
- `templates/auth/registro.html`: formulario reducido a nombre + email.

#### Servicio de email

- Proveedor: **Resend** (resend.com).
- Remitente: `FAMA <noreply@appfama.es>` (dominio dado de alta en IONOS, pendiente de confirmacion DNS en Resend).
- API key almacenada en `.env`, nunca en el codigo fuente.

#### Migracion de usuarios existentes

```js
db.usuarios.updateMany(
  {email_verificado: {$exists: false}},
  {$set: {email_verificado: true, validado: true}}
)
```

### Mejoras en el panel de administracion

- Las estadisticas del panel pasan a ocupar una sola fila usando `col` (distribucion automatica Bootstrap) en lugar de `col-lg-2`.
- La tarjeta "Pendientes" se resalta en rojo cuando hay usuarios esperando validacion.
- El dropdown de cambio de rol en la tabla de usuarios se corrige con `overflow:visible` + `data-bs-boundary="viewport"` para evitar que quede cortado por el contenedor; se muestra una marca visual en el rol activo.

### Mejoras visuales generales

- Se eliminan los breadcrumbs de todas las paginas de detalle: viviendas, servicios, compraventa, ocio, foro/detalle, foro/canal, foro/formulario y foro/nuevo_canal.
- El dashboard de inicio reduce el limite de anuncios mostrados por seccion de 4 a 3.
- La tabla de usuarios del panel admin incorpora `overflow:visible` para que el dropdown de roles no quede recortado.

## 2026-06-02 CEST

### Simplificacion del flujo de registro y validacion de usuarios

Se redisena el flujo de alta eliminando el paso de verificacion de email.
El nuevo flujo es mas sencillo y adecuado para una plataforma cerrada interna.

#### Flujo nuevo

1. El usuario rellena solo **nombre + email**.
2. El sistema crea la cuenta con `email_verificado=True` y `validado=False`.
3. Se envia email de aviso: *"Tu solicitud esta pendiente de validacion. Este proceso puede durar unas horas."*
4. El admin ve el badge **Pendiente** en el panel y pulsa el boton de aprobacion.
5. Al aprobar: se establece la contrasenia a `fama1234`, `debe_cambiar_password=True`, y se envia email: *"Tu cuenta ha sido aprobada. Tu contrasenia es fama1234. Cambiala en el primer inicio de sesion."*
6. El usuario hace login con `fama1234` y queda forzado a cambiarla antes de continuar.

#### Archivos modificados

- `utils/email.py`:
  - Eliminadas las funciones de token `itsdangerous` (`generar_token_verificacion`, `confirmar_token_verificacion`).
  - Eliminada `enviar_verificacion_email()`.
  - Nueva `enviar_pendiente_validacion()`: notifica que la cuenta espera aprobacion.
  - `enviar_aprobacion_cuenta()`: simplificada — ya no recibe contrasenia aleatoria ni incluye enlace; muestra `fama1234` directamente.

- `models/usuario.py`:
  - `crear()`: `email_verificado=True` por defecto (sin paso de verificacion).
  - Eliminados `generar_password_temporal()` y `verificar_email_usuario()`.

- `routes/auth.py`:
  - Eliminada la ruta `/auth/verificar-email/<token>`.
  - Registro llama a `enviar_pendiente_validacion()`.
  - Login simplificado: solo avisa de "pendiente de validacion" si procede; ya no comprueba `email_verificado`.

- `routes/admin.py`:
  - `validar_usuario()`: usa `fama1234` directamente en vez de contrasenia aleatoria.
  - Query de pendientes en el panel ya no filtra por `email_verificado`.

- `templates/admin/usuarios.html`:
  - Eliminado el badge "Sin verificar" (ya no existe ese estado).
  - Boton de validacion ya no exige `email_verificado=True` para mostrarse.

#### Migracion ejecutada

```js
db.usuarios.updateMany(
  {email_verificado: {$ne: true}},
  {$set: {email_verificado: true}}
)
```

### Contrasenia por defecto unificada a fama1234

- `models/usuario.py` — `resetear_password()`: cambia la contrasenia a `fama1234` en vez de `Password`.
- `routes/admin.py` — `validar_usuario()`: usa `fama1234` al aprobar una cuenta.
- `scripts/resetear_passwords.py` (nuevo): pone `fama1234` y `debe_cambiar_password=True` a todos los usuarios excepto `admin@appfama.es`. Util para entornos de desarrollo.

### Cambio de email del administrador

- El email de login del administrador cambia de `admin@fama.es` a `admin@appfama.es`.
- Archivos actualizados: `scripts/crear_admin.py`, `scripts/resetear_passwords.py`.
- Documento actualizado en MongoDB:

```js
db.usuarios.updateOne(
  {email: "admin@fama.es"},
  {$set: {email: "admin@appfama.es"}}
)
```

### Verificacion del dominio de email appfama.es

- Se confirma que el dominio `appfama.es` queda verificado en Resend con los registros DNS dados de alta en IONOS.
- El sistema de envio de emails transaccionales desde `noreply@appfama.es` queda operativo.

## 2026-06-02 20:32:51 CEST

### Ajustes visuales de logo y navegacion

- Se sustituye el logo usado en la pagina por `static/img/famalogo.png`.
- Se actualizan las referencias del logo en:
  - `templates/base.html`
  - `templates/index.html`
- Se edita `static/img/famalogo.png` para eliminar el fondo gris y dejarlo con transparencia real.
- Se corrigen zonas del propio logo que habian quedado mal tras la extraccion del fondo:
  - Correccion de blancos en el faro.
  - Correccion de blancos en el tejado de la casa.
  - Perfilado puntual de bordes irregulares en la zona del faro.
- Se ajusta el hero de la pagina principal:
  - El logo central queda centrado horizontalmente.
  - El texto "Foro de Apoyo Multiproposito de la Armada" baja para no solaparse con el logo.
- Se ajusta la barra de navegacion superior:
  - El logo del navbar queda mejor centrado verticalmente.
  - Se reduce el espacio entre el logo y el enlace "Novedades".
  - Se desplaza ligeramente el conjunto inicial de la navegacion para compactar la cabecera.

#### Archivos modificados

- `static/img/famalogo.png`
- `static/css/estilos.css`
- `templates/base.html`
- `templates/index.html`

## 2026-06-02 CEST (segunda sesión)

### Eliminación del sistema de emails

- Se elimina `utils/email.py` y se retira `resend==2.10.0` de `requirements.txt`.
- Se eliminan las variables `RESEND_API_KEY`, `MAIL_FROM` y `APP_URL` de `utils/config.py`.
- El registro ya no envía ningún correo: el flujo es únicamente nombre + email → validación manual por admin.

### Login por nombre de usuario

- El campo de login cambia de email a **nombre de usuario** (que debe ser único en la BD).
- `models/usuario.py` — `autenticar()` busca ahora por `nombre` en lugar de email.
- `models/usuario.py` — `crear()` valida unicidad de nombre (case-insensitive) antes de insertar.
- `models/usuario.py` — `verificar_respuesta_seguridad()` acepta nombre en lugar de email.
- `routes/auth.py` — login, cambiar_password y recuperar_password usan campo `nombre`.
- `templates/auth/login.html` — campo "Nombre de usuario" en lugar de "Email".
- `templates/auth/recuperar.html` — campo "Nombre de usuario" en lugar de "Email".

### Validación de email simplificada

- El registro solo exige que el email contenga `@`; el campo pasa a `type="text"`.
- El texto de la página de registro ya no menciona verificación de correo.

### Transferencia de rol de administrador

- Al asignar rol `admin` a otro usuario, la cuenta del admin promotor se elimina y la sesión se cierra.
- Esto garantiza una transferencia limpia del poder de administración.
- `routes/admin.py` — `cambiar_rol()` ampliado con esta lógica.

### Protección del último administrador

- No es posible eliminar (desactivar) al único admin activo de la plataforma.
- `routes/admin.py` — `eliminar_usuario()`: comprueba `count_documents({rol: admin, activo: True}) <= 1` antes de permitir la operación.
- Los admins pueden eliminar a otros admins siempre que no sea el último.

### Restauración de iconos Bootstrap en tarjetas de módulos

- Se eliminan las ilustraciones (`viviendas-ilustracion.png`, `viaje.png`, `mercadillo.png`, `futball.png`) de las tarjetas del dashboard.
- Se restauran los iconos Bootstrap originales: `bi-house-door`, `bi-tools`, `bi-shop`, `bi-trophy`.

### Corrección de faltas de ortografía en el frontend

- `Contrasenia` → `Contraseña` en todos los templates visibles al usuario:
  - `templates/auth/login.html`, `cambiar_password.html`, `recuperar.html`
  - `templates/base.html`, `templates/admin/usuarios.html`, `panel.html`, `ver_usuario.html`

### Perfil de usuario ampliado

- `templates/auth/perfil.html` muestra ahora: avatar, nombre, rol (badge de color), email y fecha de registro.
- La sección de subida/borrado de foto se mantiene en una tarjeta separada.

### Aviso de edición por gestor o admin

- Cuando un gestor o admin edita un anuncio que no es suyo, se guardan `editado_por` y `fecha_edicion` en el documento MongoDB.
- El detalle de cada módulo muestra un aviso amarillo con el nombre del editor y la fecha.
- Módulos afectados: `routes/viviendas.py`, `routes/servicios.py`, `routes/compraventa.py`, `routes/ocio.py` y sus respectivos `detalle.html`.

### Sistema de reportes de anuncios

- Los gestores pueden reportar cualquier anuncio (vivienda, servicio, compraventa, ocio) indicando un motivo.
- Los reportes se almacenan en la colección `reportes` de MongoDB.
- Nueva ruta `POST /admin/reportes/nuevo` — crea el reporte.
- Nueva ruta `GET /admin/reportes` — lista reportes para gestores y admins.
- Nueva ruta `POST /admin/reportes/resolver/<id>` — marca como resuelto (solo admin).
- Nueva ruta `POST /admin/reportes/eliminar/<id>` — elimina el reporte (solo admin).
- `templates/admin/reportes.html` — tabla de reportes con estado y acciones.
- El panel de administración incluye una tarjeta de acceso rápido a reportes.

### Test de conexión a base de datos

- Nueva ruta `GET /admin/test-bd` (solo admin): hace ping a MongoDB y muestra el resultado como mensaje flash.
- `templates/admin/panel.html` — nueva tarjeta "Base de datos" con botón "Probar conexión".

### Documentación PRIMER_ADMIN.md

- Creado `documentacion/PRIMER_ADMIN.md` con instrucciones paso a paso para crear el primer administrador en un despliegue nuevo.

### Simulación de rol para el administrador

El admin puede actuar temporalmente como gestor o usuario para comprobar cómo se ve la aplicación desde cada perfil sin necesidad de crear cuentas adicionales.

#### Funcionamiento

- En el desplegable de usuario del navbar aparece la sección **Simular rol** con las opciones Admin, Gestor y Usuario.
- Al seleccionar un rol, `session["rol_real"]` guarda el rol original y `session["rol"]` cambia al simulado.
- Todos los checks de permisos existentes funcionan automáticamente con el rol simulado.
- Un **banner amarillo** fijo aparece en la parte superior indicando qué rol se está simulando y ofreciendo un enlace para volver a Admin.
- Al cerrar sesión, `session.clear()` elimina tanto el rol simulado como el real.

#### Archivos modificados

- `routes/auth.py` — nueva ruta `GET /auth/simular-rol/<rol>` protegida por `@login_required`; solo accesible si `rol_real == 'admin'` o `rol == 'admin'`.
- `templates/base.html` — sección de simulación en el dropdown de usuario y banner amarillo condicional cuando la simulación está activa.

### Auditoría de portabilidad y commit de todos los cambios

Se verifica que la aplicación puede iniciarse en cualquier dispositivo con solo Docker instalado y los ficheros del repositorio git.

#### Problemas detectados y resueltos

| Problema | Solución |
|----------|----------|
| Más de 30 ficheros modificados sin commitear | Añadidos al staging y commiteados |
| `static/img/famalogo.png` no estaba en git | Añadido al commit |
| `templates/admin/reportes.html` no estaba en git | Añadido al commit |
| `documentacion/PRIMER_ADMIN.md` no estaba en git | Añadido al commit |
| `utils/email.py` borrado en disco pero aún en git | `git rm utils/email.py` |
| Logos antiguos borrados en disco pero aún en git | `git rm` de `logofama.png`, `logofama-transparente.png`, `logofama-contorno-azul.png` |
| `.env.example` con variables Resend obsoletas | Limpiado; aclarado que con Docker no es necesario `.env` |

#### Procedimiento de inicio desde clon limpio

```bash
git clone <repo>
cd FAMA
docker compose up -d --build
docker compose exec web python scripts/crear_admin.py
```

Acceso en `http://localhost:8000`. Solo se necesita Docker; Python, pip y cualquier otra herramienta local son innecesarios.

## 2026-06-02 CEST (tercera sesión)

### Protección global de acceso: toda la app requiere login

- Se añade `@app.before_request` en `app.py` que redirige al login si no hay sesión activa.
- Quedan libres únicamente las rutas del blueprint `auth` y los ficheros estáticos.
- Cualquier ruta nueva añadida en el futuro queda protegida automáticamente sin necesidad de `@login_required` individual.

### Credenciales del admin bootstrap actualizadas

- Nombre de usuario cambiado de `Administrador FAMA` a `admin`.
- Contraseña cambiada de `Admin1234` a `admin1234`.
- Actualizado `scripts/crear_admin.py` y `documentacion/PRIMER_ADMIN.md`.
- Documento MongoDB actualizado con el nuevo nombre y contraseña.

### Instrucciones de contraseña por defecto en PRIMER_ADMIN.md

- Añadida tabla en `documentacion/PRIMER_ADMIN.md` explicando que la contraseña por defecto `fama1234` se asigna en dos situaciones: aprobación de cuenta nueva y reseteo manual desde el panel.

### Pre-relleno del login al transferir rol de administrador

- Al transferir el rol `admin` a otro usuario, la redirección al login incluye el nombre del nuevo admin como parámetro URL (`?nuevo_admin=...`).
- El formulario de login muestra ese nombre prerrellenado, con fondo amarillo, campo bloqueado (`readonly`) y un aviso indicando que se debe iniciar sesión como el nuevo administrador.
- Archivos modificados: `routes/admin.py`, `templates/auth/login.html`.

### Reactivación y eliminación definitiva de usuarios inactivos

- Los usuarios desactivados muestran ahora dos botones en la tabla de usuarios del panel admin:
  - **Reactivar** (verde): restaura `activo=True`.
  - **Eliminar definitivamente** (rojo): borra el documento de MongoDB de forma permanente, con confirmación previa.
- Nueva ruta `POST /admin/usuarios/reactivar/<id>` — solo admin.
- Nueva ruta `POST /admin/usuarios/eliminar-definitivo/<id>` — solo admin.
- Nuevos métodos `reactivar()` y `eliminar_definitivo()` en `models/usuario.py`.
- Archivos modificados: `routes/admin.py`, `models/usuario.py`, `templates/admin/usuarios.html`.

### Corrección del script crear_admin.py

- Añadido `sys.path.insert` para que el script encuentre el módulo `utils` al ejecutarse desde dentro del contenedor Docker.

### Auditoría de coherencia del código

Se revisa todo el código en busca de inconsistencias y se aplican las siguientes correcciones:

| # | Fichero | Problema | Solución |
|---|---------|----------|----------|
| 1 | `routes/admin.py` | Docstring de `resetear_password` mencionaba `'Password'` | Actualizado a `fama1234` |
| 2 | `routes/admin.py` | Estadística de usuarios filtraba por `email_verificado: True` (siempre verdadero) | Filtro eliminado |
| 3 | `routes/auth.py` | `session["email"]` se guardaba en sesión pero ninguna ruta ni template lo usaba | Eliminado |
| 4 | `templates/admin/ver_usuario.html` | Badge "Sin verificar" y condición de validación usaban `email_verificado` (rama muerta) | Eliminadas ambas referencias |
| 5 | `scripts/crear_admin.py` | Docstring listaba credenciales antiguas (`admin@fama.es` / `Admin1234`) | Actualizado a `admin@appfama.es` / `admin1234` |

## 2026-06-04 CEST

### Rediseño del formulario de registro

- El formulario de registro pasa de 2 campos (nombre + email) a 8 campos completos.
- Campos nuevos: **ID de usuario** (login), **nombre**, **apellidos**, **contraseña**, **confirmar contraseña**, **pregunta de seguridad** (desplegable), **respuesta**.
- El usuario establece su propia contraseña al registrarse; ya no se genera una contraseña temporal.
- La validación por admin sigue siendo obligatoria antes de poder iniciar sesión, pero al aprobar ya no se sobreescribe la contraseña.
- Archivos modificados: `templates/auth/registro.html`, `routes/auth.py`, `models/usuario.py`, `routes/admin.py`.

### Preguntas de seguridad predeterminadas

- Se definen 4 preguntas de seguridad fijas en `routes/auth.py` como constante `PREGUNTAS_SEGURIDAD`:
  - ¿Cuál es el nombre de tu primera mascota?
  - ¿En qué ciudad naciste?
  - ¿Cuál es el nombre de tu madre?
  - ¿Cuál es tu película favorita?
- El campo de pregunta de seguridad en el registro pasa a ser un `<select>` con esas 4 opciones.
- La respuesta se almacena hasheada en MongoDB.

### Recuperación de contraseña por pasos

- El flujo de recuperación se divide en 3 pasos con indicador visual:
  1. Introducir ID de usuario.
  2. Responder la pregunta de seguridad (se muestra la pregunta guardada).
  3. Solo si la respuesta es correcta, introducir y confirmar la nueva contraseña.
- Se usan claves de sesión (`rec_nombre`, `rec_verificado`) para mantener el estado entre pasos de forma segura.
- Archivos modificados: `routes/auth.py` (`recuperar_password()`), `templates/auth/recuperar.html`.

### Cambio de etiqueta: "Nombre de usuario" → "ID de usuario"

- La etiqueta del campo de login pasa a llamarse **ID de usuario** en `templates/auth/login.html` y `templates/auth/registro.html` para mayor claridad.

### Selector de roles: renombrado y ampliado al gestor

- La sección **Simular rol** del navbar pasa a llamarse **Elegir rol** (icono `person-gear`).
- Se elimina el banner amarillo de "Simulando rol X" que aparecía en la parte superior.
- Los gestores pueden ahora cambiar entre su rol (`gestor`) y `usuario` sin necesidad de ser admin.
- El admin sigue pudiendo elegir entre los tres roles (`admin`, `gestor`, `usuario`).
- Archivos modificados: `templates/base.html`, `routes/auth.py` (`simular_rol()`).

### Acceso público sin login obligatorio

- Se elimina la redirección global a login para usuarios no autenticados.
- Los listados, detalles, foro y calendario son accesibles libremente.
- Las rutas interactivas (crear, editar, eliminar, inscribirse, responder) siguen protegidas por `@login_required` individualmente y redirigen al login al intentar usarlas.
- El `before_request` pasa a llamarse `verificar_sesion` y solo comprueba que los usuarios ya autenticados siguen activos y validados.
- Archivos modificados: `app.py`.

### Botones de acción visibles para usuarios no autenticados

- Los botones de **Publicar**, **Crear evento**, **Nueva publicación**, **Inscribirme** y el formulario de respuesta del foro son ahora visibles para todos los visitantes.
- Al interactuar con ellos sin sesión, la ruta protegida redirige automáticamente al login.
- Los botones de **Editar** y **Eliminar** siguen ocultos para quien no sea propietario o admin/gestor.
- Los estados vacíos ("Publica el primero", "Ser el primero en publicar") también muestran el botón a todos.
- Archivos modificados: `templates/viviendas/listar.html`, `templates/servicios/listar.html`, `templates/compraventa/listar.html`, `templates/compraventa/armada.html`, `templates/ocio/listar.html`, `templates/ocio/calendario.html`, `templates/ocio/detalle.html`, `templates/foro/listar.html`, `templates/foro/canal.html`, `templates/foro/detalle.html`.

### Creación de usuarios desde el panel admin

- El admin dispone de un botón **Crear usuario** en la cabecera del listado de usuarios.
- Al pulsarlo se abre un modal Bootstrap `modal-lg` con el mismo formulario de 8 campos que el registro público.
- La cuenta se crea directamente como **activa y validada** (sin paso de aprobación).
- Nueva ruta `POST /admin/usuarios/crear` con `@admin_required`.
- Archivos modificados: `routes/admin.py`, `templates/admin/usuarios.html`.

### Reporte de usuarios por el gestor

- Los gestores disponen de un botón **Reportar usuario** en la ficha de cada usuario (`/admin/usuarios/ver/<id>`).
- Al pulsarlo se abre un modal pequeño centrado con un campo de texto para el motivo.
- Los reportes se almacenan en la colección `reportes` con `tipo_reporte: "usuario"` (separado de los reportes de anuncios).
- Nueva ruta `POST /admin/usuarios/reportar/<user_id>` con `@gestor_required`.
- Archivos modificados: `routes/admin.py`, `templates/admin/ver_usuario.html`.

### Bloqueo de fechas pasadas en eventos de ocio

- El campo de fecha del formulario de eventos incluye `min="{{ now.strftime('%Y-%m-%d') }}"` para bloquear la selección de fechas pasadas en el navegador.
- Validación adicional en servidor en `routes/ocio.py` (rutas `nuevo` y `editar`) para rechazar fechas anteriores a la fecha actual aunque se manipule el HTML.
- Archivos modificados: `templates/ocio/formulario.html`, `routes/ocio.py`.

### Icono de Bootstrap actualizado en el módulo Servicios

- Se sustituye el icono `bi-gear` / `bi-tools` por `bi-car-front` en todos los puntos donde aparecía el módulo Servicios.
- Archivos modificados: `templates/servicios/listar.html`, `templates/servicios/formulario.html`, `templates/base.html` (navbar), `templates/index.html` (tarjeta del módulo).

### Lightbox y zoom en fotos de anuncios

- Al pasar el ratón sobre la foto de un anuncio en los listados, la imagen se amplía suavemente (`scale(1.08)`) gracias a las clases CSS `.fama-img-wrap` (con `overflow:hidden`) y `.fama-img-zoom` (con `transition`).
- Al hacer clic en la foto se abre un modal Bootstrap a pantalla completa con la imagen ampliada sobre fondo negro.
- Si el anuncio tiene varias fotos, aparecen flechas izquierda/derecha para navegar entre ellas y un contador `N / Total` en la esquina inferior.
- La navegación también funciona con las teclas ← → del teclado.
- El modal `#famaLightbox` se declara una sola vez en `templates/base.html` y es reutilizable en toda la aplicación.
- Las imágenes reciben los atributos `data-fotos` (array JSON de URLs absolutas de todas las fotos del anuncio) y `data-index="0"`.
- Archivos modificados: `static/css/estilos.css`, `static/js/scripts.js`, `templates/base.html`, `templates/viviendas/listar.html`, `templates/servicios/listar.html`, `templates/compraventa/listar.html`.

### Fecha límite y eliminación automática de anuncios

- Los formularios de creación y edición de Viviendas, Servicios y Compraventa incluyen un campo opcional **Fecha límite**.
- El campo tiene `min="{{ now.strftime('%Y-%m-%d') }}"` para impedir seleccionar fechas pasadas.
- La fecha se almacena en MongoDB como `datetime(año, mes, día, 23, 59, 59)` (fin del día seleccionado), de modo que el anuncio es visible durante todo el día elegido.
- En `app.py` se define la función `_limpiar_expirados()` que consulta las colecciones `viviendas`, `servicios` y `compraventa` buscando documentos con `fecha_expiracion <= ahora`, elimina sus fotos del disco con `eliminar_imagenes()` y borra los documentos de MongoDB.
- La limpieza se invoca desde el `before_request` (`verificar_sesion`) como máximo **una vez por hora**, controlada por la variable global `_ts_limpieza`.
- Las tarjetas de los listados muestran un indicador naranja `⏰ Expira DD/MM/AAAA` si el anuncio tiene fecha límite.
- Archivos modificados: `app.py`, `models/vivienda.py`, `models/servicio.py`, `models/compraventa.py`, `routes/viviendas.py`, `routes/servicios.py`, `routes/compraventa.py`, `templates/viviendas/formulario.html`, `templates/servicios/formulario.html`, `templates/compraventa/formulario.html`, `templates/viviendas/listar.html`, `templates/servicios/listar.html`, `templates/compraventa/listar.html`.

### Bloqueo de fechas pasadas extendido a Novedades

- Los campos `fecha_inicio` y `fecha_fin` del formulario de publicación de novedades incluyen `min="{{ now.strftime('%Y-%m-%d') }}"`.
- Validación en servidor en `routes/novedades.py`: rechaza fechas pasadas en ambos campos y verifica que `fecha_fin >= fecha_inicio`.
- Archivos modificados: `templates/novedades/listar.html`, `routes/novedades.py`.

### Favicon FAMA

- Añadida línea `<link rel="icon" type="image/png" href=".../famalogo.png">` en el `<head>` de `templates/base.html`.
- El logo de FAMA aparece ahora en la pestaña del navegador en todas las páginas.
- Archivo modificado: `templates/base.html`.

### Alertas de administrador en el navbar

- El enlace **Panel Admin** del navbar muestra un badge rojo con el total de alertas pendientes cuando hay usuarios sin validar o reportes sin resolver.
- Al pasar el ratón sobre el badge se muestra el desglose: "N usuario(s) pendiente(s) · N reporte(s) sin resolver".
- Los contadores se calculan en el `context_processor` de `app.py` para admin y gestor; se usan `rol_real` o `rol` de sesión para detectar el rol incluso durante simulación.
- Archivos modificados: `app.py`, `templates/base.html`.

### Botón "Reportar usuario" en la tabla de usuarios

- Los gestores disponen del botón `bi-flag` (reportar) en cada fila de la tabla de usuarios (`/admin/usuarios`), al lado de los botones de resetear contraseña y ver ficha.
- Se usa un único modal dinámico `#modalReportarTabla` cuyos datos (nombre del usuario y URL de la acción) se actualizan via el evento `show.bs.modal` de Bootstrap al hacer clic.
- El modal de la ficha individual (`ver_usuario.html`) se mantiene independiente.
- Archivos modificados: `templates/admin/usuarios.html`.

### Enlace al objeto reportado en la tabla de reportes

- La columna **Objeto reportado** en `templates/admin/reportes.html` muestra un enlace clicable hacia el anuncio o usuario reportado en lugar del ID crudo.
- Para reportes de usuario: enlaza a la ficha del usuario en el panel admin (mismo tab).
- Para reportes de anuncio: enlaza al detalle del anuncio en pestaña nueva (`target="_blank"`) con icono de enlace externo.
- La lógica usa `mod = tipo_modulo | lower` y comparaciones con `in mod` para tolerar variaciones de capitalización y forma singular/plural: `'viviend'`, `'servicio'`, `'compra'`, `'ocio'`.
- El badge de tipo usa colores diferenciados por módulo: azul (vivienda), verde (servicio), amarillo (compraventa), cian (ocio), amarillo oscuro (usuario).
- Título de la página actualizado de "Reportes de anuncios" a "Reportes".
- Archivos modificados: `templates/admin/reportes.html`.

### Paginación configurable en paneles admin (10 / 25 / 50 / 100)

- Los tres listados del panel admin disponen de un selector "Mostrar N por página" (valores: 10, 25, 50, 100; por defecto 10).
- El selector se envía por GET con `onchange`, preservando el resto de filtros activos (búsqueda en usuarios, tipo en logs).
- **Usuarios**: la paginación ya existía fija en 10; ahora lee `por_pagina` del parámetro GET y lo propaga a todos los enlaces de paginación y al formulario de búsqueda.
- **Logs**: se añade paginación completa (antes cargaba todos); el contador total aparece en el título; la exportación PDF sigue exportando todos los logs del filtro activo.
- **Reportes**: se añade paginación completa (antes cargaba todos); el contador total aparece en el título.
- Archivos modificados: `routes/admin.py`, `templates/admin/usuarios.html`, `templates/admin/logs.html`, `templates/admin/reportes.html`.

### Creación de usuarios por admin — forzar cambio de contraseña

- Al crear un usuario desde el panel admin se activa `debe_cambiar_password = True` justo después de insertar el documento.
- El usuario creado por el admin iniciará sesión con la contraseña asignada y será redirigido a `/auth/cambiar-password` antes de poder continuar.
- El aviso del modal se actualiza para informar de este comportamiento.
- Archivo modificado: `routes/admin.py`, `templates/admin/usuarios.html`.

### Requisitos de contraseña segura e indicador visual

- Las contraseñas deben cumplir: mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial.
- Nueva función `validar_password_fuerte()` en `utils/validators.py` usada en todas las rutas que aceptan contraseñas nuevas: registro, cambiar contraseña, recuperación y creación de usuario por admin.
- Indicador visual rediseñado: icono `!` amarillo (`bi-exclamation-circle`) a la derecha del campo de contraseña (dentro de un `input-group`). Al pasar el ratón encima aparece un **popover Bootstrap** titulado "Requisitos de contraseña" con los 5 puntos en tiempo real (gris/verde según se cumplan). Cuando todos los requisitos están cubiertos el icono cambia a `✓` verde (`bi-check-circle-fill`). Implementado en `static/js/scripts.js` usando `bootstrap.Popover` con `setContent()` dinámico; se auto-descubre via `data-pwd-indicator` y funciona dentro de modales (evento `shown.bs.modal`).
- El atributo `minlength` de todos los campos de contraseña nueva actualizado de 6 a 8.
- Archivos modificados/creados: `utils/validators.py` (nuevo), `routes/auth.py`, `routes/admin.py`, `static/js/scripts.js`, `templates/auth/registro.html`, `templates/auth/cambiar_password.html`, `templates/auth/recuperar.html`, `templates/admin/usuarios.html`.

### Flujo de primer acceso para usuarios creados por admin

- El admin crea usuarios **sin pregunta de seguridad** (se elimina ese campo del modal de creación).
- Al primer inicio de sesión, si la cuenta tiene `debe_cambiar_password=True` y `pregunta_seguridad=None`, el login redirige a `/auth/primer-acceso` en lugar de `/auth/cambiar-password`.
- La página de primer acceso (`templates/auth/primer_acceso.html`) pide en un único formulario: nueva contraseña (con indicador visual) + pregunta de seguridad + respuesta.
- Tras completar el formulario se actualiza la contraseña (`cambiar_password`), se guarda la pregunta/respuesta (`configurar_seguridad` en modelo) y se elimina el flag.
- Nuevo método `configurar_seguridad()` añadido a `models/usuario.py`.
- Archivos modificados/creados: `models/usuario.py`, `routes/auth.py`, `routes/admin.py`, `templates/admin/usuarios.html`, `templates/auth/primer_acceso.html` (nuevo).

### Búsquedas de usuario e email sin distinción de mayúsculas/minúsculas

- `autenticar()` en `models/usuario.py` usa `$regex ... $options: "i"` para que el login funcione independientemente de la capitalización del ID de usuario.
- La búsqueda del candidato "pendiente de validación" en el login también usa regex case-insensitive.
- El email siempre se normaliza a minúsculas con `.strip().lower()` en las rutas antes de guardarse.
- La respuesta de seguridad se normaliza con `.lower()` tanto al guardar (hash) como al verificar.
- Archivos modificados: `models/usuario.py`, `routes/auth.py`.

### Sección "Mis anuncios" en el perfil de usuario

- La página de perfil (`/auth/perfil`) muestra ahora en la columna derecha todos los anuncios publicados por el usuario, agrupados por módulo: Viviendas, Servicios, Compra-Venta y Ocio.
- Cada anuncio muestra su tipo/título principal, precio o fecha según módulo, y un botón **Ver** que redirige al detalle del anuncio.
- Si el anuncio tiene fecha límite se muestra el icono de reloj con la fecha.
- Si el usuario no tiene anuncios en ningún módulo se muestra un mensaje informativo.
- La ruta `perfil()` consulta los 4 colecciones de MongoDB filtrando por `usuario_id` y las pasa al template como `mis_anuncios`.
- La página se reestructura en layout de dos columnas (col-md-4 / col-md-8).
- Archivos modificados: `routes/auth.py`, `templates/auth/perfil.html`.

### Botón "Volver" con preservación de filtros en todos los submódulos

- Todas las páginas de detalle (viviendas, servicios, compraventa, ocio, foro/detalle, foro/canal) disponen ahora de un botón **Volver** al inicio del contenido.
- Todos los botones "Cancelar" de formularios (viviendas, servicios, compraventa, ocio, foro post, foro canal, tienda Armada) usan `onclick="history.back(); return false;"` con un `href` de fallback.
- El mecanismo `history.back()` devuelve al usuario exactamente al punto donde estaba, preservando filtros de búsqueda, paginación y cualquier parámetro de URL activo.
- Archivos modificados: `templates/viviendas/detalle.html`, `templates/servicios/detalle.html`, `templates/compraventa/detalle.html`, `templates/ocio/detalle.html`, `templates/foro/detalle.html`, `templates/foro/canal.html`, `templates/viviendas/formulario.html`, `templates/servicios/formulario.html`, `templates/compraventa/formulario.html`, `templates/ocio/formulario.html`, `templates/foro/formulario.html`, `templates/foro/nuevo_canal.html`, `templates/compraventa/armada.html`.

### Precio obligatorio en viviendas y compraventa

- El campo precio en el formulario de viviendas pasa a ser `required` (antes era opcional) y se añade asterisco a la etiqueta.
- Validación en servidor en `routes/viviendas.py` (`nuevo` y `editar`) y `routes/compraventa.py` (`nuevo` y `editar`) para rechazar envíos sin precio aunque se manipule el HTML.
- Archivos modificados: `templates/viviendas/formulario.html`, `routes/viviendas.py`, `routes/compraventa.py`.

### Favicon actualizado con logohead.png

- Se sustituye el favicon por `static/img/logohead.png` (logo circular de FAMA con fondo azul integrado).
- Se añaden tres declaraciones `<link rel="icon">` con tamaños 192×192 y 32×32, más `<link rel="apple-touch-icon" sizes="180x180">` para mejor calidad en distintos contextos (navegador, favoritos, móvil).
- Se elimina el `favicon.svg` como fuente primaria (ya no es necesario al tener el fondo azul en el propio PNG).
- Archivo modificado: `templates/base.html`.
