/**
 * app.js — Página del panel (dashboard.html).
 *
 * Se ocupa de tres cosas:
 *   1. exigir sesión antes de mostrar nada (guardián de acceso);
 *   2. arrancar los módulos de negocio con el usuario autenticado;
 *   3. navegar entre las cuatro vistas del panel.
 *
 * El backend no tiene sesiones ni tokens: cada endpoint identifica al
 * propietario de los datos con el parámetro id_usuario, y todas las vistas
 * trabajan exclusivamente con el usuario que abrió la sesión en index.html.
 */
(function (App) {
    "use strict";

    var Sesion = App.Sesion;

    /** Usuario de la sesión activa; null mientras el guardián no lo fija. */
    var idUsuario = null;

    /** Vista visible en este momento. */
    var vistaActiva = "panel";

    /** Cargador de datos asociado a cada vista. */
    var CARGADORES = {
        panel: function () { return App.Dashboard.cargar(idUsuario); },
        movimientos: function () { return App.Movimientos.cargar(idUsuario); },
        categorias: function () { return App.Categorias.sincronizar(idUsuario); },
        analisis: function () { return App.Analytics.cargar(idUsuario); }
    };

    var nodos = {};

    function capturarNodos() {
        nodos = {
            cabecera: document.getElementById("cabecera-aplicacion"),
            contenido: document.getElementById("contenido"),
            pie: document.getElementById("pie-aplicacion"),
            etiquetaUsuario: document.getElementById("sesion-usuario"),
            botonCerrarSesion: document.getElementById("boton-cerrar-sesion"),
            enlaces: Array.prototype.slice.call(document.querySelectorAll(".navegacion__enlace")),
            vistas: Array.prototype.slice.call(document.querySelectorAll(".vista"))
        };
    }

    /**
     * Usuario sobre el que operan todos los módulos.
     * @throws {Error} si se invoca sin sesión iniciada.
     */
    function usuarioActivo() {
        if (idUsuario === null) {
            throw new Error("No hay ninguna sesión activa.");
        }
        return idUsuario;
    }

    /* ======================================================================
       NAVEGACIÓN
       ====================================================================== */

    /** Muestra una vista, actualiza la navegación y carga sus datos. */
    function cambiarVista(nombre) {
        vistaActiva = nombre;

        nodos.vistas.forEach(function (vista) {
            vista.hidden = vista.id !== "vista-" + nombre;
        });

        nodos.enlaces.forEach(function (enlace) {
            if (enlace.dataset.vista === nombre) {
                enlace.setAttribute("aria-current", "page");
            } else {
                enlace.removeAttribute("aria-current");
            }
        });

        return CARGADORES[nombre]();
    }

    /**
     * Refresco tras crear, editar o eliminar un movimiento: la vista visible
     * vuelve a pedir sus datos al backend, que es la fuente de verdad.
     */
    function refrescarDatosDependientes() {
        return CARGADORES[vistaActiva]();
    }

    /* ======================================================================
       GUARDIÁN DE ACCESO
       ====================================================================== */

    /** Revela la aplicación una vez confirmada la sesión. */
    function mostrarAplicacion() {
        nodos.cabecera.hidden = false;
        nodos.contenido.hidden = false;
        nodos.pie.hidden = false;
        nodos.etiquetaUsuario.textContent = "usuario #" + idUsuario;
    }

    /** Cierra la sesión y devuelve a la página de acceso. */
    function cerrarSesion() {
        Sesion.borrar();
        idUsuario = null;
        Sesion.irAlAcceso();
    }

    /**
     * Comprueba que hay sesión y que el usuario sigue existiendo en la base de
     * datos. Sin sesión válida no se muestra el panel: se vuelve al acceso.
     * La sesión se borra antes de redirigir, de modo que index.html no pueda
     * devolvernos aquí y provocar un rebote.
     *
     * @returns {Promise<boolean>} true si el acceso es válido.
     */
    async function exigirSesion() {
        var guardado = Sesion.obtener();
        if (guardado === null) {
            Sesion.irAlAcceso();
            return false;
        }
        try {
            await Sesion.verificarUsuario(guardado);
        } catch (error) {
            Sesion.borrar();
            Sesion.irAlAcceso();
            return false;
        }
        idUsuario = guardado;
        return true;
    }

    /* ======================================================================
       ARRANQUE
       ====================================================================== */

    function registrarEventos() {
        nodos.botonCerrarSesion.addEventListener("click", cerrarSesion);
        nodos.enlaces.forEach(function (enlace) {
            enlace.addEventListener("click", function () {
                cambiarVista(enlace.dataset.vista);
            });
        });
    }

    async function iniciar() {
        capturarNodos();

        if (!(await exigirSesion())) {
            return;
        }

        registrarEventos();
        App.Categorias.inicializar();
        App.Resumen.inicializar();
        App.Movimientos.inicializar();
        App.Analytics.inicializar();
        App.Dashboard.inicializar();

        mostrarAplicacion();
        await App.Categorias.sincronizar(idUsuario);
        await cambiarVista("panel");
    }

    App.usuarioActivo = usuarioActivo;
    App.refrescarDatosDependientes = refrescarDatosDependientes;
    App.cambiarVista = cambiarVista;

    document.addEventListener("DOMContentLoaded", iniciar);
})(window.App);
