/**
 * ui.js — Utilidades de presentación compartidas por todos los módulos.
 *
 * Formateo monetario en COP (Pesos Colombianos), formateo de fechas y meses,
 * estados visuales (loading, empty, error, success), notificaciones toast,
 * control de diálogos modales y protección contra inyección HTML.
 */
(function (App) {
    "use strict";

    var CONFIG = App.CONFIG;

    /**
     * Formateador monetario: Peso Colombiano (COP).
     * Muestra formato estándar colombiano con código COP y 2 decimales exactos.
     */
    var formateadorMoneda = new Intl.NumberFormat(CONFIG.LOCALIZACION, {
        style: "currency",
        currency: CONFIG.MONEDA,
        currencyDisplay: "code",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    /** Formateador numérico simple para Z-Score y estadísticas */
    var formateadorDecimal = new Intl.NumberFormat(CONFIG.LOCALIZACION, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    var NOMBRES_MES = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ];

    function elemento(selector) {
        return document.querySelector(selector);
    }

    function vaciar(nodo) {
        while (nodo && nodo.firstChild) {
            nodo.removeChild(nodo.firstChild);
        }
    }

    function aNumero(valor) {
        var numero = Number(valor);
        return Number.isFinite(numero) ? numero : null;
    }

    /** Formatea un importe en pesos colombianos: e.g. "COP 1.500.000,00" */
    function formatearImporte(valor) {
        var numero = aNumero(valor);
        if (numero === null) {
            return "—";
        }
        return formateadorMoneda.format(numero);
    }

    /** Formatea un número decimal simple: e.g. "1,85" */
    function formatearDecimal(valor) {
        var numero = aNumero(valor);
        return numero === null ? "—" : formateadorDecimal.format(numero);
    }

    /** Formatea una fecha ISO (YYYY-MM-DD) a DD/MM/AAAA sin desfases de zona horaria */
    function formatearFecha(iso) {
        if (typeof iso !== "string") {
            return "—";
        }
        var partes = iso.slice(0, 10).split("-");
        if (partes.length !== 3) {
            return iso;
        }
        return partes[2] + "/" + partes[1] + "/" + partes[0];
    }

    /** Convierte "2026-08" en "Agosto de 2026" */
    function formatearMes(mes) {
        if (typeof mes !== "string" || mes.length < 7) {
            return "—";
        }
        var anio = mes.slice(0, 4);
        var indice = Number(mes.slice(5, 7)) - 1;
        if (indice < 0 || indice > 11) {
            return mes;
        }
        return NOMBRES_MES[indice] + " de " + anio;
    }

    /** Devuelve el periodo mensual actual en formato YYYY-MM */
    function mesActual() {
        var hoy = new Date();
        return hoy.getFullYear() + "-" + String(hoy.getMonth() + 1).padStart(2, "0");
    }

    /** Devuelve la fecha actual en formato YYYY-MM-DD */
    function fechaHoy() {
        var hoy = new Date();
        return [
            hoy.getFullYear(),
            String(hoy.getMonth() + 1).padStart(2, "0"),
            String(hoy.getDate()).padStart(2, "0")
        ].join("-");
    }

    /**
     * Muestra uno de los estados de interfaz sobre su elemento contenedor.
     * @param {HTMLElement} nodo
     * @param {"cargando"|"vacio"|"error"|"exito"} tipo
     * @param {string} mensaje
     */
    function mostrarEstado(nodo, tipo, mensaje) {
        if (!nodo) {
            return;
        }
        nodo.className = "estado estado--" + tipo;
        nodo.textContent = mensaje;
        nodo.hidden = false;
    }

    function ocultarEstado(nodo) {
        if (nodo) {
            nodo.hidden = true;
        }
    }

    function mostrarErrorFormulario(nodo, mensaje) {
        if (!nodo) {
            return;
        }
        nodo.textContent = mensaje;
        nodo.hidden = false;
    }

    function limpiarErrorFormulario(nodo) {
        if (!nodo) {
            return;
        }
        nodo.textContent = "";
        nodo.hidden = true;
    }

    function crearCelda(texto, etiqueta, clase) {
        var celda = document.createElement("td");
        celda.textContent = texto;
        if (etiqueta) {
            celda.dataset.etiqueta = etiqueta;
        }
        if (clase) {
            celda.className = clase;
        }
        return celda;
    }

    function crearEtiquetaTipo(tipo) {
        var etiqueta = document.createElement("span");
        etiqueta.className = "etiqueta etiqueta--" + (tipo === "ingreso" ? "ingreso" : "gasto");
        etiqueta.textContent = tipo === "ingreso" ? "Ingreso" : "Gasto";
        return etiqueta;
    }

    /** Notificación flotante tipo toast */
    function notificar(mensaje, tipo) {
        var contenedor = document.getElementById("notificaciones");
        if (!contenedor) {
            return;
        }
        var aviso = document.createElement("p");
        aviso.className = "notificacion notificacion--" + (tipo || "exito");
        aviso.textContent = mensaje;
        contenedor.appendChild(aviso);
        window.setTimeout(function () {
            aviso.remove();
        }, 4500);
    }

    function abrirDialogo(dialogo, elementoFoco) {
        if (!dialogo) {
            return;
        }
        if (typeof dialogo.showModal === "function") {
            dialogo.showModal();
        } else {
            dialogo.setAttribute("open", "");
        }
        if (elementoFoco) {
            elementoFoco.focus();
        }
    }

    function cerrarDialogo(dialogo) {
        if (!dialogo) {
            return;
        }
        if (typeof dialogo.close === "function") {
            dialogo.close();
        } else {
            dialogo.removeAttribute("open");
        }
    }

    function mensajeDeExcepcion(error) {
        if (error && error.esErrorApi && error.message) {
            return error.message;
        }
        return App.Api.MENSAJE_RED;
    }

    App.UI = {
        elemento: elemento,
        vaciar: vaciar,
        aNumero: aNumero,
        formatearImporte: formatearImporte,
        formatearDecimal: formatearDecimal,
        formatearFecha: formatearFecha,
        formatearMes: formatearMes,
        mesActual: mesActual,
        fechaHoy: fechaHoy,
        mostrarEstado: mostrarEstado,
        ocultarEstado: ocultarEstado,
        mostrarErrorFormulario: mostrarErrorFormulario,
        limpiarErrorFormulario: limpiarErrorFormulario,
        crearCelda: crearCelda,
        crearEtiquetaTipo: crearEtiquetaTipo,
        notificar: notificar,
        abrirDialogo: abrirDialogo,
        cerrarDialogo: cerrarDialogo,
        mensajeDeExcepcion: mensajeDeExcepcion
    };
})(window.App);
