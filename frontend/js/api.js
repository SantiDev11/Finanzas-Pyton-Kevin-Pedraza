/**
 * api.js — Capa centralizada de acceso a la API REST.
 *
 * Responsabilidades:
 *   - construir las URLs a partir de App.CONFIG (única fuente de la base URL);
 *   - ejecutar todas las peticiones fetch de la aplicación;
 *   - fijar las cabeceras;
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
            throw ErrorApi(mensajeDeError(respuesta.status, datos), respuesta.status);
        }

        return datos;
    }

    App.Api = {
        ErrorApi: ErrorApi,
        MENSAJE_RED: MENSAJE_RED,

        usuarios: {
            /** POST /api/usuarios */
            registrar: function (datos) {
                return solicitar(CONFIG.RUTAS.USUARIOS, { metodo: "POST", cuerpo: datos });
            }
        },

        categorias: {
            /** GET /api/categorias?id_usuario= */
            listar: function (idUsuario) {
                return solicitar(CONFIG.RUTAS.CATEGORIAS, { parametros: { id_usuario: idUsuario } });
            },
            /** POST /api/categorias */
            crear: function (datos) {
                return solicitar(CONFIG.RUTAS.CATEGORIAS, { metodo: "POST", cuerpo: datos });
            }
        },

        movimientos: {
            /** GET /api/movimientos?id_usuario=&desde=&hasta=&categoria= */
            listar: function (idUsuario, filtros) {
                var parametros = Object.assign({ id_usuario: idUsuario }, filtros || {});
                return solicitar(CONFIG.RUTAS.MOVIMIENTOS, { parametros: parametros });
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
            /** DELETE /api/movimientos/{id}?id_usuario= */
            eliminar: function (idMovimiento, idUsuario) {
                return solicitar(CONFIG.RUTAS.MOVIMIENTOS + "/" + idMovimiento, {
                    metodo: "DELETE",
                    parametros: { id_usuario: idUsuario }
                });
            }
        },

        resumen: {
            /** GET /api/resumen?id_usuario=&mes= */
            obtener: function (idUsuario, mes) {
                return solicitar(CONFIG.RUTAS.RESUMEN, { parametros: { id_usuario: idUsuario, mes: mes } });
            }
        },

        analitica: {
            /** GET /api/analitica/prediccion?id_usuario= */
            prediccion: function (idUsuario) {
                return solicitar(CONFIG.RUTAS.PREDICCION, { parametros: { id_usuario: idUsuario } });
            },
            /** GET /api/analitica/anomalias?id_usuario= */
            anomalias: function (idUsuario) {
                return solicitar(CONFIG.RUTAS.ANOMALIAS, { parametros: { id_usuario: idUsuario } });
            }
        }
    };
})(window.App);
