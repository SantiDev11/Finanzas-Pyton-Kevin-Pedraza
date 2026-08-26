/**
 * app.js — Arranque, usuario activo y navegación entre vistas.
 *
 * El backend no tiene sesiones ni autenticación: cada endpoint identifica al
 * propietario de los datos mediante el parámetro id_usuario. El frontend
 * respeta ese mecanismo tal cual — guarda únicamente el identificador activo
 * en localStorage — y no implementa ningún inicio de sesión ni token. La
 * contraseña del formulario de registro se envía a POST /api/usuarios y no se
 * almacena en ningún momento en el navegador.
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var UI = App.UI;
    var CONFIG = App.CONFIG;

    /** Identificador de usuario sobre el que trabaja toda la aplicación. */
    var idUsuario = CONFIG.ID_USUARIO_POR_DEFECTO;

    /** Vista visible en este momento. */
    var vistaActiva = "panel";

    /** Cargador de datos asociado a cada vista. */
    var CARGADORES = {
        panel: function () { return App.Dashboard.cargar(idUsuario); },
        movimientos: function () { return App.Movimientos.cargar(idUsuario); },
        categorias: function () { return App.Categorias.sincronizar(idUsuario); },
        analisis: function () { return App.Analytics.cargar(idUsuario); }
    };

    var nodos = {};

    function capturarNodos() {
        nodos = {
            formUsuario: document.getElementById("form-usuario"),
            entradaUsuario: document.getElementById("entrada-usuario"),
            enlaces: Array.prototype.slice.call(document.querySelectorAll(".navegacion__enlace")),
            vistas: Array.prototype.slice.call(document.querySelectorAll(".vista")),

            dialogoRegistro: document.getElementById("dialogo-usuario"),
            formRegistro: document.getElementById("form-registro"),
            registroNombre: document.getElementById("registro-nombre"),
            registroCorreo: document.getElementById("registro-correo"),
            registroContrasena: document.getElementById("registro-contrasena"),
            errorRegistro: document.getElementById("error-registro"),
            botonAbrirRegistro: document.getElementById("boton-abrir-registro"),
            botonCerrarRegistro: document.getElementById("boton-cerrar-registro"),
            botonCancelarRegistro: document.getElementById("boton-cancelar-registro")
        };
    }

    /* ======================================================================
       USUARIO ACTIVO
       ====================================================================== */

    function usuarioActivo() {
        return idUsuario;
    }

    /** Recupera el usuario guardado en la sesión anterior, si lo hubiera. */
    function recuperarUsuarioGuardado() {
        var guardado = Number(window.localStorage.getItem(CONFIG.CLAVE_USUARIO));
        if (Number.isInteger(guardado) && guardado > 0) {
            idUsuario = guardado;
        }
        nodos.entradaUsuario.value = String(idUsuario);
    }

    /** Fija el usuario activo, lo persiste y recarga todos los datos. */
    async function establecerUsuario(nuevoId) {
        idUsuario = nuevoId;
        nodos.entradaUsuario.value = String(nuevoId);
        window.localStorage.setItem(CONFIG.CLAVE_USUARIO, String(nuevoId));
        await recargarTodo();
    }

    function alCambiarUsuario(evento) {
        evento.preventDefault();
        var valor = Number(nodos.entradaUsuario.value);

        if (!Number.isInteger(valor) || valor <= 0) {
            nodos.entradaUsuario.setAttribute("aria-invalid", "true");
            UI.notificar("El identificador de usuario debe ser un número entero mayor que cero.", "error");
            return;
        }

        nodos.entradaUsuario.removeAttribute("aria-invalid");
        establecerUsuario(valor);
    }

    /* ======================================================================
       REGISTRO DE USUARIO (POST /api/usuarios)
       ====================================================================== */

    async function registrarUsuario(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.errorRegistro);

        var boton = nodos.formRegistro.querySelector('button[type="submit"]');
        boton.disabled = true;

        try {
            var usuario = await Api.usuarios.registrar({
                nombre: nodos.registroNombre.value.trim(),
                correo: nodos.registroCorreo.value.trim(),
                contrasena: nodos.registroContrasena.value
            });

            nodos.formRegistro.reset();
            UI.cerrarDialogo(nodos.dialogoRegistro);
            UI.notificar("Usuario registrado con el identificador " + usuario.id_usuario + ".", "exito");
            await establecerUsuario(usuario.id_usuario);
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, UI.mensajeDeExcepcion(error));
        } finally {
            boton.disabled = false;
        }
    }

    /* ======================================================================
       NAVEGACIÓN
       ====================================================================== */

    /** Muestra una vista, actualiza la navegación y carga sus datos. */
    function cambiarVista(nombre) {
        vistaActiva = nombre;

        nodos.vistas.forEach(function (vista) {
            vista.hidden = vista.id !== "vista-" + nombre;
        });

        nodos.enlaces.forEach(function (enlace) {
            if (enlace.dataset.vista === nombre) {
                enlace.setAttribute("aria-current", "page");
            } else {
                enlace.removeAttribute("aria-current");
            }
        });

        return CARGADORES[nombre]();
    }

    /** Recarga las categorías (caché compartida) y la vista visible. */
    async function recargarTodo() {
        await App.Categorias.sincronizar(idUsuario);
        if (vistaActiva !== "categorias") {
            await CARGADORES[vistaActiva]();
        }
    }

    /**
     * Refresco tras crear, editar o eliminar un movimiento: la vista visible
     * vuelve a pedir sus datos al backend, que es la fuente de verdad.
     */
    function refrescarDatosDependientes() {
        return CARGADORES[vistaActiva]();
    }

    /* ======================================================================
       ARRANQUE
       ====================================================================== */

    function registrarEventos() {
        nodos.formUsuario.addEventListener("submit", alCambiarUsuario);

        nodos.enlaces.forEach(function (enlace) {
            enlace.addEventListener("click", function () {
                cambiarVista(enlace.dataset.vista);
            });
        });

        nodos.botonAbrirRegistro.addEventListener("click", function () {
            UI.limpiarErrorFormulario(nodos.errorRegistro);
            UI.abrirDialogo(nodos.dialogoRegistro, nodos.registroNombre);
        });
        nodos.botonCerrarRegistro.addEventListener("click", function () {
            UI.cerrarDialogo(nodos.dialogoRegistro);
        });
        nodos.botonCancelarRegistro.addEventListener("click", function () {
            UI.cerrarDialogo(nodos.dialogoRegistro);
        });
        nodos.formRegistro.addEventListener("submit", registrarUsuario);
    }

    async function iniciar() {
        capturarNodos();
        registrarEventos();

        App.Categorias.inicializar();
        App.Resumen.inicializar();
        App.Movimientos.inicializar();
        App.Analytics.inicializar();
        App.Dashboard.inicializar();

        recuperarUsuarioGuardado();
        await recargarTodo();
    }

    App.usuarioActivo = usuarioActivo;
    App.refrescarDatosDependientes = refrescarDatosDependientes;
    App.cambiarVista = cambiarVista;

    document.addEventListener("DOMContentLoaded", iniciar);
})(window.App);
