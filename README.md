# IA Project Template 🚀

Esta es una plantilla de proyecto que incluye un **agente IA** capaz de:

- Leer, crear, modificar y borrar archivos dentro de un proyecto.
- Generar y mantener actualizado automáticamente el README.md.
- Trabajar sobre cualquier proyecto nuevo dentro de la carpeta `workspace/`.

La IA está aislada en `ia_core/`, por lo que no puede modificar su propio código, solo tu proyecto.

---

## Estructura de carpetas

```
mi_template_repo/
│
├─ ia_core/                 # Código de la IA y gestión de acciones
│   ├─ __init__.py
│   ├─ main.py              # Script principal de la IA
│   ├─ action_manager.py    # Ejecuta las acciones devueltas por la IA
│   ├─ readme_manager.py    # Genera y actualiza README.md
│   ├─ updateREADME.py      # Actualiza README.md en GitHub
│   ├─ utils.py             # Funciones de ayuda
│   └─ .env                 # Variables de entorno: IA_API_KEY y GITHUB_TOKEN
│
├─ workspace/               # Carpeta donde trabajarás con tus proyectos
│   └─ ...                  # Aquí la IA puede leer/escribir archivos
│
├─ requirements.txt         # Dependencias Python
├─ Dockerfile               # Configuración Docker
└─ README.md                # Este archivo
```

> Nota: `workspace/` se montará como volumen dentro del contenedor Docker. La IA no puede acceder a `ia_core/` para modificar su propio código.

---

## Primeros pasos

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/tu_usuario/mi_template_repo.git
cd mi_template_repo
```

### 2️⃣ Configurar variables de entorno
Crea un archivo `.env` dentro de `ia_core/` con tus credenciales:

```
IA_API_KEY=tu_api_key_de_gemini
GITHUB_TOKEN=tu_token_de_github
```

### 3️⃣ Construir la imagen Docker
```bash
docker build -t ia_project .
```

### 4️⃣ Ejecutar el contenedor
```bash
docker run -it --rm -v $(pwd)/workspace:/workspace ia_project
```

- `-it` → modo interactivo.
- `--rm` → elimina el contenedor al cerrarlo.
- `-v $(pwd)/workspace:/workspace` → monta tu proyecto local para que la IA pueda trabajar en él.

Ahora podrás dar instrucciones a la IA, como:

- Leer archivos: `leer "archivo.txt"`
- Crear o modificar archivos: `crear "archivo.txt" con contenido ...`
- Actualizar automáticamente el README: la IA se encarga de mantenerlo actualizado según los cambios en `workspace/`.

---

## Dependencias

Dentro de `requirements.txt` deberían incluirse al menos:

```
google-generativeai
python-dotenv
PyGithub
```

> Puedes añadir más según tu proyecto.

---

## Flujo recomendado de trabajo

1. Crea tu proyecto dentro de `workspace/`.
2. Ejecuta la IA con Docker.
3. Pide a la IA que lea tus archivos para inicializar el contexto.
4. La IA puede ayudarte a:
   - Mantener README actualizado.
   - Detectar posibles errores o inconsistencias.
   - Sugerir mejoras o generar contenido nuevo.
5. Al finalizar, guarda tus cambios en Git desde fuera del contenedor como siempre.

---

## Notas importantes

- La IA **solo interactúa con `workspace/`**.
- `ia_core/` contiene la lógica de la IA y **no debe ser modificada por la IA**.
- El archivo `project_structure.json` se genera automáticamente y se actualiza cada vez que la IA detecta cambios en el proyecto.

---

## Futuras mejoras

- Integración multi-idioma para README.
- Soporte de plantillas MERN, Flask u otros frameworks.
- Control de versiones más avanzado dentro de la IA.
