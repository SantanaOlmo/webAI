from dotenv import load_dotenv
from ia_core.utils import enviar_a_ia, generar_estructura_proyecto
from core.action_manager import ejecutar_accion
from ia_core.readme_manager import actualizar_readme
import json

load_dotenv()

def main():
    print("🤖 Agente IA iniciado")

    # Generar la estructura del proyecto al inicio
    estructura = generar_estructura_proyecto()
    
    # Historial inicial: incluye la estructura para que la IA siempre sepa dónde están los archivos
    historial = f"Contexto inicial del proyecto (estructura de archivos):\n{json.dumps(estructura, indent=2)}\n"
    historial += "Instrucciones: puedes leer, crear, escribir, borrar archivos, o hablar.\n"

    while True:
        instruccion = input("\n¿Qué quieres que haga la IA? (escribe 'salir' para terminar): ")

        if instruccion.lower() == "salir":
            resumen = input("\nHaz un resumen de lo que hemos hablado y del avance del proyecto: ")
            historial += f"\nUsuario: {resumen}\n"
            break

        historial += f"\nUsuario: {instruccion}\n"

        # Llamada a la IA con historial, que ya incluye la estructura automáticamente
        respuesta_ia = enviar_a_ia(instruccion, contexto=historial)

        # Ejecutar acción/s devueltas por la IA
        resultado = ejecutar_accion(respuesta_ia)

        # Mostrar resumen de acciones ejecutadas
        print("\n🔹 Resumen de acciones ejecutadas:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

        # Extraer contenidos leídos para actualizar README automáticamente
        contenidos_leidos = {}
        for accion in resultado.get("acciones", []):
            if accion.get("status") == "ok" and "contenido" in accion:
                contenidos_leidos.update(accion["contenido"])

        if contenidos_leidos:
            actualizar_readme(contenidos_leidos)

        # Actualizar estructura si se modificaron archivos
        if resultado.get("status") == "ok":
            estructura = generar_estructura_proyecto()
            historial += f"\n[Actualización de estructura]:\n{json.dumps(estructura, indent=2)}\n"

        # Guardar respuesta en historial
        historial += f"IA: {respuesta_ia}\n"


if __name__ == "__main__":
    main()
