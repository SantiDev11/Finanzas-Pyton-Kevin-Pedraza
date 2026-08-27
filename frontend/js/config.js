/**
 * config.js — Configuración única del frontend.
 *
 * La URL de la API se declara en un solo sitio: la constante
 * URL_API_POR_DEFECTO de este archivo, que comparten las dos páginas del
 * frontend (index.html y dashboard.html). Para apuntar a otro entorno —por
 * ejemplo la URL pública de Render— basta con cambiar esa línea; ningún otro
 * archivo del proyecto contiene URLs de la API.
 *
 * Como alternativa, una página puede sobrescribirla sin tocar el JavaScript
 * añadiendo <meta name="api-base-url" content="..."> en su <head>.
 *
 * Aquí no se guarda ningún secreto: ni contraseñas, ni claves de API, ni
 * credenciales de base de datos, ni la SECRET_KEY que firma los tokens (esa
 * vive solo en el backend). El frontend solo conoce la URL pública.
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
            LOGIN: "/api/auth/login",
            YO: "/api/auth/me",
            USUARIOS: "/api/usuarios",
            CATEGORIAS: "/api/categorias",
            MOVIMIENTOS: "/api/movimientos",
            RESUMEN: "/api/resumen",
            PREDICCION: "/api/analitica/prediccion",
            ANOMALIAS: "/api/analitica/anomalias"
        }),

        /** Localización usada para formatear importes y fechas. */
        LOCALIZACION: "es-CO",

        /** Moneda de presentación: peso colombiano (ISO 4217). */
        MONEDA: "COP",

        /**
         * Clave de sesión en sessionStorage.
         *
         * Guarda el token de acceso y los datos públicos del usuario (id,
         * nombre y correo). Nunca la contraseña ni ningún hash.
         */
        CLAVE_SESION: "finanzas.sesion",

        /** Número de movimientos mostrados en el panel. */
        MOVIMIENTOS_EN_PANEL: 5
    });
})(window);
