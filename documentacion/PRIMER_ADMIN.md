# Creación del primer administrador

Estas instrucciones deben seguirse **una sola vez** al desplegar la aplicación en un nuevo servidor o entorno.

---

## Requisitos previos

- Docker y Docker Compose instalados y en ejecución.
- Fichero `.env` configurado (copia de `.env.example` con los valores reales).

---

## Pasos

### 1. Levantar los contenedores

```bash
docker compose up -d --build
```

Espera a que ambos contenedores estén en estado `healthy` / `Up`:

```bash
docker compose ps
```

### 2. Ejecutar el script de creación del admin

Desde la raíz del proyecto:

```bash
docker compose exec web python scripts/crear_admin.py
```

El script es **idempotente**: si el admin ya existe, no hace ningún cambio. Es seguro ejecutarlo varias veces.

Credenciales creadas:

| Campo       | Valor                |
|-------------|----------------------|
| Nombre      | Administrador FAMA   |
| Email       | admin@appfama.es     |
| Contraseña  | Admin1234            |

> **Importante:** cambia la contraseña en el primer inicio de sesión.

### 3. Iniciar sesión

Accede a la aplicación en `http://<ip-del-servidor>:8000` e inicia sesión con:

- **Nombre de usuario:** `Administrador FAMA`
- **Contraseña:** `Admin1234`

### 4. Crear el administrador real

Desde el panel de administración, registra o valida al usuario que actuará como administrador definitivo y asígnale el rol `admin`.

Al hacerlo, **la cuenta `Administrador FAMA` se elimina automáticamente** y quedas desconectado. A partir de ese momento el nuevo administrador es el único con acceso de administración.

---

## Notas

- La cuenta bootstrap (`Administrador FAMA`) desaparece en cuanto se asigna el rol `admin` a otro usuario. Es un mecanismo de seguridad para que no queden cuentas de bootstrap activas en producción.
- Si necesitas volver a crear el admin bootstrap (por ejemplo, tras un reset de la base de datos), ejecuta de nuevo el script del paso 2.
- Los datos de la aplicación se almacenan en el volumen Docker `mongo_data`. Para migrar datos entre servidores usa `mongodump` / `mongorestore`.
