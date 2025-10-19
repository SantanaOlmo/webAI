# -----------------------------
# Dockerfile para IA Proyecto
# -----------------------------
# Usamos Python 3.11 oficial
FROM python:3.11-slim

# Variables de entorno para que Python no genere pyc y buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos sólo lo necesario para instalar dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiamos la IA (ia_core) al contenedor
COPY ia_core/ ./ia_core/

# Creamos la carpeta donde la IA trabajará sobre los proyectos (workspace)
RUN mkdir /workspace

# Definimos volumen para que el workspace quede persistente fuera del contenedor
VOLUME ["/workspace"]

# Comando por defecto al iniciar el contenedor
# - Ejecuta main.py interactivo
CMD ["python", "ia_core/main.py"]
