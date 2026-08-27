/**
 * app.js — Controlador principal del Panel de Control (dashboard.html).
 *
 * Responsabilidades:
 *   1. Exigir un token válido antes de mostrar la interfaz (guardián de acceso).
 *   2. Inicializar los módulos funcionales con el usuario autenticado.
 *   3. Gestionar la navegación lateral (Sidebar) y migas de pan.
 *   4. Controlar el menú responsive en móviles y tablets.
 */
(function (App) {
    "use strict";

    var Sesion = App.Sesion;

    /** ID del usuario autenticado, tomado del token validado por el backend. */
    var idUsuario = null;

    /** Datos públicos del usuario autenticado (id, nombre, correo). */
    var usuarioAutenticado = null;

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
        panel: function () { return App.Dashboard.cargar(); },
        movimientos: function () { return App.Movimientos.cargar(); },
        categorias: function () { return App.Categorias.sincronizar(); },
        analisis: function () { return App.Analytics.cargar(); }
    };

    var nodos = {};

    function capturarNodos() {
        nodos = {
            cabecera: document.getElementById("cabecera-aplicacion"),
            contenido: document.getElementById("contenido"),
            pie: document.getElementById("pie-aplicacion"),
            tituloSeccion: document.getElementById("titulo-seccion-actual"),
            sesionUsuarioSidebar: document.getElementById("sesion-usuario-sidebar"),
            correoUsuarioSidebar: document.getElementById("correo-usuario-sidebar"),
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

    /**
     * Devuelve el ID del usuario autenticado.
     *
     * Se conserva para los módulos que necesitan saber de quién son los datos
     * que muestran. Ya NO se envía a la API: el backend deduce el usuario del
     * token, así que este valor es informativo, no una credencial.
     */
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
        // Se muestra el nombre real del usuario autenticado, no un número.
        // El token nunca se escribe en la interfaz ni en la consola.
        if (nodos.sesionUsuarioSidebar && usuarioAutenticado) {
            nodos.sesionUsuarioSidebar.textContent = usuarioAutenticado.nombre;
        }
        if (nodos.correoUsuarioSidebar && usuarioAutenticado) {
            nodos.correoUsuarioSidebar.textContent = usuarioAutenticado.correo;
        }
        if (nodos.avatarUsuario && usuarioAutenticado) {
            nodos.avatarUsuario.textContent = iniciales(usuarioAutenticado.nombre);
        }
    }

    /**
     * Cierra la sesión: descarta el token, oculta la interfaz y vuelve al acceso.
     *
     * Ocultar el panel antes de navegar evita que quede a la vista, aunque sea
     * un instante, como si la sesión siguiera abierta.
     */
    function cerrarSesion(motivo) {
        ocultarAplicacion();
        idUsuario = null;
        usuarioAutenticado = null;
        Sesion.cerrar(motivo);
    }

    function ocultarAplicacion() {
        if (nodos.cabecera) {
            nodos.cabecera.hidden = true;
        }
        if (nodos.contenido) {
            nodos.contenido.hidden = true;
        }
        if (nodos.pie) {
            nodos.pie.hidden = true;
        }
    }

    /** Iniciales para el avatar, a partir del nombre del usuario. */
    function iniciales(nombre) {
        var partes = String(nombre || "").trim().split(/\s+/).filter(Boolean);
        if (!partes.length) {
            return "U";
        }
        if (partes.length === 1) {
            return partes[0].slice(0, 2).toUpperCase();
        }
        return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
    }

    /**
     * Guardián de acceso: sin token válido no se muestra nada del panel.
     *
     * No basta con que haya algo guardado en el navegador: el token se valida
     * contra el backend (GET /api/auth/me), que comprueba firma, expiración y
     * existencia del usuario. La identidad que se usa después es la que
     * devuelve el servidor, no la que estuviera guardada localmente.
     */
    async function exigirSesion() {
        if (Sesion.obtener() === null) {
            Sesion.irAlAcceso();
            return false;
        }

        try {
            usuarioAutenticado = await Sesion.verificar();
        } catch (error) {
            var motivo = (error && error.estado === 401)
                ? "Tu sesión expiró. Vuelve a iniciar sesión."
                : "No fue posible verificar tu sesión. Vuelve a iniciar sesión.";
            Sesion.cerrar(motivo);
            return false;
        }

        idUsuario = usuarioAutenticado.id_usuario;
        return true;
    }

    /* ======================================================================
       INICIALIZACIÓN
       ====================================================================== */

    function registrarEventos() {
        if (nodos.botonCerrarSesion) {
            nodos.botonCerrarSesion.addEventListener("click", function () {
                cerrarSesion();
            });
        }

        // Si cualquier petición recibe un 401, la sesión dejó de valer: se
        // cierra de inmediato en lugar de dejar el panel abierto mostrando
        // errores sueltos.
        document.addEventListener("sesion:expirada", function () {
            if (idUsuario !== null) {
                cerrarSesion("Tu sesión expiró. Vuelve a iniciar sesión.");
            }
        });

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
        await App.Categorias.sincronizar();
        await cambiarVista("panel");
    }

    App.usuarioActivo = usuarioActivo;
    App.refrescarDatosDependientes = refrescarDatosDependientes;
    App.cambiarVista = cambiarVista;

    document.addEventListener("DOMContentLoaded", iniciar);
})(window.App);
