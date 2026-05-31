/**
 * scripts.js - Scripts personalizados de la aplicacion FAMA.
 * Funciones de utilidad globales usadas en todas las paginas.
 */

/**
 * Muestra un dialogo de confirmacion antes de eliminar un elemento.
 * Se llama desde los atributos onsubmit de los formularios de borrado.
 */
function confirmarEliminacion() {
    return confirm('Estas seguro de que quieres eliminar este elemento? Esta accion no se puede deshacer.');
}

/**
 * Cierra automaticamente las alertas flash despues de 5 segundos.
 */
document.addEventListener('DOMContentLoaded', function () {
    const alertas = document.querySelectorAll('.alert.alert-dismissible');
    alertas.forEach(function (alerta) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alerta);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
});
