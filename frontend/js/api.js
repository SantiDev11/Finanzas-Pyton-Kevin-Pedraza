/**
 * api.js — Capa centralizada de acceso a la API REST.
 *
 * Responsabilidades:
 *   - construir las URLs a partir de App.CONFIG (única fuente de la base URL);
 *   - ejecutar todas las peticiones fetch de la aplicación;
 *   - adjuntar el token de acceso en la cabecera Authorization;
 *   - detectar la expiración de la sesión (401) y avisar a la aplicación;
 *   - convertir cualquier fallo en un ErrorApi con un mensaje comprensible;
 *   - devolver siempre JSON ya parseado.
 *
 * Ningún otro archivo debe llamar a fetch() directamente.
 */
(function (App) {
    "use strict";

    var CONFIG = App.CONFIG;

    var MENSAJES_POR_ESTADO = {
        400: "La solicitud contiene datos inválidos.",
        401: "Tu sesión no es válida o ha expirado. Vuelve a iniciar sesión.",
        404: "El recurso solicitado no existe.",
        409: "El recurso ya existe o entra en conflicto con otro.",
        422: "Algún dato del formulario no tiene el formato esperado.",
        500: "Error interno del servidor. Inténtalo de nuevo más tarde."
    };

    var MENSAJE_RED = "No fue posible conectar con el servidor. Comprueba que la API esté en ejecución.";

    /**
     * Error de API con el código HTTP y un mensaje ya apto para mostrarse.
     */
    function ErrorApi(mensaje, estado) {
        var error = new Error(mensaje);
        error.name = "ErrorApi";
        error.estado = estado || 0;
        error.esErrorApi = true;
        return error;
    }

    /**
     * Compone la URL final de un endpoint con sus parámetros de consulta.
     * Los parámetros nulos, indefinidos o vacíos se descartan.
     */
    function construirUrl(ruta, parametros) {
        var url = CONFIG.API_BASE_URL + ruta;
        var consulta = new URLSearchParams();

        Object.keys(parametros || {}).forEach(function (clave) {
            var valor = parametros[clave];
            if (valor !== null && valor !== undefined && valor !== "") {
                consulta.append(clave, valor);
            }
        });

        var cadena = consulta.toString();
        return cadena ? url + "?" + cadena : url;
    }

    /**
     * Traduce el cuerpo de una respuesta de error a un mensaje para el usuario.
     * Nunca se propagan trazas, SQL ni detalles internos: para los 500 siempre
     * se usa un texto genérico.
     */
    function mensajeDeError(estado, cuerpo) {
        if (estado >= 500) {
            return MENSAJES_POR_ESTADO[500];
        }

        if (cuerpo && typeof cuerpo.detail === "string" && cuerpo.detail.trim()) {
            var detalle = cuerpo.detail.trim();
            if (estado === 422 && Array.isArray(cuerpo.errors) && cuerpo.errors.length) {
                return detalle + ": " + cuerpo.errors.join("; ");
            }
            return detalle;
        }

        return MENSAJES_POR_ESTADO[estado] || "No fue posible completar la operación.";
    }

    /**
     * Ejecuta una petición contra la API y devuelve el JSON de la respuesta.
     *
     * @param {string} ruta Ruta relativa del endpoint.
     * @param {Object} [opciones] metodo, cuerpo y parametros de consulta.
     * @returns {Promise<Object>} Cuerpo de la respuesta ya parseado.
     * @throws {Error} ErrorApi con mensaje presentable y código HTTP.
     */
    async function solicitar(ruta, opciones) {
        var config = opciones || {};
        var metodo = config.metodo || "GET";
        var peticion = {
            method: metodo,
            headers: { Accept: "application/json" }
        };

        // El token viaja siempre en la cabecera Authorization, nunca en la URL:
        // un query string queda registrado en logs, historiales y proxies.
        // App.Sesion se consulta aquí, y no al cargar el módulo, porque
        // sesion.js se carga después que api.js.
        if (!config.sinAutenticacion && App.Sesion) {
            var token = App.Sesion.token();
            if (token) {
                peticion.headers["Authorization"] = "Bearer " + token;
            }
        }

        if (config.cuerpo !== undefined && config.cuerpo !== null) {
            peticion.headers["Content-Type"] = "application/json";
            peticion.body = JSON.stringify(config.cuerpo);
        }

        var respuesta;
        try {
            respuesta = await fetch(construirUrl(ruta, config.parametros), peticion);
        } catch (fallo) {
            throw ErrorApi(MENSAJE_RED, 0);
        }

        var datos = null;
        try {
            datos = await respuesta.json();
        } catch (fallo) {
            datos = null;
        }

        if (!respuesta.ok) {
            var error = ErrorApi(mensajeDeError(respuesta.status, datos), respuesta.status);

            // Un 401 en una petición autenticada significa que la sesión dejó de
            // valer (token caducado, manipulado, o usuario eliminado). Se avisa
            // a quien escuche para que limpie la sesión y vuelva al acceso. En el
            // propio login no aplica: allí un 401 solo indica credenciales
            // incorrectas.
            if (respuesta.status === 401 && !config.sinAutenticacion) {
                document.dispatchEvent(new CustomEvent("sesion:expirada"));
            }

            throw error;
        }

        return datos;
    }

    App.Api = {
        ErrorApi: ErrorApi,
        MENSAJE_RED: MENSAJE_RED,

        auth: {
            /**
             * POST /api/auth/login
             *
             * Única petición que se envía sin token: es la que lo obtiene. Un
             * 401 aquí significa credenciales incorrectas, no sesión caducada.
             */
            iniciarSesion: function (correo, contrasena) {
                return solicitar(CONFIG.RUTAS.LOGIN, {
                    metodo: "POST",
                    cuerpo: { correo: correo, contrasena: contrasena },
                    sinAutenticacion: true
                });
            },
            /** GET /api/auth/me — comprueba que el token sigue siendo válido. */
            yo: function () {
                return solicitar(CONFIG.RUTAS.YO);
            }
        },

        usuarios: {
            /** POST /api/usuarios — registro, no requiere token. */
            registrar: function (datos) {
                return solicitar(CONFIG.RUTAS.USUARIOS, {
                    metodo: "POST",
                    cuerpo: datos,
                    sinAutenticacion: true
                });
            }
        },

        categorias: {
            /** GET /api/categorias — las del usuario autenticado. */
            listar: function () {
                return solicitar(CONFIG.RUTAS.CATEGORIAS);
            },
            /** POST /api/categorias */
            crear: function (datos) {
                return solicitar(CONFIG.RUTAS.CATEGORIAS, { metodo: "POST", cuerpo: datos });
            },
            /** PUT /api/categorias/{id} */
            actualizar: function (idCategoria, datos) {
                return solicitar(CONFIG.RUTAS.CATEGORIAS + "/" + idCategoria, {
                    metodo: "PUT",
                    cuerpo: datos
                });
            },
            /** DELETE /api/categorias/{id} */
            eliminar: function (idCategoria) {
                return solicitar(CONFIG.RUTAS.CATEGORIAS + "/" + idCategoria, {
                    metodo: "DELETE"
                });
            }
        },

        movimientos: {
            /** GET /api/movimientos?desde=&hasta=&categoria= */
            listar: function (filtros) {
                return solicitar(CONFIG.RUTAS.MOVIMIENTOS, { parametros: filtros || {} });
            },
            /** POST /api/movimientos */
            crear: function (datos) {
                return solicitar(CONFIG.RUTAS.MOVIMIENTOS, { metodo: "POST", cuerpo: datos });
            },
            /** PUT /api/movimientos/{id} */
            actualizar: function (idMovimiento, datos) {
                return solicitar(CONFIG.RUTAS.MOVIMIENTOS + "/" + idMovimiento, {
                    metodo: "PUT",
                    cuerpo: datos
                });
            },
            /** DELETE /api/movimientos/{id} */
            eliminar: function (idMovimiento) {
                return solicitar(CONFIG.RUTAS.MOVIMIENTOS + "/" + idMovimiento, {
                    metodo: "DELETE"
                });
            }
        },

        resumen: {
            /** GET /api/resumen?mes= */
            obtener: function (mes) {
                return solicitar(CONFIG.RUTAS.RESUMEN, { parametros: { mes: mes } });
            }
        },

        analitica: {
            /** GET /api/analitica/prediccion */
            prediccion: function () {
                return solicitar(CONFIG.RUTAS.PREDICCION);
            },
            /** GET /api/analitica/anomalias */
            anomalias: function () {
                return solicitar(CONFIG.RUTAS.ANOMALIAS);
            }
        }
    };
})(window.App);
