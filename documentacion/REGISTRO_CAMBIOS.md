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
