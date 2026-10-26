"""Chatbot de CENIGRAF con interfaz adaptable, historial local y API FastAPI."""

from typing import Dict, List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from iagenerativa import generar_respuesta

app = FastAPI(title="Bienvenido a CeniBot", version="2.1.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: List[Dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str


HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#123c69">
    <title>Bienvenido a CeniBot</title>
    <style>
        :root {
            --azul: #123c69;
            --azul-oscuro: #0a2949;
            --azul-claro: #eaf2fb;
            --turquesa: #0f8b8d;
            --fondo: #f3f6fb;
            --texto: #1d2939;
            --suave: #667085;
            --borde: #dce4ee;
            --blanco: #ffffff;
            --sidebar: #f8fafc;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            padding: 26px 20px;
            min-height: 100vh;
            background: radial-gradient(circle at top left, #e2eefb 0, var(--fondo) 42%, #f8fafc 100%);
            color: var(--texto);
            font-family: Inter, "Segoe UI", Arial, sans-serif;
        }

        button, input { font: inherit; }
        button { cursor: pointer; }
        button:focus-visible, input:focus-visible {
            outline: 3px solid #80b7f0;
            outline-offset: 2px;
        }
        button:disabled { opacity: .6; cursor: wait; }

        .contenedor {
            width: 100%;
            max-width: 900px;
            margin: 0 auto;
        }

        .encabezado {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 20px 24px;
            color: white;
            background: linear-gradient(120deg, var(--azul-oscuro), var(--azul));
            border-radius: 20px 20px 0 0;
            box-shadow: 0 10px 28px rgba(18, 60, 105, .16);
        }

        .logo {
            display: grid;
            place-items: center;
            flex: 0 0 52px;
            height: 52px;
            border-radius: 16px;
            background: rgba(255,255,255,.14);
            font-size: 18px;
            font-weight: 800;
            letter-spacing: .5px;
            border: 1px solid rgba(255,255,255,.25);
        }

        .encabezado h1 { margin: 0 0 4px; font-size: 1.25rem; }
        .encabezado p { margin: 0; color: #dce9f7; font-size: .92rem; }
        .estado {
            margin-left: auto;
            display: flex;
            align-items: center;
            gap: 7px;
            font-size: .8rem;
            white-space: nowrap;
            color: #e2f8ee;
        }
        .punto { width: 8px; height: 8px; background: #5ee0a0; border-radius: 50%; }

        .panel {
            background: var(--blanco);
            border: 1px solid var(--borde);
            border-top: 0;
            border-radius: 0 0 20px 20px;
            overflow: hidden;
            box-shadow: 0 16px 36px rgba(16, 39, 70, .09);
        }
        .contenido { padding: 22px; }
        .intro { margin: 0 0 16px; color: var(--suave); line-height: 1.5; font-size: .95rem; }
        .seccion-titulo { margin: 0 0 10px; font-size: .91rem; color: var(--azul-oscuro); font-weight: 750; }
        .preguntas { display: flex; flex-wrap: wrap; gap: 9px; margin-bottom: 18px; }
        .pregunta {
            border: 1px solid #c9d8ea;
            border-radius: 999px;
            background: #f7faff;
            color: var(--azul);
            padding: 9px 13px;
            font-size: .86rem;
            line-height: 1.3;
            transition: background .15s, transform .15s;
        }
        .pregunta:hover:not(:disabled) { background: var(--azul-claro); transform: translateY(-1px); }

        .chat {
            height: min(43vh, 390px);
            min-height: 260px;
            overflow-y: auto;
            padding: 16px;
            border: 1px solid var(--borde);
            border-radius: 15px;
            background: #f8fafc;
            scroll-behavior: smooth;
        }
        .mensaje { display: flex; margin: 0 0 14px; }
        .mensaje:last-child { margin-bottom: 0; }
        .burbuja {
            max-width: 85%;
            padding: 11px 14px;
            border-radius: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            font-size: .95rem;
        }
        .mensaje.asistente { justify-content: flex-start; }
        .mensaje.asistente .burbuja {
            background: white;
            border: 1px solid var(--borde);
            border-top-left-radius: 5px;
        }
        .mensaje.usuario { justify-content: flex-end; }
        .mensaje.usuario .burbuja {
            color: white;
            background: var(--azul);
            border-top-right-radius: 5px;
        }
        .mensaje.sistema .burbuja {
            max-width: 100%;
            color: #8a4b08;
            background: #fff7e8;
            border: 1px solid #f4d59b;
            font-size: .88rem;
        }

        .escribiendo {
            display: none;
            margin: 12px 0 0;
            color: var(--suave);
            font-size: .88rem;
            align-items: center;
            gap: 9px;
        }
        .escribiendo.visible { display: flex; }
        .puntos { display: inline-flex; gap: 4px; }
        .puntos span {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--turquesa);
            animation: subir 1s infinite ease-in-out;
        }
        .puntos span:nth-child(2) { animation-delay: .15s; }
        .puntos span:nth-child(3) { animation-delay: .3s; }
        @keyframes subir {
            0%, 60%, 100% { transform: translateY(0); opacity: .45; }
            30% { transform: translateY(-4px); opacity: 1; }
        }

        .formulario { display: flex; gap: 10px; margin-top: 14px; }
        .entrada {
            flex: 1;
            min-width: 0;
            padding: 13px 15px;
            border: 1px solid #bdc9d8;
            border-radius: 12px;
            color: var(--texto);
            background: white;
        }
        .boton {
            border: 0;
            border-radius: 12px;
            padding: 12px 17px;
            font-weight: 700;
            transition: background .15s;
        }
        .enviar { background: var(--turquesa); color: white; }
        .enviar:hover:not(:disabled) { background: #0b7375; }
        .acciones {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            margin-top: 14px;
        }
        .ayuda { color: var(--suave); font-size: .8rem; line-height: 1.4; }
        .limpiar { background: white; color: var(--azul); border: 1px solid #c9d8ea; padding: 9px 13px; }
        .limpiar:hover:not(:disabled) { background: var(--azul-claro); }
        .pie { text-align: center; color: var(--suave); font-size: .78rem; padding: 14px 10px 2px; }

        /* Barra lateral de conversaciones */
        #panel-historial {
            position: fixed;
            inset: 0 auto 0 0;
            width: 285px;
            padding: 22px 16px;
            overflow-y: auto;
            background: var(--sidebar);
            border-right: 1px solid var(--borde);
            box-shadow: 4px 0 18px rgba(20, 40, 70, .08);
            z-index: 1002;
            transform: translateX(-105%);
            transition: transform .22s ease;
        }
        #panel-historial.abierto { transform: translateX(0); }
        .encabezado-historial {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .encabezado-historial h2 { color: var(--azul-oscuro); font-size: 1rem; margin: 0; }
        .boton-icono {
            width: 34px;
            height: 34px;
            display: grid;
            place-items: center;
            border: 1px solid var(--borde);
            border-radius: 9px;
            color: var(--texto);
            background: white;
        }
        #nuevo-chat {
            width: 100%;
            margin-bottom: 19px;
            text-align: left;
            background: var(--azul);
            color: white;
            border-radius: 11px;
            padding: 12px 14px;
        }
        #nuevo-chat:hover { background: var(--azul-oscuro); }
        .historial-etiqueta {
            margin: 0 0 9px 4px;
            color: var(--suave);
            text-transform: uppercase;
            letter-spacing: .06em;
            font-size: .7rem;
            font-weight: 800;
        }
        #lista-historial { display: flex; flex-direction: column; gap: 6px; }
        .item-historial {
            width: 100%;
            padding: 11px 12px;
            border: 1px solid transparent;
            border-radius: 10px;
            background: transparent;
            color: #26364a;
            text-align: left;
            line-height: 1.35;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            cursor: pointer;
        }
        .item-historial:hover, .item-historial.activa {
            background: #e7efff;
            border-color: #cbdafa;
        }
        .historial-vacio { padding: 8px 5px; color: var(--suave); font-size: .85rem; line-height: 1.45; }
        #abrir-historial {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            position: fixed;
            top: 12px;
            left: 12px;
            z-index: 1003;
            border: 1px solid var(--borde);
            border-radius: 10px;
            padding: 10px 13px;
            background: white;
            color: var(--azul);
            box-shadow: 0 4px 14px rgba(20, 40, 70, .09);
            font-weight: 700;
        }
        .sombra-historial {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 30, 50, .35);
            z-index: 1001;
        }
        .sombra-historial.visible { display: block; }

        @media (min-width: 900px) {
            body { padding: 26px 26px 26px 315px; }
            .contenedor { max-width: 900px; }
            #panel-historial { transform: translateX(0); }
            #abrir-historial, #cerrar-historial, .sombra-historial { display: none !important; }
        }
        @media (max-width: 620px) {
            body { padding: 66px 10px 12px; }
            .encabezado { padding: 16px; gap: 11px; border-radius: 16px 16px 0 0; }
            .logo { flex-basis: 44px; height: 44px; border-radius: 13px; font-size: 15px; }
            .encabezado h1 { font-size: 1.05rem; }
            .encabezado p { font-size: .8rem; }
            .estado { display: none; }
            .panel { border-radius: 0 0 16px 16px; }
            .contenido { padding: 14px; }
            .preguntas { display: grid; grid-template-columns: 1fr; gap: 8px; }
            .pregunta { width: 100%; border-radius: 10px; text-align: left; padding: 11px 12px; }
            .chat { height: 42vh; min-height: 250px; padding: 12px; }
            .burbuja { max-width: 93%; font-size: .9rem; }
            .formulario { gap: 7px; }
            .entrada { padding: 12px 10px; font-size: 16px; }
            .boton { padding: 11px 12px; }
            .acciones { align-items: flex-start; flex-direction: column-reverse; }
            .limpiar { align-self: flex-end; }
            .ayuda { font-size: .76rem; }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: .01ms !important;
                transition-duration: .01ms !important;
                scroll-behavior: auto !important;
            }
        }
    </style>
</head>
<body>
    <button id="abrir-historial" type="button" aria-label="Abrir historial">☰ Historial</button>
    <div id="sombra-historial" class="sombra-historial"></div>

    <aside id="panel-historial" aria-label="Historial de conversaciones">
        <div class="encabezado-historial">
            <h2>Mis conversaciones</h2>
            <button id="cerrar-historial" class="boton-icono" type="button" aria-label="Cerrar historial">×</button>
        </div>
        <button id="nuevo-chat" class="boton" type="button">＋ Nuevo chat</button>
        <p class="historial-etiqueta">Recientes</p>
        <div id="lista-historial"></div>
    </aside>

    <main class="contenedor">
        <header class="encabezado">
            <div class="logo" aria-hidden="true">CB</div>
            <div>
                <h1>Asistente virtual CeniBot</h1>
                <p>Información sobre formación y oferta educativa</p>
            </div>
            <div class="estado"><span class="punto"></span> Disponible</div>
        </header>

        <section class="panel" aria-label="Conversación con el asistente">
            <div class="contenido">
                <p class="intro">¡Hola! Bienvenido a CeniBot. Selecciona una pregunta frecuente o escribe tu consulta.</p>
                <h2 class="seccion-titulo">Preguntas frecuentes</h2>
                <div class="preguntas" id="preguntas">
                    <button type="button" class="pregunta">¿Qué programas de formación ofrece CENIGRAF?</button>
                    <button type="button" class="pregunta">¿Qué tipos de formación existen?</button>
                    <button type="button" class="pregunta">¿Cuáles son los requisitos de inscripción?</button>
                    <button type="button" class="pregunta">¿Cómo consulto las fechas de inscripción?</button>
                    <button type="button" class="pregunta">¿Cuál es la diferencia entre técnico y tecnólogo?</button>
                </div>

                <div class="fila-conversacion" style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px;">
                    <h2 class="seccion-titulo" style="margin:0;">Conversación</h2>
                    <button class="boton limpiar" id="limpiar" type="button">Limpiar chat</button>
                </div>

                <div class="chat" id="chat" role="log" aria-live="polite" aria-relevant="additions text"></div>
                <div id="escribiendo" class="escribiendo" role="status" aria-live="polite" aria-hidden="true">
                    <span class="puntos" aria-hidden="true"><span></span><span></span><span></span></span>
                    CeniBot está escribiendo…
                </div>

                <form class="formulario" id="formulario">
                    <input class="entrada" id="mensaje" name="mensaje" type="text" placeholder="Escribe tu pregunta…" maxlength="2000" autocomplete="off" aria-label="Escribe tu pregunta">
                    <button class="boton enviar" id="enviar" type="submit">Enviar</button>
                </form>
                <div class="acciones">
                    <span class="ayuda">Las respuestas dependen de la información institucional disponible.</span>
                </div>
            </div>
        </section>
        <footer class="pie">CeniBot · Asistente informativo</footer>
    </main>

    <script>
    "use strict";

    const chat = document.getElementById("chat");
    const formulario = document.getElementById("formulario");
    const entrada = document.getElementById("mensaje");
    const botonEnviar = document.getElementById("enviar");
    const botonLimpiar = document.getElementById("limpiar");
    const indicadorEscribiendo = document.getElementById("escribiendo");
    const listaHistorial = document.getElementById("lista-historial");
    const panelHistorial = document.getElementById("panel-historial");
    const sombraHistorial = document.getElementById("sombra-historial");

    const CLAVE_CONVERSACIONES = "conversaciones_cenibot_v1";
    const CLAVE_ACTIVA = "conversacion_activa_cenibot_v1";
    const CLAVE_ANTERIOR = "historial_chat_cenigraf";
    const MENSAJE_BIENVENIDA = "¡Hola! Bienvenido a CeniBot. Selecciona una pregunta frecuente o escribe tu consulta.";

    function crearId() {
        return Date.now().toString(36) + Math.random().toString(36).slice(2, 9);
    }

    function crearTitulo(texto) {
        const titulo = String(texto || "").replace(/\s+/g, " ").trim();
        return titulo.length > 38 ? titulo.slice(0, 38).trim() + "…" : (titulo || "Nuevo chat");
    }

    function cargarConversaciones() {
        try {
            const datos = JSON.parse(localStorage.getItem(CLAVE_CONVERSACIONES) || "[]");
            if (!Array.isArray(datos)) return [];
            return datos.filter(function(c) {
                return c && typeof c.id === "string" && Array.isArray(c.mensajes);
            });
        } catch (error) {
            console.warn("No se pudo leer el historial guardado.", error);
            return [];
        }
    }

    let conversaciones = cargarConversaciones();

    // Migra la conversación guardada por la versión anterior del historial.
    if (conversaciones.length === 0) {
        try {
            const anterior = JSON.parse(localStorage.getItem(CLAVE_ANTERIOR) || "[]");
            if (Array.isArray(anterior) && anterior.length > 0) {
                const mensajesAnteriores = anterior
                    .filter(function(m) {
                        return m && typeof m.remitente === "string" && typeof m.texto === "string";
                    })
                    .map(function(m) {
                        return { remitente: m.remitente, texto: m.texto };
                    });

                if (mensajesAnteriores.length > 0) {
                    const primero = mensajesAnteriores.find(function(m) { return m.remitente === "Tú"; });
                    const fecha = new Date().toISOString();
                    conversaciones.push({
                        id: crearId(),
                        titulo: crearTitulo(primero ? primero.texto : "Conversación anterior"),
                        mensajes: mensajesAnteriores,
                        creada: fecha,
                        actualizada: fecha
                    });
                }
            }
        } catch (error) {
            console.warn("No se pudo migrar el historial anterior.", error);
        }
    }

    let conversacionActivaId = localStorage.getItem(CLAVE_ACTIVA);
    if (!conversaciones.some(function(c) { return c.id === conversacionActivaId; })) {
        conversacionActivaId = conversaciones.length ? conversaciones[0].id : null;
    }

    function obtenerActiva() {
        return conversaciones.find(function(c) { return c.id === conversacionActivaId; }) || null;
    }

    function guardarEstado() {
        try {
            localStorage.setItem(CLAVE_CONVERSACIONES, JSON.stringify(conversaciones));
            if (conversacionActivaId) {
                localStorage.setItem(CLAVE_ACTIVA, conversacionActivaId);
            } else {
                localStorage.removeItem(CLAVE_ACTIVA);
            }
        } catch (error) {
            console.error("No se pudo guardar el historial en este navegador.", error);
        }
    }

    function crearBurbuja(remitente, texto) {
        const fila = document.createElement("div");
        fila.className = "mensaje";
        if (remitente === "Tú") {
            fila.classList.add("usuario");
        } else if (remitente === "Sistema") {
            fila.classList.add("sistema");
        } else {
            fila.classList.add("asistente");
        }

        const burbuja = document.createElement("div");
        burbuja.className = "burbuja";
        burbuja.textContent = texto;
        fila.appendChild(burbuja);
        return fila;
    }

    function mostrarMensajes() {
        chat.innerHTML = "";
        const conversacion = obtenerActiva();

        if (!conversacion || conversacion.mensajes.length === 0) {
            chat.appendChild(crearBurbuja("Bot", MENSAJE_BIENVENIDA));
        } else {
            conversacion.mensajes.forEach(function(mensaje) {
                chat.appendChild(crearBurbuja(mensaje.remitente, mensaje.texto));
            });
        }
        chat.scrollTop = chat.scrollHeight;
    }

    function mostrarHistorial() {
        listaHistorial.innerHTML = "";
        const ordenadas = conversaciones.slice().sort(function(a, b) {
            return new Date(b.actualizada || b.creada) - new Date(a.actualizada || a.creada);
        });

        if (ordenadas.length === 0) {
            const vacio = document.createElement("p");
            vacio.className = "historial-vacio";
            vacio.textContent = "Tus conversaciones nuevas aparecerán aquí.";
            listaHistorial.appendChild(vacio);
            return;
        }

        ordenadas.forEach(function(conversacion) {
            const boton = document.createElement("button");
            boton.type = "button";
            boton.className = "item-historial";
            if (conversacion.id === conversacionActivaId) boton.classList.add("activa");
            boton.textContent = conversacion.titulo || "Nuevo chat";
            boton.title = boton.textContent;
            boton.addEventListener("click", function() {
                conversacionActivaId = conversacion.id;
                guardarEstado();
                mostrarHistorial();
                mostrarMensajes();
                cerrarPanel();
            });
            listaHistorial.appendChild(boton);
        });
    }

    function refrescarInterfaz() {
        guardarEstado();
        mostrarHistorial();
        mostrarMensajes();
    }

    function nuevaConversacion(cerrar = false) {
        const fecha = new Date().toISOString();
        const conversacion = {
            id: crearId(),
            titulo: "Nuevo chat",
            mensajes: [],
            creada: fecha,
            actualizada: fecha
        };
        conversaciones.push(conversacion);
        conversacionActivaId = conversacion.id;
        refrescarInterfaz();
        if (cerrar) cerrarPanel();
        entrada.focus();
    }

    function agregarMensaje(remitente, texto) {
        let conversacion = obtenerActiva();
        if (!conversacion) {
            nuevaConversacion();
            conversacion = obtenerActiva();
        }
        if (remitente === "Tú" && conversacion.titulo === "Nuevo chat") {
            conversacion.titulo = crearTitulo(texto);
        }
        conversacion.mensajes.push({ remitente: remitente, texto: texto });
        conversacion.actualizada = new Date().toISOString();
        refrescarInterfaz();
    }

    function abrirPanel() {
        panelHistorial.classList.add("abierto");
        sombraHistorial.classList.add("visible");
    }

    function cerrarPanel() {
        panelHistorial.classList.remove("abierto");
        sombraHistorial.classList.remove("visible");
    }

    function mostrarEscribiendo(mostrar) {
        indicadorEscribiendo.classList.toggle("visible", mostrar);
        indicadorEscribiendo.setAttribute("aria-hidden", mostrar ? "false" : "true");
        if (mostrar) chat.scrollTop = chat.scrollHeight;
    }

    async function enviarPregunta(texto) {
        const mensaje = String(texto || "").trim();
        if (!mensaje || botonEnviar.disabled) return;

        agregarMensaje("Tú", mensaje);
        entrada.value = "";
        botonEnviar.disabled = true;
        mostrarEscribiendo(true);

        try {
            const respuesta = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: mensaje })
            });

            const datos = await respuesta.json();
            if (!respuesta.ok) {
                throw new Error(datos.detail || "No se pudo obtener una respuesta.");
            }
            agregarMensaje("Bot", datos.reply || "No se recibió una respuesta.");
        } catch (error) {
            agregarMensaje("Sistema", "No se pudo obtener una respuesta. Comprueba la conexión e inténtalo de nuevo.");
            console.error("Error al consultar el chatbot:", error);
        } finally {
            mostrarEscribiendo(false);
            botonEnviar.disabled = false;
            entrada.focus();
        }
    }

    document.getElementById("nuevo-chat").addEventListener("click", function() {
        nuevaConversacion(true);
    });
    document.getElementById("abrir-historial").addEventListener("click", abrirPanel);
    document.getElementById("cerrar-historial").addEventListener("click", cerrarPanel);
    sombraHistorial.addEventListener("click", cerrarPanel);

    formulario.addEventListener("submit", function(evento) {
        evento.preventDefault();
        const mensaje = entrada.value.trim();
        if (!mensaje) {
            entrada.focus();
            return;
        }
        enviarPregunta(mensaje);
    });

    // Limpiar solamente la conversación seleccionada; las demás se conservan.
    botonLimpiar.addEventListener("click", function() {
        const conversacion = obtenerActiva();
        if (!conversacion) {
            nuevaConversacion();
            return;
        }
        if (conversacion.mensajes.length > 0 && !window.confirm("¿Quieres borrar los mensajes de esta conversación? Las demás conversaciones se conservarán.")) {
            return;
        }
        conversacion.mensajes = [];
        conversacion.titulo = "Nuevo chat";
        conversacion.actualizada = new Date().toISOString();
        refrescarInterfaz();
    });

    // Las preguntas frecuentes usan la misma función de envío que el formulario.
    document.querySelectorAll(".pregunta").forEach(function(boton) {
        boton.addEventListener("click", function() {
            enviarPregunta(boton.textContent.trim());
        });
    });

    // Garantizar que exista una conversación activa al abrir la página.
    if (!obtenerActiva()) {
        nuevaConversacion();
    } else {
        guardarEstado();
        mostrarHistorial();
        mostrarMensajes();
    }
    </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def pagina():
    return HTML


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    mensaje = request.message.strip()
    if not mensaje:
        return ChatResponse(reply="Por favor, escribe una pregunta.")
    respuesta = await generar_respuesta(mensaje)
    return ChatResponse(reply=respuesta)
