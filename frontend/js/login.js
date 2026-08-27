/**
 * login.js — Lógica de la página de acceso (index.html).
 *
 * Dos formularios sobre los endpoints que la API ya expone:
 *   - Iniciar sesión: valida contra MySQL que el identificador exista.
 *   - Crear cuenta:   POST /api/usuarios (la API cifra con bcrypt).
 *
 * En ambos casos, al terminar se guarda la sesión y se redirige al panel.
 * Este archivo no se carga en dashboard.html.
 */
(function (App) {
    "use strict";

    var Api = App.Api;
    var UI = App.UI;
    var Sesion = App.Sesion;

    var nodos = {};

    function capturarNodos() {
        nodos = {
            pestanas: Array.prototype.slice.call(document.querySelectorAll(".pestanas__boton")),
            paneles: Array.prototype.slice.call(document.querySelectorAll(".acceso__panel")),

            formIngreso: document.getElementById("form-ingreso"),
            ingresoId: document.getElementById("ingreso-id"),
            errorIngreso: document.getElementById("error-ingreso"),
            botonIngresar: document.getElementById("boton-ingresar"),

            formRegistro: document.getElementById("form-registro"),
            registroNombre: document.getElementById("registro-nombre"),
            registroCorreo: document.getElementById("registro-correo"),
            registroContrasena: document.getElementById("registro-contrasena"),
            errorRegistro: document.getElementById("error-registro")
        };
    }

    /** Alterna entre el panel de inicio de sesión y el de registro. */
    function cambiarPanel(nombre) {
        nodos.paneles.forEach(function (panel) {
            panel.hidden = panel.id !== "panel-" + nombre;
        });
        nodos.pestanas.forEach(function (pestana) {
            if (pestana.dataset.panel === nombre) {
                pestana.setAttribute("aria-current", "page");
            } else {
                pestana.removeAttribute("aria-current");
            }
        });
    }

    /** Guarda la sesión y salta al panel. */
    function entrar(idUsuario) {
        Sesion.guardar(idUsuario);
        Sesion.irAlPanel();
    }

    async function alIniciarSesion(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.errorIngreso);

        var identificador = Number(nodos.ingresoId.value);
        if (!Number.isInteger(identificador) || identificador <= 0) {
            nodos.ingresoId.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorIngreso,
                "Introduce un identificador de usuario válido (número entero mayor que cero).");
            nodos.ingresoId.focus();
            return;
        }
        nodos.ingresoId.removeAttribute("aria-invalid");

        nodos.botonIngresar.disabled = true;
        try {
            await Sesion.verificarUsuario(identificador);
            entrar(identificador);
        } catch (error) {
            nodos.ingresoId.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorIngreso, UI.mensajeDeExcepcion(error));
            nodos.botonIngresar.disabled = false;
        }
    }

    async function alRegistrar(evento) {
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
            entrar(usuario.id_usuario);
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, UI.mensajeDeExcepcion(error));
            boton.disabled = false;
        }
    }

    /**
     * Si al abrir el acceso ya había una sesión válida en esta pestaña, se
     * continúa directamente al panel. Si el usuario guardado ya no existe, la
     * sesión se descarta y se muestra el formulario: así nunca se produce un
     * rebote infinito entre las dos páginas.
     */
    async function continuarSiHaySesion() {
        var guardado = Sesion.obtener();
        if (guardado === null) {
            return;
        }
        try {
            await Sesion.verificarUsuario(guardado);
            Sesion.irAlPanel();
        } catch (error) {
            Sesion.borrar();
            UI.mostrarErrorFormulario(nodos.errorIngreso,
                "La sesión anterior ya no es válida. Vuelve a identificarte.");
        }
    }

    function iniciar() {
        capturarNodos();

        nodos.formIngreso.addEventListener("submit", alIniciarSesion);
        nodos.formRegistro.addEventListener("submit", alRegistrar);
        nodos.pestanas.forEach(function (pestana) {
            pestana.addEventListener("click", function () {
                cambiarPanel(pestana.dataset.panel);
            });
        });

        return continuarSiHaySesion();
    }

    document.addEventListener("DOMContentLoaded", iniciar);
})(window.App);
