# Creación del primer administrador

Estas instrucciones deben seguirse **una sola vez** al desplegar la aplicación en un nuevo servidor o entorno.

---

## Requisitos previos

- Docker y Docker Compose instalados y en ejecución.
- Variables de entorno configuradas en el servidor. En desarrollo local puedes usar `.env.example` como referencia, pero el proyecto no carga `.env` automáticamente en producción.

---

## Pasos

### 1. Levantar los contenedores

```bash
docker compose up -d --build
```

Espera a que los contenedores estén en estado `healthy` / `Up`:

```bash
docker compose ps
```

### 2. Ejecutar el script de creación del admin

Desde la raíz del proyecto:

```bash
docker compose exec web python scripts/crear_admin.py
```

El script es **idempotente**: si el administrador ya existe, no hace ningún cambio. Es seguro ejecutarlo varias veces.

Credenciales creadas:

| Campo       | Valor                |
|-------------|----------------------|
| Nombre      | admin                |
| Email       | admin@appfama.es     |
| Contraseña  | admin1234            |

> **Importante:** cambia la contraseña en el primer inicio de sesión.

### 3. Iniciar sesión

- En desarrollo local, la aplicación responde en `http://localhost:5000`.
- En producción con Nginx externo, accede mediante el dominio o IP del servidor en `http://192.168.7.80` o `https://192.168.7.80`.

Inicia sesión con:

- **Nombre de usuario:** `admin`
- **Contraseña:** `admin1234`

### 4. Crear el administrador definitivo

Desde el panel de administración, valida o registra al usuario que actuará como administrador definitivo y asígnale el rol `admin`.

En el flujo actual, la cuenta bootstrap `admin` permanece hasta que existe al menos otro administrador.

---

## Contraseña por defecto

Todos los usuarios reciben la contraseña **`fama1234`** en los siguientes casos:

| Situación | Quién la asigna |
|-----------|----------------|
| El admin aprueba una nueva cuenta | Sistema automático al validar |
| El admin o gestor resetea la contraseña de un usuario | Botón "Resetear contraseña" en el panel |

El usuario queda obligado a cambiarla en su primer inicio de sesión.

---

## Notas

- La cuenta bootstrap (`admin`) puede volver a crearse ejecutando de nuevo `docker compose exec web python scripts/crear_admin.py`.
- El servicio `web` se sirve internamente en el puerto `5000`; el proxy inverso Nginx del servidor debe reenviar tráfico hacia ese puerto.
- Los datos de la aplicación se almacenan en el volumen Docker `mongo_data`. Para migrar datos entre servidores usa `mongodump` / `mongorestore`.
