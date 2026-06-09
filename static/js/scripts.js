/**
 * scripts.js - Scripts personalizados de la aplicación FAMA.
 * Funciones de utilidad globales usadas en todas las páginas.
 */

/**
 * Muestra un diálogo de confirmación antes de eliminar un elemento.
 * Se llama desde los atributos onsubmit de los formularios de borrado.
 */
function confirmarEliminacion() {
    return confirm('¿Estás seguro de que quieres eliminar este elemento? Esta acción no se puede deshacer.');
}

/**
 * Cierra automáticamente las alertas flash después de 5 segundos.
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

/**
 * Indicador de fortaleza de contraseña con popover Bootstrap.
 * El <input> lleva data-pwd-indicator="<id-del-icono>".
 * El icono (<span id="..."> dentro del input-group) muestra:
 *   - ! amarillo  -> requisitos sin cumplir (popover visible al hacer hover)
 *   - ✓ verde     -> todos los requisitos cumplidos
 */
(function () {
    var REGLAS = [
        { key: 'len',     re: /.{8,}/,        text: '8 caracteres mínimo' },
        { key: 'upper',   re: /[A-Z]/,         text: '1 mayúscula (A-Z)' },
        { key: 'lower',   re: /[a-z]/,         text: '1 minúscula (a-z)' },
        { key: 'num',     re: /[0-9]/,         text: '1 número (0-9)' },
        { key: 'special', re: /[^A-Za-z0-9]/, text: '1 carácter especial (!@#...)' },
    ];

    function buildHtml(val) {
        return '<p class="mb-0 small" style="line-height:1.7">' +
            REGLAS.map(function (r) {
                var ok = r.re.test(val);
                return '<span class="' + (ok ? 'text-success fw-semibold' : 'text-secondary') + '">' +
                    r.text + '</span>';
            }).join('<span class="text-muted mx-1">·</span>') +
            '</p>';
    }

    function setup(input) {
        var iconEl = document.getElementById(input.dataset.pwdIndicator);
        if (!iconEl) return;

        var pop = new bootstrap.Popover(iconEl, {
            html:      true,
            trigger:   'hover focus',
            placement: 'bottom',
            content:   buildHtml(''),
        });

        input.addEventListener('input', function () {
            var val = input.value;
            var allOk = REGLAS.every(function (r) { return r.re.test(val); });

            pop.setContent({ '.popover-body': buildHtml(val) });

            var i = iconEl.querySelector('i');
            if (i) {
                i.className = allOk
                    ? 'bi bi-check-circle-fill text-success'
                    : 'bi bi-exclamation-circle text-warning';
            }
        });
    }

    function init() {
        document.querySelectorAll('[data-pwd-indicator]').forEach(function (el) {
            if (!el.dataset.pwdReady) {
                el.dataset.pwdReady = '1';
                setup(el);
            }
        });
    }

    document.addEventListener('DOMContentLoaded', init);
    document.addEventListener('shown.bs.modal', init);
}());

/**
 * Toggle lista / cuadrícula en los listados de anuncios.
 * Guarda la preferencia en localStorage con la clave 'fama_vista_<key>'.
 * Por defecto muestra la vista lista.
 */
function initVistaToggle(key) {
    var grid    = document.getElementById('vista-grid');
    var lista   = document.getElementById('vista-lista');
    var btnGrid = document.getElementById('btn-vista-grid');
    var btnList = document.getElementById('btn-vista-lista');
    if (!grid || !lista) return;

    function setVista(v) {
        var esGrid = (v === 'grid');
        grid.classList.toggle('d-none', !esGrid);
        lista.classList.toggle('d-none',  esGrid);
        if (btnGrid) btnGrid.classList.toggle('active', esGrid);
        if (btnList) btnList.classList.toggle('active', !esGrid);
        try { localStorage.setItem('fama_vista_' + key, v); } catch (e) {}
    }

    var guardada = 'lista';
    try { guardada = localStorage.getItem('fama_vista_' + key) || 'lista'; } catch (e) {}
    setVista(guardada);

    if (btnGrid) btnGrid.addEventListener('click', function () { setVista('grid'); });
    if (btnList) btnList.addEventListener('click', function () { setVista('lista'); });
}

/**
 * Lightbox: abre las fotos de un anuncio ampliadas con navegación prev/next.
 * Las imágenes deben tener la clase .fama-lightbox y los atributos:
 *   data-fotos  -> JSON array de URLs absolutas de todas las fotos del anuncio
 *   data-index  -> índice (0-based) de la foto actual dentro del array
 */
(function () {
    var fotos = [];
    var idx   = 0;

    function mostrar() {
        document.getElementById('lbImg').src = fotos[idx];
        var total = fotos.length;
        document.getElementById('lbCounter').textContent =
            total > 1 ? (idx + 1) + ' / ' + total : '';
        document.getElementById('lbPrev').style.display = total > 1 ? '' : 'none';
        document.getElementById('lbNext').style.display = total > 1 ? '' : 'none';
    }

    function abrir(listaFotos, indice) {
        fotos = listaFotos;
        idx   = indice;
        mostrar();
        bootstrap.Modal.getOrCreateInstance(
            document.getElementById('famaLightbox')
        ).show();
    }

    document.addEventListener('DOMContentLoaded', function () {
        // Click sobre cualquier imagen lightbox
        document.addEventListener('click', function (e) {
            var img = e.target.closest('.fama-lightbox');
            if (!img) return;
            e.preventDefault();
            var lista  = JSON.parse(img.dataset.fotos  || '[]');
            var indice = parseInt(img.dataset.index   || '0', 10);
            if (lista.length === 0) return;
            abrir(lista, indice);
        });

        // Botones de navegación
        var btnPrev = document.getElementById('lbPrev');
        var btnNext = document.getElementById('lbNext');
        if (btnPrev) btnPrev.addEventListener('click', function () {
            idx = (idx - 1 + fotos.length) % fotos.length;
            mostrar();
        });
        if (btnNext) btnNext.addEventListener('click', function () {
            idx = (idx + 1) % fotos.length;
            mostrar();
        });

        // Navegación con teclado (flechas)
        document.addEventListener('keydown', function (e) {
            var modal = document.getElementById('famaLightbox');
            if (!modal || !modal.classList.contains('show')) return;
            if (e.key === 'ArrowLeft')  { idx = (idx - 1 + fotos.length) % fotos.length; mostrar(); }
            if (e.key === 'ArrowRight') { idx = (idx + 1) % fotos.length; mostrar(); }
        });
    });
}());
