/**
 * sesion.js — Sesión autenticada compartida por las dos páginas del frontend.
 *
 * index.html (acceso) la crea con el token que devuelve el login;
 * dashboard.html (panel) la exige. Es el único módulo que sabe dónde se guarda
 * la sesión y cómo se navega entre páginas.
 *
 * DÓNDE SE GUARDA EL TOKEN, Y POR QUÉ
 * -----------------------------------
 * El token se guarda en `sessionStorage`. La alternativa a prueba de XSS sería
 * una cookie `httpOnly`, que el JavaScript no puede leer; se ha descartado
 * porque el frontend y la API son dos servicios en orígenes distintos, y una
 * cookie entre orígenes exigiría `SameSite=None; Secure` más protección CSRF
 * propia. Es un cambio de arquitectura que excede esta fase.
 *
 * A cambio se aplican las mitigaciones que sí caben aquí:
 *
 *   - `sessionStorage` y no `localStorage`: el token muere al cerrar la
 *     pestaña, en lugar de quedarse en el disco indefinidamente;
 *   - el token nunca se escribe en consola ni se muestra en la interfaz;
 *   - el token nunca viaja en la URL, solo en la cabecera `Authorization`;
 *   - todo el renderizado del proyecto usa `textContent`, nunca `innerHTML`,
 *     que es lo que de verdad cierra la puerta al XSS que podría leerlo;
 *   - los tokens caducan (ACCESS_TOKEN_EXPIRE_MINUTES en el backend), así que
 *     uno robado tiene una ventana de uso limitada.
 *
 * Queda documentado como riesgo residual conocido en el README.
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var CONFIG = App.CONFIG;

    /** Páginas del frontend, en un único sitio. */
    var PAGINA_ACCESO = "index.html";
    var PAGINA_PANEL = "dashboard.html";

    /**
     * Lee la sesión guardada: { token, usuario } o null.
     *
     * Cualquier contenido corrupto se trata como ausencia de sesión.
     */
    function obtener() {
        try {
            var crudo = window.sessionStorage.getItem(CONFIG.CLAVE_SESION);
            if (!crudo) {
                return null;
            }
            var datos = JSON.parse(crudo);
            if (!datos || typeof datos.token !== "string" || !datos.token) {
                return null;
            }
            if (!datos.usuario || !Number.isInteger(datos.usuario.id_usuario)) {
                return null;
            }
            return datos;
        } catch (error) {
            return null;
        }
    }

    /** Token de acceso de la sesión activa, o null. */
    function token() {
        var sesion = obtener();
        return sesion ? sesion.token : null;
    }

    /** Usuario autenticado (id, nombre, correo), o null. */
    function usuario() {
        var sesion = obtener();
        return sesion ? sesion.usuario : null;
    }

    /** Identificador del usuario autenticado, o null. */
    function idUsuario() {
        var actual = usuario();
        return actual ? actual.id_usuario : null;
    }

    /**
     * Guarda la sesión devuelta por POST /api/auth/login.
     *
     * Del usuario solo se conservan los datos públicos que la interfaz necesita
     * mostrar. La contraseña no se guarda en ningún momento.
     */
    function guardar(respuestaLogin) {
        var datos = {
            token: respuestaLogin.access_token,
            usuario: {
                id_usuario: respuestaLogin.usuario.id_usuario,
                nombre: respuestaLogin.usuario.nombre,
                correo: respuestaLogin.usuario.correo
            }
        };
        try {
            window.sessionStorage.setItem(CONFIG.CLAVE_SESION, JSON.stringify(datos));
        } catch (error) {
            /* Modo privado sin almacenamiento: la navegación seguirá funcionando,
               pero el panel volverá a pedir acceso. */
        }
    }

    /** Borra la sesión del navegador (cierre de sesión). */
    function borrar() {
        try {
            window.sessionStorage.removeItem(CONFIG.CLAVE_SESION);
        } catch (error) {
            /* Sin almacenamiento no hay nada que borrar. */
        }
    }

    /**
     * Comprueba contra el backend que el token sigue siendo válido.
     *
     * Devuelve el usuario autenticado. Lanza ErrorApi con estado 401 si el
     * token expiró, fue manipulado o el usuario ya no existe.
     */
    async function verificar() {
        return Api.auth.yo();
    }

    function irAlPanel() {
        window.location.href = PAGINA_PANEL;
    }

    function irAlAcceso() {
        window.location.href = PAGINA_ACCESO;
    }

    /**
     * Cierra la sesión y vuelve a la pantalla de acceso.
     *
     * @param {string} [motivo] Texto a mostrar en el acceso, por ejemplo cuando
     *                          la sesión ha caducado.
     */
    function cerrar(motivo) {
        borrar();
        if (motivo) {
            try {
                window.sessionStorage.setItem("finanzas.motivo_salida", motivo);
            } catch (error) {
                /* Sin almacenamiento simplemente no se muestra el aviso. */
            }
        }
        irAlAcceso();
    }

    /** Recupera y consume el motivo del último cierre de sesión, si lo hubo. */
    function motivoDeSalida() {
        try {
            var motivo = window.sessionStorage.getItem("finanzas.motivo_salida");
            window.sessionStorage.removeItem("finanzas.motivo_salida");
            return motivo || null;
        } catch (error) {
            return null;
        }
    }

    App.Sesion = {
        PAGINA_ACCESO: PAGINA_ACCESO,
        PAGINA_PANEL: PAGINA_PANEL,
        obtener: obtener,
        token: token,
        usuario: usuario,
        idUsuario: idUsuario,
        guardar: guardar,
        borrar: borrar,
        verificar: verificar,
        cerrar: cerrar,
        motivoDeSalida: motivoDeSalida,
        irAlPanel: irAlPanel,
        irAlAcceso: irAlAcceso
    };
})(window.App);
