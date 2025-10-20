import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Configuración de la API Key de Gemini
API_KEY = os.getenv("IA_API_KEY")
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"


def limpiar_respuesta(respuesta):
    """Limpia cualquier bloque de código o markdown en la respuesta de la IA."""
    if not respuesta:
        return None
    respuesta = respuesta.strip()
    if respuesta.startswith("```"):
        respuesta = respuesta.split("\n", 1)[-1]
    if respuesta.endswith("```"):
        respuesta = respuesta.rsplit("```", 1)[0]
    return respuesta.strip()


def cargar_ai_schema():
    """Carga el esquema JSON con instrucciones y formato esperado para la IA."""
    schema_path = Path(__file__).parent / "config" / "ai_schema.json"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ No se encontró ia_core/config/ai_schema.json. Se usará esquema básico.")
        return {
            "instructions": (
                "Responde SIEMPRE en JSON válido. Puedes generar una sola acción o varias a la vez. "
                "No uses markdown ni texto plano fuera del JSON. Cada acción debe incluir 'action', "
                "'ruta' si aplica, 'type' ('file' o 'directory') si creas algo, y opcionalmente 'contenido' o 'mensaje'."
            ),
            "actions_allowed": ["leer", "escribir", "crear", "borrar", "hablar"],
            "example_single_action": {"action": "hablar", "mensaje": "Hola!"},
            "example_multiple_actions": [
                {"action": "leer", "ruta": "archivo.txt"},
                {"action": "hablar", "mensaje": "Archivo leído"}
            ]
        }


def enviar_a_ia(instruccion, contexto=""):
    """Envía la instrucción a Gemini con contexto e instrucciones reforzadas desde ai_schema.json."""
    schema = cargar_ai_schema()

    instrucciones_ai = (
        f"{schema['instructions']}\n\n"
        f"Acciones permitidas: {', '.join(schema['actions_allowed'])}\n"
        f"Ejemplo de acción individual:\n{json.dumps(schema['example_single_action'])}\n"
        f"Ejemplo de acciones múltiples:\n{json.dumps(schema['example_multiple_actions'])}\n\n"
    )

    prompt = (
        f"{instrucciones_ai}"
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


def generar_estructura_proyecto(base_path=None):
    """
    Genera un diccionario con la estructura del proyecto (carpetas y archivos)
    y la guarda en project_structure.json.
    """
    if base_path is None:
        base_path = Path(__file__).resolve().parent.parent  # sube desde ia_core

    estructura = {}

    for ruta in base_path.rglob("*"):
        partes = ruta.relative_to(base_path).parts
        actual = estructura
        for p in partes[:-1]:
            actual = actual.setdefault(p, {})
        if ruta.is_file():
            actual[partes[-1]] = {"type": "file"}
        elif ruta.is_dir():
            actual[partes[-1]] = {"type": "directory"}

    with open(base_path / "project_structure.json", "w", encoding="utf-8") as f:
        json.dump(estructura, f, indent=2, ensure_ascii=False)

    print("📦 Estructura del proyecto actualizada en project_structure.json")
    return estructura
