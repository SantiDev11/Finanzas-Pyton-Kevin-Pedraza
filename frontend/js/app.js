/**
 * app.js — Controlador principal del Panel de Control (dashboard.html).
 *
 * Responsabilidades:
 *   1. Exigir sesión válida antes de mostrar la interfaz (guardián de acceso).
 *   2. Inicializar los módulos funcionales con el usuario autenticado.
 *   3. Gestionar la navegación lateral (Sidebar) y migas de pan.
 *   4. Controlar el menú responsive en móviles y tablets.
 */
(function (App) {
    "use strict";

    var Sesion = App.Sesion;

    /** ID del usuario de la sesión activa */
    var idUsuario = null;

    /** Vista actualmente visible */
    var vistaActiva = "panel";

    var TITULOS_VISTA = {
        panel: "Dashboard",
        movimientos: "Movimientos",
        categorias: "Categorías",
        analisis: "Análisis"
    };

    /** Cargador de datos asociado a cada vista */
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
            tituloSeccion: document.getElementById("titulo-seccion-actual"),
            sesionUsuarioSidebar: document.getElementById("sesion-usuario-sidebar"),
            avatarUsuario: document.getElementById("avatar-usuario"),
            botonCerrarSesion: document.getElementById("boton-cerrar-sesion"),

            // Menú lateral y responsive
            barraLateral: document.getElementById("barra-lateral"),
            sidebarBackdrop: document.getElementById("sidebar-backdrop"),
            botonMenuMovil: document.getElementById("boton-menu-movil"),
            botonCerrarSidebar: document.getElementById("boton-cerrar-sidebar"),

            enlaces: Array.prototype.slice.call(document.querySelectorAll(".menu-lateral__enlace")),
            vistas: Array.prototype.slice.call(document.querySelectorAll(".vista"))
        };
    }

    /** Devuelve el ID de usuario activo */
    function usuarioActivo() {
        if (idUsuario === null) {
            throw new Error("No hay ninguna sesión activa.");
        }
        return idUsuario;
    }

    /* ======================================================================
       CONTROL DEL SIDEBAR RESPONSIVE
       ====================================================================== */

    function abrirSidebar() {
        if (nodos.barraLateral) {
            nodos.barraLateral.classList.add("abierta");
        }
        if (nodos.sidebarBackdrop) {
            nodos.sidebarBackdrop.classList.add("activo");
        }
    }

    function cerrarSidebar() {
        if (nodos.barraLateral) {
            nodos.barraLateral.classList.remove("abierta");
        }
        if (nodos.sidebarBackdrop) {
            nodos.sidebarBackdrop.classList.remove("activo");
        }
    }

    /* ======================================================================
       NAVEGACIÓN ENTRE VISTAS
       ====================================================================== */

    /** Muestra una vista, actualiza la navegación y carga sus datos */
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

        if (nodos.tituloSeccion) {
            nodos.tituloSeccion.textContent = TITULOS_VISTA[nombre] || nombre;
        }

        cerrarSidebar();
        return CARGADORES[nombre]();
    }

    /** Refresca los datos de la vista activa tras una mutación */
    function refrescarDatosDependientes() {
        return CARGADORES[vistaActiva]();
    }

    /* ======================================================================
       GUARDIÁN DE ACCESO
       ====================================================================== */

    function mostrarAplicacion() {
        if (nodos.cabecera) {
            nodos.cabecera.hidden = false;
        }
        if (nodos.contenido) {
            nodos.contenido.hidden = false;
        }
        if (nodos.pie) {
            nodos.pie.hidden = false;
        }
        if (nodos.sesionUsuarioSidebar) {
            nodos.sesionUsuarioSidebar.textContent = "Usuario #" + idUsuario;
        }
        if (nodos.avatarUsuario) {
            nodos.avatarUsuario.textContent = "U" + idUsuario;
        }
    }

    function cerrarSesion() {
        Sesion.borrar();
        idUsuario = null;
        Sesion.irAlAcceso();
    }

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
       INICIALIZACIÓN
       ====================================================================== */

    function registrarEventos() {
        if (nodos.botonCerrarSesion) {
            nodos.botonCerrarSesion.addEventListener("click", cerrarSesion);
        }

        if (nodos.botonMenuMovil) {
            nodos.botonMenuMovil.addEventListener("click", abrirSidebar);
        }

        if (nodos.botonCerrarSidebar) {
            nodos.botonCerrarSidebar.addEventListener("click", cerrarSidebar);
        }

        if (nodos.sidebarBackdrop) {
            nodos.sidebarBackdrop.addEventListener("click", cerrarSidebar);
        }

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
