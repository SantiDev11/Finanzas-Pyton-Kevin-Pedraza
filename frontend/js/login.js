/**
 * login.js — Lógica de la pantalla de acceso (index.html).
 *
 * Flujo:
 *   - Iniciar sesión: POST /api/auth/login con correo y contraseña. El backend
 *     verifica la contraseña contra el hash bcrypt y devuelve un JWT.
 *   - Crear cuenta:   POST /api/usuarios y, acto seguido, login automático con
 *     esas mismas credenciales.
 *
 * La contraseña solo existe dentro del formulario y del cuerpo de la petición:
 * no se guarda en el navegador, no se registra en consola y no se conserva
 * después del envío.
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
            ingresoCorreo: document.getElementById("ingreso-correo"),
            ingresoContrasena: document.getElementById("ingreso-contrasena"),
            errorIngreso: document.getElementById("error-ingreso"),
            botonIngresar: document.getElementById("boton-ingresar"),

            formRegistro: document.getElementById("form-registro"),
            registroNombre: document.getElementById("registro-nombre"),
            registroCorreo: document.getElementById("registro-correo"),
            registroContrasena: document.getElementById("registro-contrasena"),
            errorRegistro: document.getElementById("error-registro"),
            botonRegistrar: document.getElementById("boton-registrar")
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
        if (nombre === "ingreso" && nodos.ingresoCorreo) {
            nodos.ingresoCorreo.focus();
        } else if (nombre === "registro" && nodos.registroNombre) {
            nodos.registroNombre.focus();
        }
    }

    /**
     * Guarda la sesión devuelta por el login y navega al panel.
     *
     * El formulario se limpia antes de salir para que la contraseña no quede
     * en el DOM si el usuario vuelve atrás en el historial.
     */
    function entrar(respuestaLogin, formulario) {
        Sesion.guardar(respuestaLogin);
        if (formulario) {
            formulario.reset();
        }
        Sesion.irAlPanel();
    }

    /** Recuerda el último correo usado, para no tener que reescribirlo. */
    function recordarCorreo(correo) {
        try {
            window.localStorage.setItem("finanzas.ultimo_correo", correo);
        } catch (error) {
            /* Modo privado sin persistencia: no es un problema. */
        }
    }

    function correoRecordado() {
        try {
            return window.localStorage.getItem("finanzas.ultimo_correo") || "";
        } catch (error) {
            return "";
        }
    }

    /* ======================================================================
       INICIO DE SESIÓN
       ====================================================================== */

    async function alIniciarSesion(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.errorIngreso);

        var correo = nodos.ingresoCorreo.value.trim();
        var contrasena = nodos.ingresoContrasena.value;

        if (!correo || !correo.includes("@")) {
            nodos.ingresoCorreo.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorIngreso, "Introduce un correo electrónico válido.");
            nodos.ingresoCorreo.focus();
            return;
        }
        nodos.ingresoCorreo.removeAttribute("aria-invalid");

        if (!contrasena) {
            nodos.ingresoContrasena.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorIngreso, "Introduce tu contraseña.");
            nodos.ingresoContrasena.focus();
            return;
        }
        nodos.ingresoContrasena.removeAttribute("aria-invalid");

        nodos.botonIngresar.disabled = true;
        nodos.botonIngresar.textContent = "Verificando…";

        try {
            var respuesta = await Api.auth.iniciarSesion(correo, contrasena);
            recordarCorreo(correo);
            entrar(respuesta, nodos.formIngreso);
        } catch (error) {
            // El backend devuelve el mismo mensaje para correo inexistente y
            // contraseña incorrecta; aquí no se añade ninguna pista adicional.
            nodos.ingresoContrasena.value = "";
            nodos.ingresoCorreo.setAttribute("aria-invalid", "true");
            nodos.ingresoContrasena.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorIngreso, UI.mensajeDeExcepcion(error));
            nodos.botonIngresar.disabled = false;
            nodos.botonIngresar.textContent = "Iniciar sesión";
        }
    }

    /* ======================================================================
       REGISTRO
       ====================================================================== */

    async function alRegistrar(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.errorRegistro);

        var nombre = nodos.registroNombre.value.trim();
        var correo = nodos.registroCorreo.value.trim();
        var contrasena = nodos.registroContrasena.value;

        if (nombre.length < 2) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, "El nombre debe tener al menos 2 caracteres.");
            nodos.registroNombre.focus();
            return;
        }

        if (!correo || !correo.includes("@")) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, "Introduce un correo electrónico válido.");
            nodos.registroCorreo.focus();
            return;
        }

        if (contrasena.length < 8) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, "La contraseña debe tener al menos 8 caracteres.");
            nodos.registroContrasena.focus();
            return;
        }

        nodos.botonRegistrar.disabled = true;
        nodos.botonRegistrar.textContent = "Creando cuenta…";

        try {
            await Api.usuarios.registrar({
                nombre: nombre,
                correo: correo,
                contrasena: contrasena
            });

            // Alta correcta: se inicia sesión con esas mismas credenciales para
            // que el usuario entre directamente, sin escribirlas otra vez.
            var respuesta = await Api.auth.iniciarSesion(correo, contrasena);
            recordarCorreo(correo);
            entrar(respuesta, nodos.formRegistro);
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, UI.mensajeDeExcepcion(error));
            nodos.botonRegistrar.disabled = false;
            nodos.botonRegistrar.textContent = "Crear cuenta y entrar";
        }
    }

    /* ======================================================================
       ARRANQUE
       ====================================================================== */

    /**
     * Si ya hay una sesión válida en esta pestaña, se continúa al panel.
     *
     * El token se valida contra el backend (GET /api/auth/me): tener algo
     * guardado no basta, puede haber caducado.
     */
    async function continuarSiHaySesion() {
        // Aviso heredado del cierre de sesión anterior (por ejemplo, expiración).
        var motivo = Sesion.motivoDeSalida();
        if (motivo) {
            UI.mostrarErrorFormulario(nodos.errorIngreso, motivo);
        }

        if (nodos.ingresoCorreo && !nodos.ingresoCorreo.value) {
            nodos.ingresoCorreo.value = correoRecordado();
        }

        if (Sesion.obtener() === null) {
            return;
        }

        try {
            await Sesion.verificar();
            Sesion.irAlPanel();
        } catch (error) {
            Sesion.borrar();
            if (!motivo) {
                UI.mostrarErrorFormulario(
                    nodos.errorIngreso,
                    "La sesión anterior expiró o ya no es válida. Vuelve a iniciar sesión."
                );
            }
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
