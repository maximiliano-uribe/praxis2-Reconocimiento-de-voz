# utils/archivos.py

import os
import json
import subprocess

def asegurar_carpeta(carpeta):
    os.makedirs(carpeta, exist_ok=True)


def convertir_webm_a_wav(entrada, salida, sr_target=16000):
    """
    Conversión usando ffmpeg.
    """
    comando = [
        "ffmpeg",
        "-y",
        "-i", entrada,
        "-ar", str(sr_target),
        "-ac", "1",
        salida
    ]
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def leer_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def guardar_json(path, contenido):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(contenido, f, indent=4)
