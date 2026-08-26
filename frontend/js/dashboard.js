/**
 * dashboard.js — Vista principal (panel).
 *
 * Compone la pantalla de inicio a partir de tres llamadas a la API:
 *   GET /api/resumen              (delegado en resumen.js)
 *   GET /api/movimientos          (últimos movimientos, sin filtros)
 *   GET /api/analitica/prediccion (delegado en analytics.js)
 *
 * No calcula ningún importe: se limita a mostrar lo que responde el backend.
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var UI = App.UI;
    var CONFIG = App.CONFIG;

    var nodos = {};

    function capturarNodos() {
        nodos = {
            estado: document.getElementById("estado-ultimos"),
            tabla: document.getElementById("tabla-ultimos"),
            cuerpo: document.getElementById("cuerpo-ultimos")
        };
    }

    /** Descarga el historial completo y muestra solo los más recientes. */
    async function cargarUltimosMovimientos(idUsuario) {
        UI.mostrarEstado(nodos.estado, "cargando", "Cargando movimientos…");
        nodos.tabla.hidden = true;

        try {
            var lista = await Api.movimientos.listar(idUsuario);
            renderizarUltimos(lista.slice(0, CONFIG.MOVIMIENTOS_EN_PANEL));
        } catch (error) {
            UI.mostrarEstado(nodos.estado, "error", UI.mensajeDeExcepcion(error));
        }
    }

    function renderizarUltimos(lista) {
        UI.vaciar(nodos.cuerpo);

        if (!lista.length) {
            nodos.tabla.hidden = true;
            UI.mostrarEstado(nodos.estado, "vacio", "No hay movimientos registrados.");
            return;
        }

        lista.forEach(function (movimiento) {
            var fila = document.createElement("tr");

            fila.appendChild(UI.crearCelda(UI.formatearFecha(movimiento.fecha), "Fecha"));
            fila.appendChild(UI.crearCelda(movimiento.categoria, "Categoría"));

            var celdaTipo = UI.crearCelda("", "Tipo");
            celdaTipo.appendChild(UI.crearEtiquetaTipo(movimiento.tipo));
            fila.appendChild(celdaTipo);

            var claseMonto = "celda--numerica " + (movimiento.tipo === "ingreso" ? "celda--ingreso" : "celda--gasto");
            fila.appendChild(UI.crearCelda(UI.formatearImporte(movimiento.monto), "Monto", claseMonto));

            nodos.cuerpo.appendChild(fila);
        });

        UI.ocultarEstado(nodos.estado);
        nodos.tabla.hidden = false;
    }

    /** Carga completa del panel. */
    function cargar(idUsuario) {
        return Promise.all([
            App.Resumen.cargar(idUsuario),
            cargarUltimosMovimientos(idUsuario),
            App.Analytics.cargarPrediccionPanel(idUsuario)
        ]);
    }

    function inicializar() {
        capturarNodos();
    }

    App.Dashboard = {
        inicializar: inicializar,
        cargar: cargar
    };
})(window.App);
