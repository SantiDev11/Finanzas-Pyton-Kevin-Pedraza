/**
 * dashboard.js — Vista principal (Panel de Control y Gráficos Chart.js).
 *
 * Consolida la información del usuario a través de la API:
 *   - Resumen mensual y KPI cards (delegado en resumen.js)
 *   - Gráfico de gastos por categoría (Chart.js con datos reales)
 *   - Gráfico de tendencia mensual ingresos vs gastos (Chart.js con datos reales)
 *   - Últimos 5 movimientos financieros
 *   - Predicción de gasto para el panel
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var UI = App.UI;
    var CONFIG = App.CONFIG;

    var nodos = {};
    var chartCategorias = null;
    var chartTendencia = null;

    // Paleta de colores armoniosa para el gráfico de categorías
    var PALETA_GRAFICOS = [
        "#1d4ed8", "#3b82f6", "#06b6d4", "#10b981", "#f59e0b",
        "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#64748b"
    ];

    function capturarNodos() {
        nodos = {
            estadoUltimos: document.getElementById("estado-ultimos"),
            tablaUltimos: document.getElementById("tabla-ultimos"),
            cuerpoUltimos: document.getElementById("cuerpo-ultimos"),
            botonVerTodos: document.getElementById("boton-ver-todos-movimientos"),

            // Contenedores de gráficos
            estadoGraficoCategorias: document.getElementById("estado-grafico-categorias"),
            contenedorGraficoCategorias: document.getElementById("contenedor-grafico-categorias"),
            canvasCategorias: document.getElementById("canvas-grafico-categorias"),

            estadoGraficoTendencia: document.getElementById("estado-grafico-tendencia"),
            contenedorGraficoTendencia: document.getElementById("contenedor-grafico-tendencia"),
            canvasTendencia: document.getElementById("canvas-grafico-tendencia")
        };
    }

    /** Descarga y pinta los últimos 5 movimientos */
    async function cargarUltimosMovimientos() {
        UI.mostrarEstado(nodos.estadoUltimos, "cargando", "Cargando movimientos recientes…");
        if (nodos.tablaUltimos) {
            nodos.tablaUltimos.hidden = true;
        }

        try {
            var lista = await Api.movimientos.listar();
            renderizarUltimos(lista.slice(0, CONFIG.MOVIMIENTOS_EN_PANEL));
            renderizarGraficos(lista);
        } catch (error) {
            UI.mostrarEstado(nodos.estadoUltimos, "error", UI.mensajeDeExcepcion(error));
            if (nodos.estadoGraficoCategorias) {
                UI.mostrarEstado(nodos.estadoGraficoCategorias, "error", "No fue posible cargar datos para el gráfico.");
            }
            if (nodos.estadoGraficoTendencia) {
                UI.mostrarEstado(nodos.estadoGraficoTendencia, "error", "No fue posible cargar datos para la tendencia.");
            }
        }
    }

    function renderizarUltimos(lista) {
        UI.vaciar(nodos.cuerpoUltimos);

        if (!lista.length) {
            if (nodos.tablaUltimos) {
                nodos.tablaUltimos.hidden = true;
            }
            UI.mostrarEstado(nodos.estadoUltimos, "vacio", "No hay movimientos registrados.");
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
            fila.appendChild(UI.crearCelda(UI.formatearImporte(movimiento.monto), "Monto (COP)", claseMonto));

            nodos.cuerpoUltimos.appendChild(fila);
        });

        UI.ocultarEstado(nodos.estadoUltimos);
        if (nodos.tablaUltimos) {
            nodos.tablaUltimos.hidden = false;
        }
    }

    /* ======================================================================
       RENDERIZADO DE GRÁFICOS (CHART.JS)
       ====================================================================== */

    function renderizarGraficos(movimientos) {
        if (typeof Chart === "undefined") {
            if (nodos.estadoGraficoCategorias) {
                UI.mostrarEstado(nodos.estadoGraficoCategorias, "error", "Librería de gráficos no disponible.");
            }
            if (nodos.estadoGraficoTendencia) {
                UI.mostrarEstado(nodos.estadoGraficoTendencia, "error", "Librería de gráficos no disponible.");
            }
            return;
        }

        renderizarGraficoCategorias(movimientos);
        renderizarGraficoTendencia(movimientos);
    }

    /** Gráfico 1: Gastos por Categoría (Doughnut Chart) */
    function renderizarGraficoCategorias(movimientos) {
        if (!nodos.canvasCategorias) {
            return;
        }

        if (chartCategorias) {
            chartCategorias.destroy();
            chartCategorias = null;
        }

        // Agrupar gastos por categoría
        var gastosPorCat = {};
        movimientos.forEach(function (m) {
            if (m.tipo === "gasto") {
                var monto = UI.aNumero(m.monto) || 0;
                var nombre = m.categoria || "Sin categoría";
                gastosPorCat[nombre] = (gastosPorCat[nombre] || 0) + monto;
            }
        });

        var etiquetas = Object.keys(gastosPorCat);
        var valores = Object.values(gastosPorCat);

        if (!etiquetas.length) {
            UI.mostrarEstado(nodos.estadoGraficoCategorias, "vacio", "No hay gastos registrados para generar el gráfico.");
            if (nodos.contenedorGraficoCategorias) {
                nodos.contenedorGraficoCategorias.hidden = true;
            }
            return;
        }

        UI.ocultarEstado(nodos.estadoGraficoCategorias);
        if (nodos.contenedorGraficoCategorias) {
            nodos.contenedorGraficoCategorias.hidden = false;
        }

        var ctx = nodos.canvasCategorias.getContext("2d");
        chartCategorias = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: etiquetas,
                datasets: [{
                    data: valores,
                    backgroundColor: PALETA_GRAFICOS.slice(0, etiquetas.length),
                    borderWidth: 2,
                    borderColor: getComputedStyle(document.documentElement).getPropertyValue("--color-surface").trim() || "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            boxWidth: 12,
                            padding: 14,
                            font: { family: "inherit", size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                var valor = context.raw || 0;
                                return " " + context.label + ": " + UI.formatearImporte(valor);
                            }
                        }
                    }
                },
                cutout: "68%"
            }
        });
    }

    /** Gráfico 2: Tendencia Mensual Ingresos vs Gastos (Bar Chart) */
    function renderizarGraficoTendencia(movimientos) {
        if (!nodos.canvasTendencia) {
            return;
        }

        if (chartTendencia) {
            chartTendencia.destroy();
            chartTendencia = null;
        }

        if (!movimientos.length) {
            UI.mostrarEstado(nodos.estadoGraficoTendencia, "vacio", "No hay movimientos registrados para mostrar la tendencia.");
            if (nodos.contenedorGraficoTendencia) {
                nodos.contenedorGraficoTendencia.hidden = true;
            }
            return;
        }

        // Agrupar movimientos por mes (YYYY-MM)
        var datosPorMes = {};
        movimientos.forEach(function (m) {
            var periodo = (m.fecha || "").slice(0, 7);
            if (periodo && periodo.length === 7) {
                if (!datosPorMes[periodo]) {
                    datosPorMes[periodo] = { ingresos: 0, gastos: 0 };
                }
                var monto = UI.aNumero(m.monto) || 0;
                if (m.tipo === "ingreso") {
                    datosPorMes[periodo].ingresos += monto;
                } else {
                    datosPorMes[periodo].gastos += monto;
                }
            }
        });

        // Ordenar meses cronológicamente
        var mesesOrdenados = Object.keys(datosPorMes).sort();

        // Mostrar últimos 6 meses si hay muchos
        if (mesesOrdenados.length > 6) {
            mesesOrdenados = mesesOrdenados.slice(-6);
        }

        var etiquetas = mesesOrdenados.map(function (m) {
            return UI.formatearMes(m);
        });

        var datosIngresos = mesesOrdenados.map(function (m) {
            return datosPorMes[m].ingresos;
        });

        var datosGastos = mesesOrdenados.map(function (m) {
            return datosPorMes[m].gastos;
        });

        UI.ocultarEstado(nodos.estadoGraficoTendencia);
        if (nodos.contenedorGraficoTendencia) {
            nodos.contenedorGraficoTendencia.hidden = false;
        }

        var ctx = nodos.canvasTendencia.getContext("2d");
        chartTendencia = new Chart(ctx, {
            type: "bar",
            data: {
                labels: etiquetas,
                datasets: [
                    {
                        label: "Ingresos",
                        data: datosIngresos,
                        backgroundColor: "#10b981",
                        borderRadius: 6
                    },
                    {
                        label: "Gastos",
                        data: datosGastos,
                        backgroundColor: "#ef4444",
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            boxWidth: 12,
                            padding: 12,
                            font: { family: "inherit", size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return " " + context.dataset.label + ": " + UI.formatearImporte(context.raw);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (val) {
                                return UI.formatearImporte(val);
                            }
                        }
                    }
                }
            }
        });
    }

    /** Carga global del Dashboard */
    function cargar() {
        return Promise.all([
            App.Resumen.cargar(),
            cargarUltimosMovimientos(),
            App.Analytics.cargarPrediccionPanel()
        ]);
    }

    function inicializar() {
        capturarNodos();
        if (nodos.botonVerTodos) {
            nodos.botonVerTodos.addEventListener("click", function () {
                App.cambiarVista("movimientos");
            });
        }
    }

    App.Dashboard = {
        inicializar: inicializar,
        cargar: cargar
    };
})(window.App);
