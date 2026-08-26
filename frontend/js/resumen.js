/**
 * resumen.js — Resumen financiero mensual.
 *
 * Endpoint utilizado:
 *   GET /api/resumen?id_usuario=&mes=
 *
 * Los tres importes (ingresos, gastos y balance) se muestran exactamente como
 * los devuelve el backend. El frontend no vuelve a sumar ni a restar nada: la
 * única operación local es el ancho en porcentaje de la barra comparativa, que
 * es un recurso visual y no un importe.
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
            tarjetaBalance: document.querySelector(".indicador--balance"),
            proporcion: document.getElementById("proporcion-resumen"),
            barraIngresos: document.getElementById("barra-ingresos"),
            barraGastos: document.getElementById("barra-gastos")
        };
    }

    /** Mes seleccionado; si el campo está vacío se usa el mes en curso. */
    function mesSeleccionado() {
        return nodos.mes.value || UI.mesActual();
    }

    /**
     * Descarga y pinta el resumen del mes indicado.
     * @param {number} idUsuario
     * @param {string} [mes] Periodo YYYY-MM. Por defecto, el del selector.
     */
    async function cargar(idUsuario, mes) {
        var periodo = mes || mesSeleccionado();
        nodos.mes.value = periodo;

        UI.mostrarEstado(nodos.estado, "cargando", "Cargando resumen de " + UI.formatearMes(periodo) + "…");
        nodos.indicadores.hidden = true;
        nodos.proporcion.hidden = true;

        try {
            var resumen = await Api.resumen.obtener(idUsuario, periodo);
            renderizar(resumen);
        } catch (error) {
            UI.mostrarEstado(nodos.estado, "error", UI.mensajeDeExcepcion(error));
        }
    }

    /** Vuelca en pantalla los importes tal cual llegan de la API. */
    function renderizar(resumen) {
        nodos.ingresos.textContent = UI.formatearImporte(resumen.total_ingresos);
        nodos.gastos.textContent = UI.formatearImporte(resumen.total_gastos);
        nodos.balance.textContent = UI.formatearImporte(resumen.balance);

        var balance = UI.aNumero(resumen.balance);
        nodos.tarjetaBalance.classList.toggle("es-negativo", balance !== null && balance < 0);

        actualizarProporcion(resumen);

        UI.ocultarEstado(nodos.estado);
        nodos.indicadores.hidden = false;
    }

    /**
     * Ajusta la barra comparativa. Solo calcula anchos en porcentaje; ningún
     * importe mostrado en pantalla procede de esta operación.
     */
    function actualizarProporcion(resumen) {
        var ingresos = UI.aNumero(resumen.total_ingresos) || 0;
        var gastos = UI.aNumero(resumen.total_gastos) || 0;
        var total = ingresos + gastos;

        if (total <= 0) {
            nodos.proporcion.hidden = true;
            return;
        }

        nodos.barraIngresos.style.width = (ingresos / total) * 100 + "%";
        nodos.barraGastos.style.width = (gastos / total) * 100 + "%";
        nodos.proporcion.hidden = false;
    }

    function alEnviarFormulario(evento) {
        evento.preventDefault();
        if (!nodos.mes.value) {
            UI.mostrarEstado(nodos.estado, "error", "Selecciona un mes para consultar el resumen.");
            nodos.indicadores.hidden = true;
            nodos.proporcion.hidden = true;
            return;
        }
        cargar(App.usuarioActivo(), nodos.mes.value);
    }

    function inicializar() {
        capturarNodos();
        nodos.mes.value = UI.mesActual();
        nodos.formulario.addEventListener("submit", alEnviarFormulario);
    }

    App.Resumen = {
        inicializar: inicializar,
        cargar: cargar,
        mesSeleccionado: mesSeleccionado
    };
})(window.App);
