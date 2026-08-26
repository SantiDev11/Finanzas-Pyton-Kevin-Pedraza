/**
 * ui.js — Utilidades de presentación compartidas por todos los módulos.
 *
 * Aquí vive todo lo que toca el DOM de forma genérica: formateo de importes y
 * fechas, estados de carga/vacío/error, notificaciones y diálogos. Los módulos
 * de negocio (movimientos, categorías, resumen, análisis) no repiten este
 * código ni construyen HTML con innerHTML: siempre se usa textContent, de modo
 * que ningún dato del backend puede inyectarse como marcado.
 */
(function (App) {
    "use strict";

    var CONFIG = App.CONFIG;

    /* Un único formateador numérico con dos decimales, reutilizado tanto para
       importes como para valores estadísticos (Z-Score). */
    var formateadorDecimal = new Intl.NumberFormat(CONFIG.LOCALIZACION, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    var NOMBRES_MES = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ];

    /** Atajo de document.querySelector. */
    function elemento(selector) {
        return document.querySelector(selector);
    }

    /** Elimina todos los hijos de un nodo. */
    function vaciar(nodo) {
        while (nodo.firstChild) {
            nodo.removeChild(nodo.firstChild);
        }
    }

    /** Convierte a número los importes, que la API serializa como cadena. */
    function aNumero(valor) {
        var numero = Number(valor);
        return Number.isFinite(numero) ? numero : null;
    }

    /** Formatea un importe monetario. Devuelve "—" si el valor no es numérico. */
    function formatearImporte(valor) {
        var numero = aNumero(valor);
        return numero === null ? "—" : "$ " + formateadorDecimal.format(numero);
    }

    /** Formatea un número decimal simple (por ejemplo un Z-Score). */
    function formatearDecimal(valor) {
        var numero = aNumero(valor);
        return numero === null ? "—" : formateadorDecimal.format(numero);
    }

    /**
     * Formatea una fecha ISO (YYYY-MM-DD) como DD/MM/AAAA.
     * Se parsea manualmente para no depender de la zona horaria del navegador.
     */
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

    /** Convierte "2026-08" en "agosto de 2026". */
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

    /** Devuelve el mes actual en formato YYYY-MM. */
    function mesActual() {
        var hoy = new Date();
        return hoy.getFullYear() + "-" + String(hoy.getMonth() + 1).padStart(2, "0");
    }

    /** Devuelve la fecha de hoy en formato YYYY-MM-DD. */
    function fechaHoy() {
        var hoy = new Date();
        return [
            hoy.getFullYear(),
            String(hoy.getMonth() + 1).padStart(2, "0"),
            String(hoy.getDate()).padStart(2, "0")
        ].join("-");
    }

    /**
     * Pinta uno de los cuatro estados de interfaz sobre su elemento contenedor.
     *
     * @param {HTMLElement} nodo Elemento de estado (role="status").
     * @param {"cargando"|"vacio"|"error"|"exito"} tipo
     * @param {string} mensaje Texto visible para la persona usuaria.
     */
    function mostrarEstado(nodo, tipo, mensaje) {
        if (!nodo) {
            return;
        }
        nodo.className = "estado estado--" + tipo;
        nodo.textContent = mensaje;
        nodo.hidden = false;
    }

    /** Oculta el bloque de estado (caso "success" con datos en pantalla). */
    function ocultarEstado(nodo) {
        if (nodo) {
            nodo.hidden = true;
        }
    }

    /** Muestra un mensaje de error dentro de un formulario. */
    function mostrarErrorFormulario(nodo, mensaje) {
        if (!nodo) {
            return;
        }
        nodo.textContent = mensaje;
        nodo.hidden = false;
    }

    /** Limpia el mensaje de error de un formulario. */
    function limpiarErrorFormulario(nodo) {
        if (!nodo) {
            return;
        }
        nodo.textContent = "";
        nodo.hidden = true;
    }

    /** Crea una celda de tabla con su etiqueta para la vista apilada en móvil. */
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

    /** Crea la etiqueta visual de tipo (ingreso / gasto). */
    function crearEtiquetaTipo(tipo) {
        var etiqueta = document.createElement("span");
        etiqueta.className = "etiqueta etiqueta--" + (tipo === "ingreso" ? "ingreso" : "gasto");
        etiqueta.textContent = tipo === "ingreso" ? "Ingreso" : "Gasto";
        return etiqueta;
    }

    /** Muestra una notificación efímera en la esquina inferior. */
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

    /** Abre un <dialog> y coloca el foco en su primer campo utilizable. */
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

    /** Cierra un <dialog>. */
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

    /** Extrae el mensaje presentable de cualquier error capturado. */
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
