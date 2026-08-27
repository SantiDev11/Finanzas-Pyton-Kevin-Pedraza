/**
 * categorias.js — Gestión de categorías.
 *
 * Endpoints utilizados (los únicos que expone el backend para categorías):
 *   GET  /api/categorias
 *   POST /api/categorias
 *
 * Ninguno lleva id_usuario: el backend deduce el propietario del token.
 *
 * El módulo mantiene además la caché de categorías del usuario activo, que
 * reutilizan los desplegables de movimientos y la tabla de anomalías para
 * traducir un id_categoria a su nombre.
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var UI = App.UI;

    /** Categorías del usuario autenticado. */
    var categorias = [];

    var nodos = {};

    function capturarNodos() {
        nodos = {
            estado: document.getElementById("estado-categorias"),
            tabla: document.getElementById("tabla-categorias"),
            cuerpo: document.getElementById("cuerpo-categorias"),
            contador: document.getElementById("contador-categorias"),
            formulario: document.getElementById("form-categoria"),
            nombre: document.getElementById("categoria-nombre"),
            tipo: document.getElementById("categoria-tipo"),
            error: document.getElementById("error-categoria")
        };
    }

    /** Devuelve todas las categorías en caché. */
    function obtenerTodas() {
        return categorias.slice();
    }

    /** Devuelve las categorías de un tipo concreto ("ingreso" | "gasto"). */
    function obtenerPorTipo(tipo) {
        return categorias.filter(function (categoria) {
            return categoria.tipo === tipo;
        });
    }

    /** Traduce un identificador de categoría a su nombre legible. */
    function nombreDe(idCategoria) {
        var encontrada = categorias.find(function (categoria) {
            return categoria.id_categoria === idCategoria;
        });
        return encontrada ? encontrada.nombre : "Categoría " + idCategoria;
    }

    /** Avisa al resto de módulos de que la caché de categorías cambió. */
    function anunciarCambio() {
        document.dispatchEvent(new CustomEvent("categorias:actualizadas"));
    }

    /**
     * Descarga las categorías del usuario, actualiza la caché y repinta la tabla.
     * No propaga la excepción: el error se refleja en el estado de la sección.
     */
    async function sincronizar() {
        UI.mostrarEstado(nodos.estado, "cargando", "Cargando categorías…");
        nodos.tabla.hidden = true;
        nodos.contador.textContent = "";

        try {
            categorias = await Api.categorias.listar();
            renderizar();
        } catch (error) {
            categorias = [];
            UI.mostrarEstado(nodos.estado, "error", UI.mensajeDeExcepcion(error));
        }

        anunciarCambio();
    }

    /** Pinta la tabla de categorías o el estado vacío correspondiente. */
    function renderizar() {
        UI.vaciar(nodos.cuerpo);

        if (!categorias.length) {
            nodos.tabla.hidden = true;
            nodos.contador.textContent = "";
            UI.mostrarEstado(nodos.estado, "vacio", "No hay categorías registradas todavía.");
            return;
        }

        categorias.forEach(function (categoria) {
            var fila = document.createElement("tr");

            fila.appendChild(UI.crearCelda(String(categoria.id_categoria), "ID", "celda--numerica"));
            fila.appendChild(UI.crearCelda(categoria.nombre, "Nombre"));

            var celdaTipo = UI.crearCelda("", "Tipo");
            celdaTipo.appendChild(UI.crearEtiquetaTipo(categoria.tipo));
            fila.appendChild(celdaTipo);

            nodos.cuerpo.appendChild(fila);
        });

        nodos.contador.textContent = categorias.length === 1
            ? "1 categoría"
            : categorias.length + " categorías";

        UI.ocultarEstado(nodos.estado);
        nodos.tabla.hidden = false;
    }

    /** Alta de categoría contra POST /api/categorias. */
    async function enviarFormulario(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.error);

        var nombre = nodos.nombre.value.trim();
        if (nombre.length < 2) {
            nodos.nombre.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.error, "El nombre de la categoría debe tener al menos 2 caracteres.");
            nodos.nombre.focus();
            return;
        }
        nodos.nombre.removeAttribute("aria-invalid");

        var boton = nodos.formulario.querySelector('button[type="submit"]');
        boton.disabled = true;

        try {
            await Api.categorias.crear({
                nombre: nombre,
                tipo: nodos.tipo.value
            });
            nodos.formulario.reset();
            UI.notificar("Categoría creada correctamente.", "exito");
            await sincronizar();
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.error, UI.mensajeDeExcepcion(error));
        } finally {
            boton.disabled = false;
        }
    }

    function inicializar() {
        capturarNodos();
        nodos.formulario.addEventListener("submit", enviarFormulario);
    }

    App.Categorias = {
        inicializar: inicializar,
        sincronizar: sincronizar,
        obtenerTodas: obtenerTodas,
        obtenerPorTipo: obtenerPorTipo,
        nombreDe: nombreDe
    };
})(window.App);
