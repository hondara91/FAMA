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