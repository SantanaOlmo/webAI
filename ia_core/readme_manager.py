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
