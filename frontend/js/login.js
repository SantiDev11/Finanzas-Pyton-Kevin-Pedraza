/**
 * login.js — Lógica de la pantalla de acceso (index.html).
 *
 * Flujo:
 *   - Iniciar sesión: acepta identificador de usuario (ID) o correo electrónico
 *     asociado a la cuenta, valida existencia contra MySQL y establece la sesión.
 *   - Crear cuenta:   POST /api/usuarios (la API cifra con bcrypt en backend).
 *
 * En ambos casos, al validar se guarda la sesión y se redirige al panel.
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
        if (nombre === "ingreso" && nodos.ingresoId) {
            nodos.ingresoId.focus();
        } else if (nombre === "registro" && nodos.registroNombre) {
            nodos.registroNombre.focus();
        }
    }

    /** Guarda la sesión y navega al panel financiero. */
    function entrar(idUsuario) {
        Sesion.guardar(idUsuario);
        Sesion.irAlPanel();
    }

    /** Guarda la asociación de correo a idUsuario en el navegador */
    function recordarUsuario(correo, idUsuario) {
        try {
            if (correo) {
                window.localStorage.setItem("finanzas.correo." + correo.toLowerCase().trim(), String(idUsuario));
            }
            window.localStorage.setItem("finanzas.ultimo_id", String(idUsuario));
        } catch (e) {
            /* Modo privado sin persistencia */
        }
    }

    /** Busca el ID de usuario a partir del valor ingresado (número o correo guardado) */
    function resolverIdentificador(valor) {
        var texto = (valor || "").trim();
        if (!texto) {
            return null;
        }

        // Si es un número entero directo
        var idNumerico = Number(texto);
        if (Number.isInteger(idNumerico) && idNumerico > 0) {
            return idNumerico;
        }

        // Si es un correo, buscar en la asociación local del navegador
        try {
            var idGuardado = window.localStorage.getItem("finanzas.correo." + texto.toLowerCase());
            if (idGuardado) {
                var parseado = Number(idGuardado);
                if (Number.isInteger(parseado) && parseado > 0) {
                    return parseado;
                }
            }
        } catch (e) {
            // Ignorar error de almacenamiento
        }

        return null;
    }

    async function alIniciarSesion(evento) {
        evento.preventDefault();
        UI.limpiarErrorFormulario(nodos.errorIngreso);

        var valorEntrada = nodos.ingresoId.value.trim();
        var idUsuario = resolverIdentificador(valorEntrada);

        if (!valorEntrada) {
            nodos.ingresoId.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorIngreso, "Por favor ingresa tu identificador de usuario (ID) o correo electrónico.");
            nodos.ingresoId.focus();
            return;
        }

        if (idUsuario === null) {
            // Si introdujo un correo que no está mapeado aún localmente
            if (valorEntrada.includes("@")) {
                nodos.ingresoId.setAttribute("aria-invalid", "true");
                UI.mostrarErrorFormulario(
                    nodos.errorIngreso,
                    "El backend actual valida usuarios mediante identificador numérico (ID). Si es tu primera vez en este navegador, ingresa tu ID numérico (ej: 1) o crea una nueva cuenta en la pestaña 'Crear cuenta'."
                );
            } else {
                nodos.ingresoId.setAttribute("aria-invalid", "true");
                UI.mostrarErrorFormulario(nodos.errorIngreso, "Introduce un identificador de usuario válido (número entero positivo).");
            }
            nodos.ingresoId.focus();
            return;
        }

        nodos.ingresoId.removeAttribute("aria-invalid");
        nodos.botonIngresar.disabled = true;

        try {
            await Sesion.verificarUsuario(idUsuario);
            recordarUsuario(valorEntrada.includes("@") ? valorEntrada : null, idUsuario);
            entrar(idUsuario);
        } catch (error) {
            nodos.ingresoId.setAttribute("aria-invalid", "true");
            UI.mostrarErrorFormulario(nodos.errorIngreso, UI.mensajeDeExcepcion(error));
            nodos.botonIngresar.disabled = false;
        }
    }

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

        try {
            var usuario = await Api.usuarios.registrar({
                nombre: nombre,
                correo: correo,
                contrasena: contrasena
            });
            recordarUsuario(correo, usuario.id_usuario);
            nodos.formRegistro.reset();
            entrar(usuario.id_usuario);
        } catch (error) {
            UI.mostrarErrorFormulario(nodos.errorRegistro, UI.mensajeDeExcepcion(error));
            nodos.botonRegistrar.disabled = false;
        }
    }

    /**
     * Si ya había una sesión válida en esta pestaña, se continúa al panel.
     */
    async function continuarSiHaySesion() {
        var guardado = Sesion.obtener();
        if (guardado === null) {
            // Sugerir el último ID si existe
            try {
                var ultimoId = window.localStorage.getItem("finanzas.ultimo_id");
                if (ultimoId && nodos.ingresoId && !nodos.ingresoId.value) {
                    nodos.ingresoId.value = ultimoId;
                }
            } catch (e) { }
            return;
        }
        try {
            await Sesion.verificarUsuario(guardado);
            Sesion.irAlPanel();
        } catch (error) {
            Sesion.borrar();
            UI.mostrarErrorFormulario(nodos.errorIngreso, "La sesión anterior expiró o ya no es válida.");
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
