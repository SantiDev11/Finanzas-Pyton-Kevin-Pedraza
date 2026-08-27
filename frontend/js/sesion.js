/**
 * sesion.js — Sesión compartida por las dos páginas del frontend.
 *
 * index.html (acceso) la escribe; dashboard.html (panel) la exige. Es el único
 * módulo que conoce dónde se guarda la sesión y cómo se navega entre páginas.
 *
 * LIMITACIÓN DEL BACKEND ACTUAL
 * -----------------------------
 * La API expone un único endpoint de usuarios, POST /api/usuarios (registro).
 * No existe ninguna ruta de inicio de sesión ni de verificación de
 * credenciales, así que el frontend NO puede comprobar correo y contraseña:
 * eso exigiría añadir un endpoint al backend, que está aprobado y no se
 * modifica. Lo que sí se valida contra MySQL es que el usuario exista.
 *
 * No se implementa JWT, OAuth ni ningún esquema de tokens.
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var CONFIG = App.CONFIG;

    /** Páginas del frontend, en un único sitio. */
    var PAGINA_ACCESO = "index.html";
    var PAGINA_PANEL = "dashboard.html";

    /**
     * Identificador del usuario con sesión iniciada, o null.
     *
     * Se usa sessionStorage y no localStorage para que la sesión muera al
     * cerrar la pestaña. Solo se guarda el identificador: nunca el correo, la
     * contraseña ni ningún hash.
     */
    function obtener() {
        try {
            var valor = Number(window.sessionStorage.getItem(CONFIG.CLAVE_SESION));
            return Number.isInteger(valor) && valor > 0 ? valor : null;
        } catch (error) {
            return null;
        }
    }

    function guardar(idUsuario) {
        try {
            window.sessionStorage.setItem(CONFIG.CLAVE_SESION, String(idUsuario));
        } catch (error) {
            /* Modo privado sin almacenamiento: la navegación seguirá funcionando,
               pero el panel volverá a pedir acceso. */
        }
    }

    function borrar() {
        try {
            window.sessionStorage.removeItem(CONFIG.CLAVE_SESION);
        } catch (error) {
            /* Sin almacenamiento no hay nada que borrar. */
        }
    }

    /**
     * Comprueba contra la base de datos que el usuario existe.
     *
     * Se reutiliza GET /api/categorias porque valida la existencia del usuario
     * antes de responder: devuelve 200 (aunque la lista esté vacía) si existe y
     * 404 si no. Es el endpoint existente más barato para esta comprobación; en
     * cuanto el backend exponga un login o un GET /api/usuarios/{id}, esta
     * función debería apuntar allí.
     *
     * @throws {Error} ErrorApi si el usuario no existe o la API no responde.
     */
    async function verificarUsuario(idUsuario) {
        await Api.categorias.listar(idUsuario);
    }

    function irAlPanel() {
        window.location.href = PAGINA_PANEL;
    }

    function irAlAcceso() {
        window.location.href = PAGINA_ACCESO;
    }

    App.Sesion = {
        PAGINA_ACCESO: PAGINA_ACCESO,
        PAGINA_PANEL: PAGINA_PANEL,
        obtener: obtener,
        guardar: guardar,
        borrar: borrar,
        verificarUsuario: verificarUsuario,
        irAlPanel: irAlPanel,
        irAlAcceso: irAlAcceso
    };
})(window.App);
