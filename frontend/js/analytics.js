/**
 * analytics.js — Módulo analítico (predicción y anomalías).
 *
 * Endpoints utilizados:
 *   GET /api/analitica/prediccion?id_usuario=
 *   GET /api/analitica/anomalias?id_usuario=
 *
 * Todo lo que se muestra procede del backend: aquí no se estima, no se
 * extrapola y no se calcula ningún Z-Score. Cuando el histórico es
 * insuficiente se explica la situación en lugar de inventar un número.
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var UI = App.UI;

    var MENSAJE_SIN_HISTORICO =
        "No hay suficientes datos históricos de gastos para calcular una predicción. " +
        "Registra movimientos de al menos dos meses distintos.";

    var DESCRIPCION_CONFIANZA = {
        alta: "Confianza alta: seis meses o más de histórico.",
        media: "Confianza media: entre dos y cinco meses de histórico.",
        baja: "Confianza baja: histórico insuficiente para una regresión."
    };

    var nodos = {};

    function capturarNodos() {
        nodos = {
            // Tarjeta compacta del panel
            estadoPanel: document.getElementById("estado-prediccion-panel"),
            panel: document.getElementById("prediccion-panel"),
            panelMes: document.getElementById("panel-prediccion-mes"),
            panelValor: document.getElementById("panel-prediccion-valor"),
            panelConfianza: document.getElementById("panel-prediccion-confianza"),

            // Vista de análisis
            estadoPrediccion: document.getElementById("estado-prediccion"),
            detalle: document.getElementById("detalle-prediccion"),
            mes: document.getElementById("prediccion-mes"),
            valor: document.getElementById("prediccion-valor"),
            confianza: document.getElementById("prediccion-confianza"),
            meses: document.getElementById("prediccion-meses"),
            razon: document.getElementById("prediccion-razon"),

            estadoAnomalias: document.getElementById("estado-anomalias"),
            tablaAnomalias: document.getElementById("tabla-anomalias"),
            cuerpoAnomalias: document.getElementById("cuerpo-anomalias"),
            contadorAnomalias: document.getElementById("contador-anomalias"),

            botonRecargar: document.getElementById("boton-recargar-analisis")
        };
    }

    /** Una predicción es utilizable si el backend procesó algún mes de gastos. */
    function tieneDatosSuficientes(prediccion) {
        return prediccion.meses_procesados > 0 && Boolean(prediccion.mes_predicho);
    }

    function textoConfianza(prediccion) {
        return DESCRIPCION_CONFIANZA[prediccion.confianza] || "Confianza: " + prediccion.confianza;
    }

    /* ======================================================================
       PREDICCIÓN — TARJETA DEL PANEL
       ====================================================================== */

    async function cargarPrediccionPanel(idUsuario) {
        UI.mostrarEstado(nodos.estadoPanel, "cargando", "Calculando predicción…");
        nodos.panel.hidden = true;

        try {
            var prediccion = await Api.analitica.prediccion(idUsuario);

            if (!tieneDatosSuficientes(prediccion)) {
                UI.mostrarEstado(nodos.estadoPanel, "vacio", MENSAJE_SIN_HISTORICO);
                return;
            }

            nodos.panelMes.textContent = UI.formatearMes(prediccion.mes_predicho);
            nodos.panelValor.textContent = UI.formatearImporte(prediccion.gasto_estimado);
            nodos.panelConfianza.textContent = textoConfianza(prediccion);

            UI.ocultarEstado(nodos.estadoPanel);
            nodos.panel.hidden = false;
        } catch (error) {
            UI.mostrarEstado(nodos.estadoPanel, "error", UI.mensajeDeExcepcion(error));
        }
    }

    /* ======================================================================
       PREDICCIÓN — VISTA DE ANÁLISIS
       ====================================================================== */

    async function cargarPrediccion(idUsuario) {
        UI.mostrarEstado(nodos.estadoPrediccion, "cargando", "Calculando predicción…");
        nodos.detalle.hidden = true;

        try {
            var prediccion = await Api.analitica.prediccion(idUsuario);

            if (!tieneDatosSuficientes(prediccion)) {
                UI.mostrarEstado(nodos.estadoPrediccion, "vacio", MENSAJE_SIN_HISTORICO);
                return;
            }

            nodos.mes.textContent = "Gasto estimado para " + UI.formatearMes(prediccion.mes_predicho);
            nodos.valor.textContent = UI.formatearImporte(prediccion.gasto_estimado);
            nodos.confianza.textContent = prediccion.confianza + " — " + textoConfianza(prediccion);
            nodos.meses.textContent = String(prediccion.meses_procesados);
            nodos.razon.textContent = prediccion.razon;

            UI.ocultarEstado(nodos.estadoPrediccion);
            nodos.detalle.hidden = false;
        } catch (error) {
            UI.mostrarEstado(nodos.estadoPrediccion, "error", UI.mensajeDeExcepcion(error));
        }
    }

    /* ======================================================================
       ANOMALÍAS
       ====================================================================== */

    async function cargarAnomalias(idUsuario) {
        UI.mostrarEstado(nodos.estadoAnomalias, "cargando", "Analizando gastos…");
        nodos.tablaAnomalias.hidden = true;
        nodos.contadorAnomalias.textContent = "";

        try {
            var resultado = await Api.analitica.anomalias(idUsuario);
            renderizarAnomalias(resultado);
        } catch (error) {
            UI.mostrarEstado(nodos.estadoAnomalias, "error", UI.mensajeDeExcepcion(error));
        }
    }

    /** Una respuesta sin anomalías es un resultado válido, no un error. */
    function renderizarAnomalias(resultado) {
        UI.vaciar(nodos.cuerpoAnomalias);

        var lista = resultado.anomalias || [];
        if (!lista.length) {
            nodos.tablaAnomalias.hidden = true;
            nodos.contadorAnomalias.textContent =
                resultado.total_gastos_analizados + " gastos analizados";
            UI.mostrarEstado(nodos.estadoAnomalias, "exito", "No se detectaron anomalías.");
            return;
        }

        lista.forEach(function (anomalia) {
            var fila = document.createElement("tr");

            fila.appendChild(UI.crearCelda(UI.formatearFecha(anomalia.fecha), "Fecha"));
            fila.appendChild(UI.crearCelda(
                UI.formatearImporte(anomalia.monto), "Monto", "celda--numerica celda--gasto"
            ));
            fila.appendChild(UI.crearCelda(App.Categorias.nombreDe(anomalia.id_categoria), "Categoría"));

            var celdaZ = UI.crearCelda("", "Z-Score", "celda--numerica");
            var etiqueta = document.createElement("span");
            etiqueta.className = "etiqueta etiqueta--aviso";
            etiqueta.textContent = UI.formatearDecimal(anomalia.z_score);
            celdaZ.appendChild(etiqueta);
            fila.appendChild(celdaZ);

            fila.appendChild(UI.crearCelda(anomalia.descripcion || "—", "Descripción"));

            nodos.cuerpoAnomalias.appendChild(fila);
        });

        nodos.contadorAnomalias.textContent =
            resultado.total_anomalias + " de " + resultado.total_gastos_analizados +
            " gastos superan el umbral |Z| > " + UI.formatearDecimal(resultado.umbral_z_score);

        UI.ocultarEstado(nodos.estadoAnomalias);
        nodos.tablaAnomalias.hidden = false;
    }

    /* ====================================================================== */

    /** Carga completa de la vista de análisis. */
    function cargar(idUsuario) {
        return Promise.all([
            cargarPrediccion(idUsuario),
            cargarAnomalias(idUsuario)
        ]);
    }

    function inicializar() {
        capturarNodos();
        nodos.botonRecargar.addEventListener("click", function () {
            cargar(App.usuarioActivo());
        });
    }

    App.Analytics = {
        inicializar: inicializar,
        cargar: cargar,
        cargarPrediccionPanel: cargarPrediccionPanel
    };
})(window.App);
