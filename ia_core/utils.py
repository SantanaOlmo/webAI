import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configuración de la API Key de Gemini
API_KEY = os.getenv("IA_API_KEY")
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"


def limpiar_respuesta(respuesta):
    """
    Limpia cualquier bloque de código o markdown en la respuesta de la IA.
    """
    if not respuesta:
        return None
    respuesta = respuesta.strip()
    if respuesta.startswith("```"):
        respuesta = respuesta.split("\n", 1)[-1]
    if respuesta.endswith("```"):
        respuesta = respuesta.rsplit("```", 1)[0]
    return respuesta.strip()


def cargar_ai_schema():
    """
    Carga el esquema JSON con instrucciones y formato esperado para la IA.
    """
    schema_path = os.path.join("config", "ai_schema.json")
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ No se encontró config/ai_schema.json. Se usará esquema básico.")
        return {
            "instructions": "Responde solo en JSON válido con 'action' y 'mensaje' como mínimo.",
            "actions_allowed": ["leer", "escribir", "crear", "borrar", "hablar"],
            "example_single_action": {"action": "hablar", "mensaje": "Hola!"},
            "example_multiple_actions": [
                {"action": "leer", "ruta": "archivo.txt"},
                {"action": "hablar", "mensaje": "Contenido leído!"}
            ]
        }


def generar_estructura_proyecto(ruta_raiz=".", archivo_salida="project_structure.json"):
    """
    Genera un JSON con la estructura actual del proyecto.
    """
    estructura = {}

    for dirpath, dirnames, filenames in os.walk(ruta_raiz):
        # Ignorar carpetas de entorno, pycache y git
        if any(x in dirpath for x in [".venv", "__pycache__", ".git"]):
            continue

        rel_path = os.path.relpath(dirpath, ruta_raiz)
        if rel_path == ".":
            rel_path = ""
        estructura[rel_path] = filenames

    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(estructura, f, indent=2, ensure_ascii=False)

    print(f"📦 Estructura del proyecto actualizada en {archivo_salida}")
    return estructura  # Devuelve la estructura para enviarla automáticamente al historial


def enviar_a_ia(instruccion, contexto=""):
    """
    Envía la instrucción a Gemini con contexto e instrucciones reforzadas desde ai_schema.json.
    Se asegura de que la IA genere rutas como strings y pueda devolver múltiples acciones.
    """
    schema = cargar_ai_schema()
    instrucciones_ai = (
        f"{schema['instructions']}\n\n"
        f"Acciones permitidas: {', '.join(schema['actions_allowed'])}\n"
        f"Ejemplo de acción individual:\n{json.dumps(schema['example_single_action'])}\n"
        f"Ejemplo de acciones múltiples:\n{json.dumps(schema['example_multiple_actions'])}\n\n"
        "Importante:\n"
        "- Todas las rutas deben ser strings, no listas.\n"
        "- Se pueden enviar varias acciones en un solo JSON bajo 'actions'."
    )

    prompt = (
        f"{instrucciones_ai}\n"
        f"Contexto del proyecto:\n{contexto}\n\n"
        f"Petición del usuario:\n{instruccion}"
    )

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return limpiar_respuesta(response.text)
    except Exception as e:
        print("❌ Error al comunicarse con Gemini:", e)
        return None
