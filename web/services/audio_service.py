import subprocess
import librosa
import numpy as np

def convertir_webm_a_wav(entrada, salida):
    cmd = [
        "ffmpeg", "-y",
        "-i", entrada,
        "-ar", "16000",
        "-ac", "1",
        salida
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def cargar_audio(path):
    try:
        y, sr = librosa.load(path, sr=16000)
        return y, sr
    except:
        return None, None

def normalizar(y):
    return y / (np.linalg.norm(y) + 1e-9)
