from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "No se encontró GEMINI_API_KEY en el archivo .env"
    )

client = genai.Client(
    api_key=api_key
)

respuesta = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Responde en español: ¿Qué es la inteligencia artificial y cómo funciona?"
)

print(respuesta.text)
