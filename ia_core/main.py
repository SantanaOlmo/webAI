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
        "Instrucciones: puedes leer, crear, escribir, borrar archivos o carpetas, o hablar.\n"
        "Cuando crees un archivo o carpeta, incluye siempre el campo 'type' con valor 'file' o 'directory'.\n"
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

        # Depuración
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

        # Actualizar estructura si se modificaron archivos o carpetas
        if resultado.get("status") == "ok":
            estructura = generar_estructura_proyecto(base_path=BASE_DIR.parent)
            historial += f"\n[Actualización de estructura]:\n{json.dumps(estructura, indent=2)}\n"

        # Guardar respuesta en historial
        historial += f"IA: {respuesta_ia}\n"


if __name__ == "__main__":
    main()
