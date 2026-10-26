"""Chatbot de CENIGRAF con interfaz adaptable y API FastAPI."""

from typing import Dict, List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from iagenerativa import generar_respuesta

app = FastAPI(title="Bienvenido a CeniBot", version="2.0.0")


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
    <title>BIENVENIDO A CeniBot</title>
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
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 24px 16px;
            min-height: 100vh;
            background: radial-gradient(circle at top left, #e2eefb 0, var(--fondo) 42%, #f8fafc 100%);
            color: var(--texto);
            font-family: Inter, "Segoe UI", Arial, sans-serif;
        }
        .contenedor { width: 100%; max-width: 900px; margin: 0 auto; }
        .encabezado {
            display: flex; align-items: center; gap: 14px;
            padding: 20px 24px; color: white;
            background: linear-gradient(120deg, var(--azul-oscuro), var(--azul));
            border-radius: 20px 20px 0 0;
            box-shadow: 0 10px 28px rgba(18, 60, 105, .16);
        }
        .logo {
            display: grid; place-items: center; flex: 0 0 52px; height: 52px;
            border-radius: 16px; background: rgba(255,255,255,.14);
            font-size: 18px; font-weight: 800; letter-spacing: .5px;
            border: 1px solid rgba(255,255,255,.25);
        }
        .encabezado h1 { margin: 0 0 4px; font-size: 1.25rem; }
        .encabezado p { margin: 0; color: #dce9f7; font-size: .92rem; }
        .estado { margin-left: auto; display: flex; align-items: center; gap: 7px; font-size: .8rem; white-space: nowrap; color: #e2f8ee; }
        .punto { width: 8px; height: 8px; background: #5ee0a0; border-radius: 50%; }
        .panel { background: var(--blanco); border: 1px solid var(--borde); border-top: 0; border-radius: 0 0 20px 20px; overflow: hidden; box-shadow: 0 16px 36px rgba(16, 39, 70, .09); }
        .contenido { padding: 22px; }
        .intro { margin: 0 0 16px; color: var(--suave); line-height: 1.5; font-size: .95rem; }
        .seccion-titulo { margin: 0 0 10px; font-size: .91rem; color: var(--azul-oscuro); font-weight: 750; }
        .preguntas { display: flex; flex-wrap: wrap; gap: 9px; margin-bottom: 18px; }
        .pregunta {
            border: 1px solid #c9d8ea; border-radius: 999px; background: #f7faff;
            color: var(--azul); padding: 9px 13px; cursor: pointer; font: inherit;
            font-size: .86rem; line-height: 1.3; transition: background .15s, transform .15s;
        }
        .pregunta:hover:not(:disabled) { background: var(--azul-claro); transform: translateY(-1px); }
        button:focus-visible, input:focus-visible { outline: 3px solid #80b7f0; outline-offset: 2px; }
        button:disabled { opacity: .55; cursor: wait; }
        .chat {
            height: min(43vh, 390px); min-height: 260px; overflow-y: auto;
            padding: 16px; border: 1px solid var(--borde); border-radius: 15px;
            background: #f8fafc; scroll-behavior: smooth;
        }
        .mensaje { display: flex; margin: 0 0 14px; }
        .mensaje:last-child { margin-bottom: 0; }
        .burbuja { max-width: 85%; padding: 11px 14px; border-radius: 14px; line-height: 1.5; white-space: pre-wrap; overflow-wrap: anywhere; font-size: .95rem; }
        .mensaje.asistente { justify-content: flex-start; }
        .mensaje.asistente .burbuja { background: white; border: 1px solid var(--borde); border-top-left-radius: 5px; }
        .mensaje.usuario { justify-content: flex-end; }
        .mensaje.usuario .burbuja { color: white; background: var(--azul); border-top-right-radius: 5px; }
        .mensaje.sistema .burbuja { max-width: 100%; color: #8a4b08; background: #fff7e8; border: 1px solid #f4d59b; font-size: .88rem; }
        .escribiendo { display: none; margin: 12px 0 0; color: var(--suave); font-size: .88rem; align-items: center; gap: 9px; }
        .escribiendo.visible { display: flex; }
        .puntos { display: inline-flex; gap: 4px; }
        .puntos span { width: 6px; height: 6px; border-radius: 50%; background: var(--turquesa); animation: subir 1s infinite ease-in-out; }
        .puntos span:nth-child(2) { animation-delay: .15s; }
        .puntos span:nth-child(3) { animation-delay: .3s; }
        @keyframes subir { 0%, 60%, 100% { transform: translateY(0); opacity: .45; } 30% { transform: translateY(-4px); opacity: 1; } }
        .formulario { display: flex; gap: 10px; margin-top: 14px; }
        .entrada { flex: 1; min-width: 0; padding: 13px 15px; border: 1px solid #bdc9d8; border-radius: 12px; font: inherit; color: var(--texto); background: white; }
        .boton { border: 0; border-radius: 12px; padding: 12px 17px; cursor: pointer; font: inherit; font-weight: 700; transition: background .15s; }
        .enviar { background: var(--turquesa); color: white; }
        .enviar:hover:not(:disabled) { background: #0b7375; }
        .acciones { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-top: 14px; }
        .ayuda { color: var(--suave); font-size: .8rem; line-height: 1.4; }
        .limpiar { background: white; color: var(--azul); border: 1px solid #c9d8ea; padding: 9px 13px; }
        .limpiar:hover:not(:disabled) { background: var(--azul-claro); }
        .pie { text-align: center; color: var(--suave); font-size: .78rem; padding: 14px 10px 2px; }
        @media (max-width: 620px) {
            body { padding: 10px; }
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
        @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; scroll-behavior: auto !important; } }

        /* PANEL DEL HISTORIAL */
        .boton-historial {
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 1003;
        background: #1459c7;
        color: white;
        }
        .panel-historial 
            position: fixed
            top: 0
            bottom: 0
            left: 0
            width: 270px
            box-sizing: border-box
            padding: 18px
            overflow-y: auto
            background: #f5f7fa
            border-right: 1px solid #ddd
            z-index: 1002
            transform: translateX(-100%)
            transition: transform 0.2s ease
        }
        .panel-historial.abierto {
        transform: translateX(0);
        }

        .encabezado-historial 
            display: flex
            justify-content: space-between
            align-items: center
            gap: 8px
            margin-bottom: 18px
        }
        .encabezado-historial h2 
            font-size: 17px
            margin: 0
        }
        .nuevo-chat 
            width: 100%
            margin-bottom: 18px
            background: #1459c7
            color: white
        }
        #lista-historial {
        display: flex;
        flex-direction: column;
        gap: 6px;
        }
        .item-historial 
            display: block
            width: 100%
            box-sizing: border-box
            padding: 11px
            border: 1px solid transparent
            border-radius: 8px
            background: transparent
            color: #222
            text-align: left
            overflow: hidden
            white-space: nowrap
            text-overflow: ellipsis
            cursor: pointer
        }
        .item-historial:hover
        .item-historial.activa 
            background: #e3edfc
            border-color: #c5d8f8
        }
        .sombra-historial 
            display: none
            position: fixed
            inset: 0
            background: rgba(0, 0, 0, 0.3)
            z-index: 1001
        }
        .sombra-historial.visible 
            display: block
        }
        @media (min-width: 900px) 
            body 
                margin: 40px 24px 40px 300px
                max-width: 760px

            .panel-historial 
                transform: translateX(0)

            .boton-historial
            #cerrar-historial
            .sombra-historial 
                display: none !important

        }
        @media (max-width: 899px) 
            body 
                margin: 65px 12px 24px

        }
        </style>
</head>
<body>
<button id="abrir-historial" class="boton-historial">
    ☰ Historial
</button>

<div id="sombra-historial" class="sombra-historial"></div>

<aside id="panel-historial" class="panel-historial">
    <div class="encabezado-historial">
        <h2>Mis conversaciones</h2>
        <button id="cerrar-historial" type="button">×</button>
    </div>

    <button id="nuevo-chat" class="nuevo-chat" type="button">
        + Nuevo chat
    </button>

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
                <h2 class="seccion-titulo">Conversación</h2>
                <div class="chat" id="chat" role="log" aria-live="polite" aria-relevant="additions text">
                    <div class="mensaje asistente"><div class="burbuja">¡Bienvenido! Estoy aquí para ayudarte con información de CeniBot.</div></div>
                </div>
                <div id="escribiendo" class="escribiendo" role="status" aria-live="polite" aria-hidden="true">
                    <span class="puntos" aria-hidden="true"><span></span><span></span><span></span></span>
                    El chatbot está escribiendo…
                </div>
                <form class="formulario" id="formulario">
                    <input class="entrada" id="mensaje" name="mensaje" type="text" placeholder="Escribe tu pregunta…" maxlength="2000" autocomplete="off" aria-label="Escribe tu pregunta">
                    <button class="boton enviar" id="enviar" type="submit">Enviar</button>
                </form>
                <div class="acciones">
                    <span class="ayuda">Las respuestas dependen de la información institucional disponible.</span>
                    <button class="boton limpiar" id="limpiar" type="button">Limpiar chat</button>
                </div>
            </div>
        </section>
        <footer class="pie">CeniBot · Asistente informativo</footer>
    </main>
    <script>
    const chat = document.getElementById("chat");
    const formulario = document.getElementById("formulario");
    const entrada = document.getElementById("mensaje");

    const CLAVE_HISTORIAL = "historial_chat_cenigraf";

    let historial = [];

    try {
        historial = JSON.parse(
            localStorage.getItem(CLAVE_HISTORIAL) || "[]"
        );

        if (!Array.isArray(historial)) {
            historial = [];
        }
    } catch (error) {
        historial = [];
    }

    function agregarMensaje(remitente, texto, guardar = true) {
        const parrafo = document.createElement("p");
        parrafo.className = "mensaje";
        parrafo.textContent = remitente + ": " + texto;

        chat.appendChild(parrafo);
        chat.scrollTop = chat.scrollHeight;

        if (guardar) {
            historial.push({ remitente, texto });

            // Conservar solamente los últimos 100 mensajes.
            historial = historial.slice(-100);

            localStorage.setItem(
                CLAVE_HISTORIAL,
                JSON.stringify(historial)
            );
        }
    }

    function cargarHistorial() {
        chat.innerHTML = "";

        if (historial.length === 0) {
            const bienvenida = document.createElement("p");
            bienvenida.className = "mensaje";
            bienvenida.textContent = "¡Bienvenido a CHATBOT!";
            chat.appendChild(bienvenida);
            return;
        }

        historial.forEach(function(mensaje) {
            agregarMensaje(
                mensaje.remitente,
                mensaje.texto,
                false
            );
        });
    }

    cargarHistorial();

    formulario.addEventListener("submit", async function(evento) {
        evento.preventDefault();

        const mensaje = entrada.value.trim();

        if (!mensaje) {
            agregarMensaje(
                "Bot",
                "Por favor, escribe un mensaje."
            );
            return;
        }

        agregarMensaje("Tú", mensaje);
        entrada.value = "";

        try {
            const respuesta = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: mensaje
                })
            });

            if (!respuesta.ok) {
                throw new Error("No se pudo obtener una respuesta.");
            }

            const datos = await respuesta.json();
            agregarMensaje("Bot", datos.reply);

        } catch (error) {
            agregarMensaje(
                "Bot",
                "Error: " + error.message
            );
        }
    });
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
