## Cambios manuales directos

- 03/06/2026: Se añadió validación para que los campos de teléfono en los formularios solo acepten 9 dígitos numéricos.
- Ajustes aplicados en:
  - `templates/viviendas/formulario.html`
  - `templates/servicios/formulario.html`
  - `routes/viviendas.py`
  - `routes/servicios.py`

- 03/06/2026: Se permitió la existencia de múltiples administradores.
- Se eliminó la eliminación automática del administrador actual al asignar un nuevo rol `admin`.
- Ahora solo se desactiva el administrador por defecto generado por `scripts/crear_admin.py` (`admin@appfama.es`) cuando se define un nuevo administrador.

- 03/06/2026: Se añadió cierre automático de sesión para cualquier usuario que haya sido desactivado.
- Archivo modificado:
  - `app.py`
  - `routes/admin.py`
