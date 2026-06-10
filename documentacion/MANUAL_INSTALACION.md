# Manual de Instalación - FAMA
## Arquitectura del Proyecto

FAMA está diseñada como una aplicación web modular basada en Flask, con una capa de datos en MongoDB y un servidor WSGI (Gunicorn) para producción.

Componentes principales:
- `app.py`: punto de entrada de la aplicación. Crea la app Flask mediante la función `create_app()` y exporta la variable `app`.
- `routes/`: blueprints que agrupan rutas por módulo (`auth`, `viviendas`, `servicios`, `compraventa`, `foro`, `ocio`, `admin`, `main`, `novedades`).
- `models/`: lógica de datos y operaciones sobre MongoDB, especialmente el modelo de usuario en `models/usuario.py`.
- `utils/`: helpers de configuración, conexión a la base de datos, validadores, decoradores, logs y gestión de subidas.
- `static/` y `templates/`: recursos estáticos y plantillas HTML Jinja2.

Flujo de ejecución:
1. Gunicorn arranca `app:app` y sirve la app Flask en `0.0.0.0:5000`.
2. La app conecta con MongoDB usando la URI definida en `MONGO_URI`.
3. El servidor Nginx del host actúa como proxy inverso, aceptando tráfico en `80/443` y reenviándolo internamente a `5000`.

## Contenedores y despliegue

El proyecto se despliega con `docker-compose` y actualmente define dos servicios:

- `web`:
  - Construye la imagen desde `Dockerfile`.
  - Expone `5000:5000`.
  - Instala dependencias de `requirements.txt` y arranca con Gunicorn.
  - Monta el código fuente en el contenedor con `.:/app`.
- `mongo`:
  - Usa `mongo:4.4`.
  - Expone `27018:27017` en el host.
  - Usa volumen persistente `mongo_data:/data/db`.
  - Tiene un `healthcheck` que comprueba la disponibilidad del servidor Mongo.

> Nota: el proxy inverso Nginx se configura fuera de Docker en el servidor, usando el puerto `80`/`443` hacia `192.168.7.80:5000`.

### Volúmenes

- `mongo_data`: volumen persistente para los datos de MongoDB.
- El código de la aplicación se monta por volumen en `web` para permitir cambios rápidos durante el desarrollo.

## Dependencias del proyecto

Dependencias principales declaradas en `requirements.txt`:
- `Flask==3.0.3`: framework web.
- `pymongo==4.4.0`: driver para MongoDB.
- `Werkzeug==3.0.3`: utilidades de seguridad.
- `python-dotenv==1.0.1`: carga variables de entorno desde `.env` opcional.
- `reportlab==4.2.2`: generación de PDFs.
- `python-docx==1.1.2`: manipulación de documentos Word.
- `gunicorn==23.0.0`: servidor WSGI para producción.

Dependencias del sistema:
- `python:3.14-slim` como imagen base de Docker.
- `mongo:4.4` como contenedor de la base de datos.

## Configuración y entorno

Variables de entorno manejadas en `utils/config.py`:
- `SECRET_KEY`: clave para firmar cookies de sesión y proteger datos de sesión.
- `FLASK_HOST`: host en el que escucha Flask/Gunicorn.
- `FLASK_PORT`: puerto interno en el que responde la app.
- `FLASK_DEBUG`: activa el modo debug de Flask solo en desarrollo.
- `MONGO_URI`: conexión a MongoDB.
- `MONGO_DB_NAME`: nombre de la base de datos.
- `MAX_CONTENT_LENGTH`: tamaño máximo de subida de archivos (5 MB).

## Algoritmos y lógicas relevantes

### Proxy inverso

El proxy inverso es una capa intermedia entre el cliente y la aplicación.

- En este proyecto, Nginx recibe las peticiones externas en `80`/`443`.
- Nginx realiza el terminación TLS cuando el tráfico llega por HTTPS.
- Luego reenvía internamente las peticiones a Gunicorn en `http://127.0.0.1:5000`.
- El proxy inverso permite:
  - usar certificados SSL/TLS en el host
  - exponer puertos estándar `80` y `443`
  - proteger y aislar el servidor de aplicación
  - manejar cabeceras como `Host`, `X-Real-IP`, `X-Forwarded-For` y `X-Forwarded-Proto`

### Uso de contraseñas

FAMA no almacena contraseñas reversibles. El proyecto emplea hashing seguro con Werkzeug:

- `generate_password_hash(password)`: genera un hash irreversible (PBKDF2 con salt aleatorio).
- `check_password_hash(hash, password)`: compara una contraseña en texto plano con su hash.

Esto significa que:
- las contraseñas no pueden recuperarse desde la base de datos.
- solo se comprueba si la contraseña ingresada coincide con el hash guardado.
- la aplicación no usa cifrado reversible para contraseñas.

#### Flujos de contraseña

- Registro: la contraseña del usuario se hashea antes de guardarla.
- Login: la contraseña ingresada se compara con el hash almacenado usando `check_password_hash`.
- Reset de contraseña por admin/gestor: se asigna un hash de la contraseña temporal `fama1234` y se fuerza el cambio en el próximo acceso.
- Recuperación por pregunta de seguridad: la respuesta de seguridad también se guarda como hash, y no en texto claro.
- Primer acceso: si la cuenta fue creada por el admin, el usuario debe configurar una nueva contraseña y su pregunta/ respuesta de seguridad.

### Validación de contraseñas

El validador de contraseñas en `utils/validators.py` comprueba que la contraseña:
- tenga al menos 8 caracteres
- contenga una letra mayúscula
- contenga una letra minúscula
- contenga al menos un número
- contenga al menos un carácter especial

Esto evita contraseñas débiles y ayuda a proteger la cuenta.

### Seguridad de sesión

- La aplicación usa la sesión de Flask para almacenar información mínima del usuario.
- La cookie de sesión está firmada con `SECRET_KEY`.
- La sesión guarda `user_id`, `nombre`, `rol` y `foto_perfil`.
- El decorador `login_required` protege rutas privadas verificando la sesión activa.

### Operaciones con MongoDB

- `models/usuario.py` implementa la lógica de usuario, autenticación, roles y recuperación.
- Las actualizaciones usan operadores MongoDB `$set` para modificar campos sin sobrescribir todo el documento.
- `utils/db.py` gestiona la conexión compartida a MongoDB.

## Cómo instalar y arrancar

1. Clona el repositorio al servidor.
2. Coloca las variables de entorno necesarias en el entorno del servicio o en un archivo `.env` (si lo deseas).
3. En el directorio del proyecto, ejecuta:

```bash
docker compose up --build
```

4. Asegúrate de que el Nginx del servidor esté configurado para hacer proxy reverso hacia:

```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name tu-dominio.com;

    ssl_certificate /ruta/a/certificado.crt;
    ssl_certificate_key /ruta/a/clave.key;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

5. Abre la aplicación desde el navegador usando el dominio configurado.

## Dependencias de desarrollo y herramientas

- Docker y Docker Compose para construir y ejecutar los contenedores.
- MongoDB para la base de datos.
- Nginx en el servidor para el proxy inverso y TLS.

## Resumen de contenedores

| Servicio | Imagen | Puerto interno | Puerto expuesto | Volumen |
|----------|--------|----------------|-----------------|---------|
| `web`    | construye desde `Dockerfile` | `5000` | `5000` | código fuente montado |
| `mongo`  | `mongo:4.4` | `27017` | `27018` | `mongo_data:/data/db` |

## Buenas prácticas de instalación

- No uses `docker compose down -v` si quieres conservar los datos de Mongo.
- Cambia el `SECRET_KEY` por una clave fuerte en producción.
- Mantén los certificados TLS actualizados en Nginx.
- Usa usuarios de MongoDB seguros si amplías la configuración de la base de datos.

---

**Última actualización**: Junio de 2026
