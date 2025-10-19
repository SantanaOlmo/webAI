import os
import json

def ejecutar_accion(respuesta_json):
    """
    Ejecuta la acción o acciones indicadas por la IA.
    Maneja errores si la respuesta es None o no es JSON válido.
    Soporta múltiples acciones y convierte listas de un solo elemento en string para rutas.
    """
    if not respuesta_json:
        print("No se recibió respuesta de la IA.")
        return {"status": "error", "acciones": [{"status": "error", "mensaje": "No se recibió respuesta"}]}

    try:
        data = json.loads(respuesta_json)
    except json.JSONDecodeError:
        print(f"IA dice (texto plano): {respuesta_json}")
        return {"status": "ok", "acciones": [{"status": "ok", "mensaje": respuesta_json}]}

    acciones = data.get("actions")
    if acciones is None:
        # Soporta acción única
        acciones = [data]

    resumen_acciones = []

    for accion in acciones:
        act = accion.get("action")
        ruta = accion.get("ruta")
        contenido = accion.get("contenido", "")
        resultado = {"status": "ok", "mensaje": "", "contenido": {}}

        # Convertir lista de un solo elemento a string
        if isinstance(ruta, list) and len(ruta) == 1:
            ruta = ruta[0]

        # Evitar intentar abrir carpetas
        if act == "leer":
            if ruta and os.path.isfile(ruta):
                try:
                    with open(ruta, "r", encoding="utf-8") as f:
                        resultado["contenido"][ruta] = f.read()
                    print(f"📄 Contenido de {ruta} leído.")
                except Exception as e:
                    resultado["status"] = "error"
                    resultado["mensaje"] = str(e)
                    print(f"❌ Error leyendo {ruta}: {e}")
            else:
                resultado["status"] = "error"
                resultado["mensaje"] = f"{ruta} no es un archivo o no existe"
                print(f"❌ Error leyendo {ruta}: no es un archivo o no existe")

        elif act in ["escribir", "crear"]:
            if ruta and isinstance(ruta, str):
                try:
                    # Asegurarse de que el directorio exista
                    os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
                    with open(ruta, "w", encoding="utf-8") as f:
                        f.write(contenido)
                    print(f"📄 Archivo {ruta} {'actualizado' if act=='escribir' else 'creado'}.")
                except Exception as e:
                    resultado["status"] = "error"
                    resultado["mensaje"] = str(e)
                    print(f"❌ Error escribiendo {ruta}: {e}")
            else:
                resultado["status"] = "error"
                resultado["mensaje"] = f"Ruta inválida para acción {act}: {ruta}"
                print(f"❌ Ruta inválida para acción {act}: {ruta}")

        elif act == "borrar":
            if ruta and os.path.isfile(ruta):
                try:
                    os.remove(ruta)
                    print(f"🗑 Archivo {ruta} borrado.")
                except Exception as e:
                    resultado["status"] = "error"
                    resultado["mensaje"] = str(e)
                    print(f"❌ Error borrando {ruta}: {e}")
            else:
                resultado["status"] = "error"
                resultado["mensaje"] = f"{ruta} no es un archivo o no existe"
                print(f"❌ Error borrando {ruta}: no es un archivo o no existe")

        elif act == "hablar":
            mensaje = accion.get("mensaje", "")
            print(f"💬 IA dice: {mensaje}")
            resultado["mensaje"] = mensaje

        else:
            print(f"❌ Acción desconocida: {act}")
            resultado["status"] = "error"
            resultado["mensaje"] = f"Acción desconocida: {act}"

        resumen_acciones.append(resultado)

    return {"status": "ok", "acciones": resumen_acciones}
