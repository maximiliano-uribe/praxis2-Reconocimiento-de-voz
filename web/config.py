import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carpeta de datos y subcarpetas
DATA_DIR = os.path.join(BASE_DIR, "data")
VOCES_AUTORIZADAS = os.path.join(DATA_DIR, "voces_autorizadas")
VERIFICACIONES = os.path.join(DATA_DIR, "verificaciones")
HISTORIAL_JSON = os.path.join(DATA_DIR, "historial.json")
CLAVE_FILE = os.path.join(DATA_DIR, "clave.txt")
VOCES_JSON = os.path.join(DATA_DIR, "voces.json")

# Carpeta de estáticos para imágenes generadas
STATIC_FOLDER = os.path.join(BASE_DIR, "static")

# Carpeta de audios a graficar (puede ser la misma que VOCES_AUTORIZADAS)
VOCES_FOLDER = os.path.join(BASE_DIR, "voces")

#pdfs
PDFS_FOLDER = os.path.join(STATIC_FOLDER, "pdfs")

# Crear carpetas si no existen
for carpeta in [VOCES_AUTORIZADAS, VERIFICACIONES, STATIC_FOLDER, VOCES_FOLDER]:
    os.makedirs(carpeta, exist_ok=True)


