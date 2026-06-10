# CONSEJOS para perfeccionar FAMA

## 1. Cambios recomendados

- Cambiar `SECRET_KEY` por una clave fuerte en el entorno de producción. Nada de valores por defecto en el código.
- Desactivar `FLASK_DEBUG` en producción y usar `debug=False` siempre en el servidor.
- No exponer Flask/Gunicorn directamente al exterior: el host debe usar Nginx solo como proxy inverso.
- Configurar Nginx para que sirva los archivos estáticos (`/static` y `/uploads`) directamente y reduzca la carga sobre Flask.
- Añadir un `healthcheck` al servicio `web` en `docker-compose.yml` si se quiere orquestar con mayor control.
- Añadir un usuario y contraseña de MongoDB en lugar de usar la conexión directa sin autenticación.
- Revisar y limitar `MAX_CONTENT_LENGTH` y los tipos de archivo permitidos para las subidas.
- Forzar HTTPS en el proxy y marcar las cookies de sesión como `Secure` y `SameSite=Lax/Strict`.
- Usar un volumen separado para `uploads/` si se quiere persistencia independiente del contenedor de aplicación.

## 2. Cambios para hacer la aplicación más segura

- Hacer que `SECRET_KEY`, `MONGO_URI`, `MONGO_DB_NAME` y otras variables sensibles se configuren solo mediante variables de entorno en el servidor, no en el repositorio.
- No usar `python-dotenv` en producción; solo en desarrollo local.
- Añadir autenticación de MongoDB y roles de usuario en la base de datos.
- Validar la extensión y el contenido de los archivos subidos para evitar cargas maliciosas.
- Revisar las rutas del admin y los permisos: la gestión de roles y la edición de usuarios deben ser exclusivas para `admin` o `gestor`.
- Limitar el acceso a `admin`/`gestor` por IP si se despliega en un entorno seguro.
- Aplicar un límite de tasa (rate limiting) a los endpoints de login y recuperación de cuenta si se añade una capa extra de seguridad.
- Revisar la sesión de Flask para que no expiren sesiones excesivamente largas y se invaliden en logout.
- Añadir registros de auditoría en eventos críticos como cambios de contraseña, reset de cuenta, creación de usuarios y validaciones.

## 3. Archivos y carpetas a eliminar para producción

### Opciones seguras para limpiar el entorno

- `documentacion/`: mantener solo los documentos necesarios para el equipo. Si quieres un entorno mínimo, puedes conservar solo los manuales finales y borrar notas de diseño antiguas.
- `scripts/`: eliminar o mover fuera de la imagen de producción. Estas utilidades son útiles en desarrollo, pero no deben formar parte del contenedor de runtime.
- `__pycache__/`: no incluirlo en el despliegue ni en el repositorio.
- `.git/`: no debe estar presente en el entorno de producción.
- `.env.example`: no es necesario en el contenedor de producción.

### Archivos específicos que puedes dejar fuera de la imagen de producción

- Archivos de prueba y semillas de datos en `scripts/seed_data/`.
- Cualquier archivo de documentación temporal o notas privadas que no sean necesarias para operar el servicio.
- Copias locales, archivos de configuración de editor o IDE si estuvieran presentes.

## 4. Sugerencias para el Docker en producción

- Construir la imagen con `docker compose build --no-cache` solo cuando se actualicen dependencias.
- Usar una imagen base `python:3.14-slim` está bien, pero revisar si puede optimizarse aún más con multistage build si se añaden compilaciones.
- No montar el código fuente con volumen en producción; esto es solo para desarrollo.
- Asegurarse de que el servicio `mongo` use un volumen persistente y no se borre con `docker compose down -v`.

## 5. Recomendaciones de mantenimiento

- Documentar claramente el flujo de despliegue y el proxy inverso en `CONSEJOS.md` y `MANUAL_INSTALACION.md`.
- Usar un archivo `README` si quieres exponer el proceso de deployment rápido.
- Revisar periódicamente las versiones de dependencias para eliminar vulnerabilidades.
- Mantener separado el entorno de desarrollo del de producción.
