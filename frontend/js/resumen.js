/**
 * resumen.js — Resumen financiero mensual y KPI cards.
 *
 * Endpoint:
 *   GET /api/resumen?mes=
 *
 * Los importes (ingresos, gastos y balance) provienen directamente de la API.
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var UI = App.UI;

    var nodos = {};

    function capturarNodos() {
        nodos = {
            formulario: document.getElementById("form-resumen"),
            mes: document.getElementById("entrada-mes"),
            estado: document.getElementById("estado-resumen"),
            indicadores: document.getElementById("indicadores-resumen"),
            ingresos: document.getElementById("valor-ingresos"),
            gastos: document.getElementById("valor-gastos"),
            balance: document.getElementById("valor-balance"),
            tarjetaBalance: document.getElementById("tarjeta-balance"),
            notaBalance: document.getElementById("nota-balance")
        };
    }

    function mesSeleccionado() {
        return (nodos.mes && nodos.mes.value) ? nodos.mes.value : UI.mesActual();
    }

    /**
     * Descarga y muestra los KPI cards del resumen del mes indicado.
     * @param {string} [mes] Periodo YYYY-MM. Por defecto, el del selector.
     */
    async function cargar(mes) {
        var periodo = mes || mesSeleccionado();
        if (nodos.mes) {
            nodos.mes.value = periodo;
        }

        UI.mostrarEstado(nodos.estado, "cargando", "Cargando resumen de " + UI.formatearMes(periodo) + "…");
        if (nodos.indicadores) {
            nodos.indicadores.hidden = true;
        }

        try {
            var resumen = await Api.resumen.obtener(periodo);
            renderizar(resumen);
        } catch (error) {
            UI.mostrarEstado(nodos.estado, "error", UI.mensajeDeExcepcion(error));
        }
    }

    function renderizar(resumen) {
        if (nodos.ingresos) {
            nodos.ingresos.textContent = UI.formatearImporte(resumen.total_ingresos);
        }
        if (nodos.gastos) {
            nodos.gastos.textContent = UI.formatearImporte(resumen.total_gastos);
        }
        if (nodos.balance) {
            nodos.balance.textContent = UI.formatearImporte(resumen.balance);
        }

        var balance = UI.aNumero(resumen.balance);
        if (nodos.tarjetaBalance) {
            nodos.tarjetaBalance.classList.toggle("es-negativo", balance !== null && balance < 0);
        }

        if (nodos.notaBalance) {
            var pct = (resumen.porcentaje_ahorro !== undefined && resumen.porcentaje_ahorro !== null)
                ? resumen.porcentaje_ahorro
                : 0;
            nodos.notaBalance.textContent = "Ahorro: " + pct + "% del ingreso";
        }

        UI.ocultarEstado(nodos.estado);
        if (nodos.indicadores) {
            nodos.indicadores.hidden = false;
        }
    }

    function alEnviarFormulario(evento) {
        evento.preventDefault();
        if (!nodos.mes.value) {
            UI.mostrarEstado(nodos.estado, "error", "Selecciona un mes para consultar el resumen.");
            if (nodos.indicadores) {
                nodos.indicadores.hidden = true;
            }
            return;
        }
        cargar(nodos.mes.value);
    }

    function inicializar() {
        capturarNodos();
        if (nodos.mes) {
            nodos.mes.value = UI.mesActual();
        }
        if (nodos.formulario) {
            nodos.formulario.addEventListener("submit", alEnviarFormulario);
        }
    }

    App.Resumen = {
        inicializar: inicializar,
        cargar: cargar,
        mesSeleccionado: mesSeleccionado
    };
})(window.App);
