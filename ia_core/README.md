# Proyecto actualizado automáticamente (2025-10-20 10:52:41)
Documentación generada automáticamente

## C:\Users\alber\Desktop\Python\webAI\ia_core\main.py
```python
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Carga variables de entorno de .env
load_dotenv()

# Directorio base del paquete ia_core
BASE_DIR = Path(__file__).resolve().parent

# Imports relativos dentro de ia_core
from .utils import enviar_a_ia, generar_estructura_proyecto
from .core.action_manager import ejecutar_accion
from .readme_manager import actualizar_readme


def main():
    print("🤖 Agente IA iniciado")

    # Generar estructura del proyecto al inicio
    estructura = generar_estructura_proyecto(base_path=BASE_DIR.parent)

    # Historial inicial: incluye la estructura para que la IA siempre sepa dónde están los archivos
    historial = (
        f"Contexto inicial del proyecto (estructura de archivos):\n"
        f"{json.dumps(estructura, indent=2)}\n"
        "Instrucciones: puedes leer, crear, escribir, borrar archivos, o hablar.\n"
    )

    while True:
        instruccion = input("\n¿Qué quieres que haga la IA? (escribe 'salir' para terminar): ")

        if instruccion.lower() == "salir":
            resumen = input("\nHaz un resumen de lo que hemos hablado y del avance del proyecto: ")
            historial += f"\nUsuario: {resumen}\n"
            break

        historial += f"\nUsuario: {instruccion}\n"

        # Llamada a la IA con historial, que ya incluye la estructura automáticamente
        respuesta_ia = enviar_a_ia(instruccion, contexto=historial)

        # Añade esto para depurar
        print("\n🟢 RESPUESTA CRUDA DE LA IA:")
        print(respuesta_ia)
        print("--------------------------------------------------\n")

        # Ejecutar acción/s devueltas por la IA
        resultado = ejecutar_accion(respuesta_ia, base_path=BASE_DIR.parent)

        # Mostrar resumen de acciones ejecutadas
        print("\n🔹 Resumen de acciones ejecutadas:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

        # Extraer contenidos leídos para actualizar README automáticamente
        contenidos_leidos = {}
        for accion in resultado.get("acciones", []):
            if accion.get("status") == "ok" and "contenido" in accion:
                contenidos_leidos.update(accion["contenido"])

        if contenidos_leidos:
            actualizar_readme(contenidos_leidos, base_path=BASE_DIR)

        # Actualizar estructura si se modificaron archivos
        if resultado.get("status") == "ok":
            estructura = generar_estructura_proyecto(base_path=BASE_DIR.parent)
            historial += f"\n[Actualización de estructura]:\n{json.dumps(estructura, indent=2)}\n"

        # Guardar respuesta en historial
        historial += f"IA: {respuesta_ia}\n"


if __name__ == "__main__":
    main()

```

## C:\Users\alber\Desktop\Python\webAI\ia_core\readme_manager.py
```python
from pathlib import Path
from datetime import datetime

def actualizar_readme(contenidos, mensaje_inicial="Documentación generada automáticamente", base_path="."):
    """
    Actualiza el README.md a partir del diccionario de contenidos de archivos.
    contenidos: dict de la forma { "archivo": "contenido" }
    base_path: directorio donde crear README.md
    """
    if not contenidos:
        print("⚠️ No hay contenidos para actualizar README.")
        return

    readme_path = Path(base_path) / "README.md"

    lines = [f"# Proyecto actualizado automáticamente ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n",
             f"{mensaje_inicial}\n\n"]

    for archivo, contenido in contenidos.items():
        if contenido is None:
            lines.append(f"## {archivo}\n❌ No se pudo leer el archivo.\n\n")
            continue
        lines.append(f"## {archivo}\n")
        lines.append("```python\n" if archivo.endswith(".py") else "```\n")
        lines.append(contenido + "\n")
        lines.append("```\n\n")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"📄 README.md actualizado con {len(contenidos)} archivos.")

```

## C:\Users\alber\Desktop\Python\webAI\ia_core\updateREADME.py
```python
from github import Github, Auth
from dotenv import load_dotenv
import os

load_dotenv()

file_url= "README.md"
TOKEN=os.getenv("GITHUB_TOKEN")
g =Github(auth=Auth.Token(TOKEN))
rep=g.get_repo("SantanaOlmo/webAI")

readme_remote=rep.get_contents(file_url)
with open(file_url,"r",encoding="utf-8") as local_readme:
    readme_content=local_readme.read()

rep.update_file(
    path=file_url,
    message="updated README.md",
    content=readme_content,
    sha=readme_remote.sha
)
```

## C:\Users\alber\Desktop\Python\webAI\ia_core\utils.py
```python
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
    schema_path = os.path.join(os.path.dirname(__file__), "config", "ai_schema.json")
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ No se encontró ia_core/config/ai_schema.json. Se usará esquema básico.")
        return {
            "instructions": "Responde solo en JSON válido con 'action' y 'mensaje' como mínimo.",
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


import os
import json
from pathlib import Path
import json

def generar_estructura_proyecto(base_path=None):
    """
    Genera un diccionario con la estructura del proyecto (carpetas y archivos)
    y la guarda en project_structure.json.
    """
    if base_path is None:
        base_path = Path(__file__).resolve().parent.parent  # sube desde ia_core

    estructura = {}

    for ruta in base_path.rglob("*"):
        if ruta.is_file():
            partes = ruta.relative_to(base_path).parts
            actual = estructura
            for p in partes[:-1]:
                actual = actual.setdefault(p, {})
            actual[partes[-1]] = "archivo"
        elif ruta.is_dir():
            partes = ruta.relative_to(base_path).parts
            actual = estructura
            for p in partes:
                actual = actual.setdefault(p, {})

    with open(base_path / "project_structure.json", "w", encoding="utf-8") as f:
        json.dump(estructura, f, indent=2, ensure_ascii=False)

    print("📦 Estructura del proyecto actualizada en project_structure.json")
    return estructura

```

## C:\Users\alber\Desktop\Python\webAI\ia_core\core\action_manager.py
```python
import json
from pathlib import Path

def ejecutar_accion(respuesta_json, base_path=None):
    """
    Ejecuta las acciones indicadas por la IA.
    Soporta:
      - Acciones simples o listas múltiples.
      - Rutas como str o lista de strings.
      - Crear, escribir, leer, borrar y hablar.
    """
    resultado = {"status": "ok", "acciones": []}

    if base_path is None:
        base_path = Path(__file__).resolve().parent.parent

    if not respuesta_json:
        print("⚠️ No se recibió respuesta de la IA.")
        return {"status": "error", "acciones": []}

    try:
        data = json.loads(respuesta_json) if isinstance(respuesta_json, str) else respuesta_json
    except json.JSONDecodeError:
        print(f"💬 IA dice (texto plano): {respuesta_json}")
        return {"status": "ok", "acciones": [{"status": "ok", "mensaje": respuesta_json, "contenido": {}}]}

    # Manejar formato con "actions" o lista simple
    if isinstance(data, dict) and "actions" in data:
        acciones = data["actions"]
    elif isinstance(data, list):
        acciones = data
    else:
        acciones = [data]

    for accion in acciones:
        accion_res = {"status": "ok", "mensaje": "", "contenido": {}}
        tipo = accion.get("action")
        contenido = accion.get("contenido", "")

        # Determinar la(s) ruta(s)
        rutas = accion.get("ruta")
        if isinstance(rutas, str):
            rutas = [rutas]
        elif not isinstance(rutas, list):
            rutas = []

        if tipo in ["leer", "crear", "escribir", "borrar"]:
            for ruta in rutas:
                if not isinstance(ruta, str):
                    continue
                ruta_final = (base_path / Path(ruta)).resolve()

                try:
                    if tipo == "leer":
                        if ruta_final.exists():
                            with open(ruta_final, "r", encoding="utf-8") as f:
                                contenido_archivo = f.read()
                            print(f"📖 Archivo leído: {ruta_final}")
                            accion_res["contenido"][str(ruta_final)] = contenido_archivo
                        else:
                            raise FileNotFoundError(f"Archivo no encontrado: {ruta_final}")

                    elif tipo in ["escribir", "crear"]:
                        ruta_final.parent.mkdir(parents=True, exist_ok=True)
                        with open(ruta_final, "w", encoding="utf-8") as f:
                            f.write(contenido)
                        accion_res["mensaje"] = f"Archivo {ruta_final} {'actualizado' if tipo == 'escribir' else 'creado'}."
                        print(f"📝 {accion_res['mensaje']}")

                    elif tipo == "borrar":
                        if ruta_final.exists():
                            ruta_final.unlink()
                            accion_res["mensaje"] = f"Archivo borrado: {ruta_final}"
                            print(f"🗑️ {accion_res['mensaje']}")
                        else:
                            raise FileNotFoundError(f"Archivo no encontrado: {ruta_final}")

                except Exception as e:
                    accion_res["status"] = "error"
                    accion_res["mensaje"] = str(e)
                    print(f"❌ Error al ejecutar acción '{tipo}': {e}")

        elif tipo == "hablar":
            mensaje = accion.get("mensaje") or contenido
            print(f"💬 IA dice: {mensaje}")
            accion_res["mensaje"] = mensaje

        else:
            accion_res["status"] = "error"
            accion_res["mensaje"] = f"Acción desconocida: {tipo}"
            print(f"❌ {accion_res['mensaje']}")

        resultado["acciones"].append(accion_res)

    return resultado

```

## C:\Users\alber\Desktop\Python\webAI\ia_core\config\ai_schema.json
```
{
  "instructions": "Responde SIEMPRE en JSON válido. Puedes generar una sola acción o varias acciones a la vez. No uses markdown, texto plano o comillas adicionales fuera del JSON. Cada acción debe incluir 'action' y opcionalmente 'ruta', 'contenido' o 'mensaje'.",
  "schema": {
    "action": "string",
    "ruta": "string o lista de strings (opcional)",
    "contenido": "string (opcional)",
    "mensaje": "string (opcional)"
  },
  "actions_allowed": ["leer", "escribir", "crear", "borrar", "hablar"],
  "example_single_action": {
    "action": "hablar",
    "mensaje": "Hola Alberto, todo está listo."
  },
  "example_multiple_actions": {
    "actions": [
      {"action": "leer", "ruta": ["README.md", "utils.py"]},
      {"action": "hablar", "mensaje": "He leído los archivos principales del proyecto"}
    ]
  }
}

```

## C:\Users\alber\Desktop\Python\webAI\ia_core\project_structure.json
```
{
  "": {
    "type": "folder",
    "children": {
      ".env": { "type": "file" },
      ".gitignore": { "type": "file" },
      "main.py": { "type": "file" },
      "project_structure.json": { "type": "file" },
      "README.md": { "type": "file" },
      "readme_manager.py": { "type": "file" },
      "resumen.txt": { "type": "file" },
      "updateREADME.py": { "type": "file" },
      "utils.py": { "type": "file" },
      "workspace": { "type": "folder", "children": {} }
    }
  },
  "config": {
    "type": "folder",
    "children": {
      "ai_schema.json": { "type": "file" }
    }
  },
  "core": {
    "type": "folder",
    "children": {
      "action_manager.py": { "type": "file" },
      "__init__.py": { "type": "file" }
    }
  }
}

```

