/**
 * config.js — Configuración única del frontend.
 *
 * La URL de la API se declara en un solo sitio: la etiqueta
 * <meta name="api-base-url"> de index.html. Para apuntar a otro entorno
 * (por ejemplo la URL pública de Render) basta con cambiar ese atributo;
 * ningún otro archivo del proyecto contiene URLs de la API.
 *
 * Aquí no se guarda ningún secreto: ni contraseñas, ni claves de API, ni
 * credenciales de base de datos. El frontend solo conoce la URL pública.
 */
(function (global) {
    "use strict";

    var URL_API_POR_DEFECTO = "http://127.0.0.1:8000";

    function leerUrlBase() {
        var meta = document.querySelector('meta[name="api-base-url"]');
        var valor = meta && meta.content ? meta.content.trim() : "";
        var url = valor || URL_API_POR_DEFECTO;
        return url.replace(/\/+$/, "");
    }

    global.App = global.App || {};

    global.App.CONFIG = Object.freeze({
        /** Raíz de la API REST, sin barra final. */
        API_BASE_URL: leerUrlBase(),

        /** Rutas relativas de los endpoints existentes en el backend. */
        RUTAS: Object.freeze({
            USUARIOS: "/api/usuarios",
            CATEGORIAS: "/api/categorias",
            MOVIMIENTOS: "/api/movimientos",
            RESUMEN: "/api/resumen",
            PREDICCION: "/api/analitica/prediccion",
            ANOMALIAS: "/api/analitica/anomalias"
        }),

        /** Clave de almacenamiento local del usuario activo (solo su ID). */
        CLAVE_USUARIO: "finanzas.id_usuario",

        /** Identificador de usuario con el que arranca la aplicación. */
        ID_USUARIO_POR_DEFECTO: 1,

        /** Localización usada para formatear importes y fechas. */
        LOCALIZACION: "es-CO",

        /** Número de movimientos mostrados en el panel. */
        MOVIMIENTOS_EN_PANEL: 5
    });
})(window);
