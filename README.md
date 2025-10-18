# webAI

### crear el entorno virtual
```bash
python -m venv .venv
```

### activar el entorno 

En Windows: `.\.venv\scripts\activate`

### añadir al .gitignore
```
.venv/
__pycache__/
*.pyc
```

### crear la estructura mínima

```
/repo
    README.md
    main.py             # Script principal del agente IA
    utils.py            # Funciones de ayuda
    requirements.txt    # Paquetes necesarios 
    .env
```

### .env

 ```
    GITHUB_TOKEN=tu_token_aqui
    IA_API_KEY=tu_api_key_aqui
```

## Instala `python-dotenv` dentro de .venv y activa el entorno

- #### Windows (cmd o powershell):
  ````
    .\.venv\Scripts\activate
  ````
  - #### Windows (bash):
  ````
    source .venv/Scripts/activate
  ````
- #### Linux/macOS:
  ````
    source .venv/bin/activate
  ````

### INSTALA
```
pip install python-dotenv
```
---

- #### verifica que esté instalado
  ````
    pip list | grep dotenv
  ````
deberías ver algo como:
````
python-dotenv 1.1.1
````



y al principio del archivo `main.py` añade :

```
from dotenv import load_dotenv
load_dotenv()
````

## acciones de la ia

| Action                | Qué hace                                      |
| --------------------- | --------------------------------------------- |
| `leer`                | Leer un archivo y devolver su contenido       |
| `escribir`            | Sobrescribir un archivo con contenido nuevo   |
| `crear`               | Crear un archivo nuevo                        |
| `borrar`              | Borrar un archivo                             |
| `hablar`              | Pedir aclaraciones o enviar mensaje a ti      |
| `invitar_colaborador` | Invitar a alguien a tu repo usando GitHub API |


### flujo del script principal `main.py`
1. Leer instrucciones de la IA.
2. Parsear el JSON de acción.
3. Ejecutar la acción correspondiente (leer, escribir, crear, borrar, invitar).
4. Si es “hablar”, mostrar mensaje y esperar tu respuesta.
5. Volver a iterar.


# Agente IA en Python

Este archivo define un **agente de IA** que recibe instrucciones del usuario, llama a la IA a través de `enviar_a_ia` y ejecuta acciones como leer, escribir, crear o borrar archivos, o simplemente "hablar".

```python
import os
import json
from utils import enviar_a_ia  # Función que envía el prompt a la IA y devuelve la respuesta
from dotenv import load_dotenv  # Para cargar variables de entorno desde un .env

load_dotenv()  # Carga las variables de entorno necesarias, por ejemplo claves de API

def ejecutar_accion(respuesta_json):
    """
    Ejecuta la acción indicada por la IA.
    
    Parámetros:
    - respuesta_json: string JSON devuelto por la IA, con estructura tipo:
      {
          "action": "leer" | "escribir" | "crear" | "borrar" | "hablar",
          "ruta": "archivo.txt",
          "contenido": "texto a escribir",
          "mensaje": "texto para mostrar"
      }
    
    Maneja errores si la respuesta es None o no es JSON válido.
    """
    if not respuesta_json:
        print("No se recibió respuesta de la IA.")
        return

    try:
        data = json.loads(respuesta_json)  # Intentamos convertir el string JSON en un dict
    except json.JSONDecodeError:
        # Si no es JSON válido, asumimos que la IA solo quiere "hablar"
        print(f"IA dice (texto plano): {respuesta_json}")
        return

    # Extraemos la acción
    action = data.get("action")

    if action == "leer":
        # Leer un archivo
        ruta = data.get("ruta")
        if ruta and os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            print(f"Contenido de {ruta}:\n{contenido}")
        else:
            print(f"Archivo {ruta} no encontrado.")

    elif action in ["escribir", "crear"]:
        # Escribir o crear un archivo
        ruta = data.get("ruta")
        contenido = data.get("contenido", "")
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(contenido)
            print(f"Archivo {ruta} {'actualizado' if action=='escribir' else 'creado'}.")

    elif action == "borrar":
        # Borrar un archivo
        ruta = data.get("ruta")
        if ruta and os.path.exists(ruta):
            os.remove(ruta)
            print(f"Archivo {ruta} borrado.")
        else:
            print(f"Archivo {ruta} no encontrado.")

    elif action == "hablar":
        # Solo mostrar un mensaje
        mensaje = data.get("mensaje", "")
        print(f"IA dice: {mensaje}")

    else:
        print(f"Acción desconocida: {action}")

def main():
    """
    Bucle principal del agente:
    - Pide instrucciones al usuario.
    - Envía la instrucción a la IA.
    - Ejecuta la acción devuelta por la IA.
    - Mantiene un historial de la conversación.
    """
    print("Agente IA iniciando...")
    historial = ""  # Para mantener contexto de la conversación

    while True:
        instruccion = input("\n¿Qué quieres que haga la IA? (escribe 'salir' para terminar): ")
        if instruccion.lower() == "salir":
            resumen = input("\nHaz un resumen de lo que hemos hablado y del avance del proyecto: ")
            historial += f"\nUsuario: {resumen}\n"
            break

        historial += f"\nUsuario: {instruccion}\n"

        # Llamada a la IA con historial
        respuesta_ia = enviar_a_ia(instruccion, contexto=historial)

        # Ejecutar acción devuelta por la IA
        ejecutar_accion(respuesta_ia)

        # Guardar respuesta en el historial
        historial += f"IA: {respuesta_ia}\n"

if __name__ == "__main__":
    main()
