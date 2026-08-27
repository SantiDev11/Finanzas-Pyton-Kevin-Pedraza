/**
 * categorias.js — Gestión completa de categorías (CRUD).
 *
 * Endpoints:
 *   GET    /api/categorias
 *   POST   /api/categorias
 *   PUT    /api/categorias/{id}
 *   DELETE /api/categorias/{id}
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
    var idCategoriaEnEdicion = null;
    var idCategoriaPorEliminar = null;

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
            error: document.getElementById("error-categoria"),

            // Diálogo de edición
            dialogoEdicion: document.getElementById("dialogo-categoria"),
            formEdicion: document.getElementById("form-editar-categoria"),
            nombreEdicion: document.getElementById("editar-categoria-nombre"),
            tipoEdicion: document.getElementById("editar-categoria-tipo"),
            errorEdicion: document.getElementById("error-editar-categoria"),
            botonCerrarDialogo: document.getElementById("boton-cerrar-dialogo-categoria"),
            botonCancelarEdicion: document.getElementById("boton-cancelar-categoria"),
            botonGuardarEdicion: document.getElementById("boton-guardar-categoria"),

            // Diálogo de confirmación
            dialogoConfirmar: document.getElementById("dialogo-confirmar"),
            textoConfirmar: document.getElementById("texto-confirmar"),
            botonConfirmarEliminar: document.getElementById("boton-confirmar-eliminar"),
            botonCancelarEliminar: document.getElementById("boton-cancelar-eliminar")
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
            fila.dataset.id = categoria.id_categoria;

            fila.appendChild(UI.crearCelda(String(categoria.id_categoria), "ID", "celda--numerica"));
            fila.appendChild(UI.crearCelda(categoria.nombre, "Nombre"));

            var celdaTipo = UI.crearCelda("", "Tipo");
            celdaTipo.appendChild(UI.crearEtiquetaTipo(categoria.tipo));
            fila.appendChild(celdaTipo);

            // Acciones: Editar y Eliminar
            var celdaAcciones = UI.crearCelda("", "Acciones", "celda--acciones");

            var botonEditar = document.createElement("button");
            botonEditar.type = "button";
            botonEditar.className = "boton boton--secundario boton--pequeno";
            botonEditar.textContent = "Editar";
            botonEditar.dataset.accion = "editar-cat";
            botonEditar.dataset.id = categoria.id_categoria;
            botonEditar.setAttribute("aria-label", "Editar categoría " + categoria.nombre);
            celdaAcciones.appendChild(botonEditar);

            var botonEliminar = document.createElement("button");
            botonEliminar.type = "button";
            botonEliminar.className = "boton boton--peligro-sutil boton--pequeno";
            botonEliminar.textContent = "Eliminar";
            botonEliminar.dataset.accion = "eliminar-cat";
            botonEliminar.dataset.id = categoria.id_categoria;
            botonEliminar.setAttribute("aria-label", "Eliminar categoría " + categoria.nombre);
            celdaAcciones.appendChild(botonEliminar);

            fila.appendChild(celdaAcciones);
            nodos.cuerpo.appendChild(fila);
        });

        nodos.contador.textContent = categorias.length === 1
            ? "1 categoría"
            : categorias.length + " categorías";

        UI.ocultarEstado(nodos.estado);
        nodos.tabla.hidden = false;
    }

    /** Alta de categoría contra POST /api/categorias. */
    async function enviarFormularioAlta(evento) {
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
            await App.refrescarDatosDependientes();
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.error, UI.mensajeDeExcepcion(error));
        } finally {
            boton.disabled = false;
        }
    }

    function abrirDialogoEdicion(categoria) {
        idCategoriaEnEdicion = categoria.id_categoria;
        UI.limpiarErrorFormulario(nodos.errorEdicion);
        nodos.nombreEdicion.value = categoria.nombre;
        nodos.tipoEdicion.value = categoria.tipo;
        UI.abrirDialogo(nodos.dialogoEdicion, nodos.nombreEdicion);
    }

    async function enviarFormularioEdicion(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.errorEdicion);

        var nombre = nodos.nombreEdicion.value.trim();
        if (nombre.length < 2) {
            nodos.nombreEdicion.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorEdicion, "El nombre de la categoría debe tener al menos 2 caracteres.");
            nodos.nombreEdicion.focus();
            return;
        }
        nodos.nombreEdicion.removeAttribute("aria-invalid");

        nodos.botonGuardarEdicion.disabled = true;

        try {
            await Api.categorias.actualizar(idCategoriaEnEdicion, {
                nombre: nombre,
                tipo: nodos.tipoEdicion.value
            });
            UI.cerrarDialogo(nodos.dialogoEdicion);
            UI.notificar("Categoría actualizada correctamente.", "exito");
            await sincronizar();
            await App.refrescarDatosDependientes();
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.errorEdicion, UI.mensajeDeExcepcion(error));
        } finally {
            nodos.botonGuardarEdicion.disabled = false;
        }
    }

    function pedirConfirmacionEliminacion(categoria) {
        idCategoriaPorEliminar = categoria.id_categoria;
        if (nodos.textoConfirmar) {
            nodos.textoConfirmar.textContent =
                "¿Deseas eliminar la categoría '" + categoria.nombre + "' (" + categoria.tipo + ")? " +
                "Solo es posible si no tiene movimientos asociados.";
        }
        UI.abrirDialogo(nodos.dialogoConfirmar, nodos.botonCancelarEliminar);
    }

    async function confirmarEliminacion() {
        if (!idCategoriaPorEliminar) return;

        nodos.botonConfirmarEliminar.disabled = true;
        try {
            await Api.categorias.eliminar(idCategoriaPorEliminar);
            UI.cerrarDialogo(nodos.dialogoConfirmar);
            UI.notificar("Categoría eliminada correctamente.", "exito");
            idCategoriaPorEliminar = null;
            await sincronizar();
            await App.refrescarDatosDependientes();
        } catch (error) {
            UI.notificar(UI.mensajeDeExcepcion(error), "error");
            UI.cerrarDialogo(nodos.dialogoConfirmar);
        } finally {
            nodos.botonConfirmarEliminar.disabled = false;
        }
    }

    function alHacerClickEnTabla(evento) {
        var boton = evento.target.closest("button[data-accion]");
        if (!boton) return;

        var accion = boton.dataset.accion;
        var id = Number(boton.dataset.id);
        var categoria = categorias.find(function (c) { return c.id_categoria === id; });
        if (!categoria) return;

        if (accion === "editar-cat") {
            abrirDialogoEdicion(categoria);
        } else if (accion === "eliminar-cat") {
            pedirConfirmacionEliminacion(categoria);
        }
    }

    function inicializar() {
        capturarNodos();
        if (nodos.formulario) {
            nodos.formulario.addEventListener("submit", enviarFormularioAlta);
        }
        if (nodos.tabla) {
            nodos.tabla.addEventListener("click", alHacerClickEnTabla);
        }
        if (nodos.formEdicion) {
            nodos.formEdicion.addEventListener("submit", enviarFormularioEdicion);
        }
        if (nodos.botonCerrarDialogo) {
            nodos.botonCerrarDialogo.addEventListener("click", function () {
                UI.cerrarDialogo(nodos.dialogoEdicion);
            });
        }
        if (nodos.botonCancelarEdicion) {
            nodos.botonCancelarEdicion.addEventListener("click", function () {
                UI.cerrarDialogo(nodos.dialogoEdicion);
            });
        }
        if (nodos.botonConfirmarEliminar) {
            nodos.botonConfirmarEliminar.addEventListener("click", function (e) {
                if (idCategoriaPorEliminar !== null) {
                    e.stopPropagation();
                    confirmarEliminacion();
                }
            });
        }
    }

    App.Categorias = {
        inicializar: inicializar,
        sincronizar: sincronizar,
        obtenerTodas: obtenerTodas,
        obtenerPorTipo: obtenerPorTipo,
        nombreDe: nombreDe
    };
})(window.App);

