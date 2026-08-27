/**
 * analytics.js — Módulo analítico (predicción y anomalías).
 *
 * Endpoints utilizados:
 *   GET /api/analitica/prediccion?id_usuario=
 *   GET /api/analitica/anomalias?id_usuario=
 *
 * Todo lo que se muestra procede del backend: aquí no se estima, no se
 * extrapola y no se calcula ningún Z-Score en el cliente.
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var UI = App.UI;

    var MENSAJE_SIN_HISTORICO =
        "No hay suficientes datos históricos de gastos para calcular una predicción. " +
        "Registra movimientos de al menos dos meses distintos.";

    var DESCRIPCION_CONFIANZA = {
        alta: "Confianza alta (historial amplio ≥ 6 meses)",
        media: "Confianza media (2 a 5 meses de historial)",
        baja: "Confianza baja (historial inicial)"
    };

    var nodos = {};

    function capturarNodos() {
        nodos = {
            // KPI Card del Panel
            panelMes: document.getElementById("panel-prediccion-mes"),
            panelValor: document.getElementById("panel-prediccion-valor"),

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

    /** Una predicción es utilizable si el backend procesó algún mes de gastos */
    function tieneDatosSuficientes(prediccion) {
        return prediccion && prediccion.meses_procesados > 0 && Boolean(prediccion.mes_predicho);
    }

    function textoConfianza(prediccion) {
        return DESCRIPCION_CONFIANZA[prediccion.confianza] || "Confianza: " + prediccion.confianza;
    }

    /* ======================================================================
       PREDICCIÓN — KPI CARD DEL PANEL
       ====================================================================== */

    async function cargarPrediccionPanel(idUsuario) {
        if (nodos.panelValor) {
            nodos.panelValor.textContent = "…";
        }

        try {
            var prediccion = await Api.analitica.prediccion(idUsuario);

            if (!tieneDatosSuficientes(prediccion)) {
                if (nodos.panelValor) nodos.panelValor.textContent = "—";
                if (nodos.panelMes) nodos.panelMes.textContent = "Historial insuficiente";
                return;
            }

            if (nodos.panelMes) {
                nodos.panelMes.textContent = "Para " + UI.formatearMes(prediccion.mes_predicho);
            }
            if (nodos.panelValor) {
                nodos.panelValor.textContent = UI.formatearImporte(prediccion.gasto_estimado);
            }
        } catch (error) {
            if (nodos.panelValor) nodos.panelValor.textContent = "—";
            if (nodos.panelMes) nodos.panelMes.textContent = "No disponible";
        }
    }

    /* ======================================================================
       PREDICCIÓN — VISTA DE ANÁLISIS
       ====================================================================== */

    async function cargarPrediccion(idUsuario) {
        UI.mostrarEstado(nodos.estadoPrediccion, "cargando", "Calculando predicción con regresión lineal…");
        if (nodos.detalle) {
            nodos.detalle.hidden = true;
        }

        try {
            var prediccion = await Api.analitica.prediccion(idUsuario);

            if (!tieneDatosSuficientes(prediccion)) {
                UI.mostrarEstado(nodos.estadoPrediccion, "vacio", MENSAJE_SIN_HISTORICO);
                return;
            }

            if (nodos.mes) nodos.mes.textContent = "Gasto estimado para " + UI.formatearMes(prediccion.mes_predicho);
            if (nodos.valor) nodos.valor.textContent = UI.formatearImporte(prediccion.gasto_estimado);
            if (nodos.confianza) nodos.confianza.textContent = textoConfianza(prediccion);
            if (nodos.meses) nodos.meses.textContent = String(prediccion.meses_procesados) + " meses";
            if (nodos.razon) nodos.razon.textContent = prediccion.razon;

            UI.ocultarEstado(nodos.estadoPrediccion);
            if (nodos.detalle) {
                nodos.detalle.hidden = false;
            }
        } catch (error) {
            UI.mostrarEstado(nodos.estadoPrediccion, "error", UI.mensajeDeExcepcion(error));
        }
    }

    /* ======================================================================
       ANOMALÍAS
       ====================================================================== */

    async function cargarAnomalias(idUsuario) {
        UI.mostrarEstado(nodos.estadoAnomalias, "cargando", "Analizando anomalías estadísticas con Z-Score…");
        if (nodos.tablaAnomalias) {
            nodos.tablaAnomalias.hidden = true;
        }
        if (nodos.contadorAnomalias) {
            nodos.contadorAnomalias.textContent = "";
        }

        try {
            var resultado = await Api.analitica.anomalias(idUsuario);
            renderizarAnomalias(resultado);
        } catch (error) {
            UI.mostrarEstado(nodos.estadoAnomalias, "error", UI.mensajeDeExcepcion(error));
        }
    }

    function renderizarAnomalias(resultado) {
        UI.vaciar(nodos.cuerpoAnomalias);

        var lista = (resultado && resultado.anomalias) || [];
        if (!lista.length) {
            if (nodos.tablaAnomalias) nodos.tablaAnomalias.hidden = true;
            if (nodos.contadorAnomalias) {
                nodos.contadorAnomalias.textContent =
                    (resultado ? resultado.total_gastos_analizados : 0) + " gastos analizados";
            }
            UI.mostrarEstado(nodos.estadoAnomalias, "exito", "No se detectaron anomalías en los gastos registrados.");
            return;
        }

        lista.forEach(function (anomalia) {
            var fila = document.createElement("tr");

            fila.appendChild(UI.crearCelda(UI.formatearFecha(anomalia.fecha), "Fecha"));
            fila.appendChild(UI.crearCelda(
                UI.formatearImporte(anomalia.monto), "Monto (COP)", "celda--numerica celda--gasto"
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

        if (nodos.contadorAnomalias) {
            nodos.contadorAnomalias.textContent =
                resultado.total_anomalias + " de " + resultado.total_gastos_analizados +
                " gastos superan el umbral |Z| > " + UI.formatearDecimal(resultado.umbral_z_score);
        }

        UI.ocultarEstado(nodos.estadoAnomalias);
        if (nodos.tablaAnomalias) {
            nodos.tablaAnomalias.hidden = false;
        }
    }

    /* ====================================================================== */

    function cargar(idUsuario) {
        return Promise.all([
            cargarPrediccion(idUsuario),
            cargarAnomalias(idUsuario)
        ]);
    }

    function inicializar() {
        capturarNodos();
        if (nodos.botonRecargar) {
            nodos.botonRecargar.addEventListener("click", function () {
                cargar(App.usuarioActivo());
            });
        }
    }

    App.Analytics = {
        inicializar: inicializar,
        cargar: cargar,
        cargarPrediccionPanel: cargarPrediccionPanel
    };
})(window.App);
