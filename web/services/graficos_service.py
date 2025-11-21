# services/graficos_service.py

import os
import numpy as np
import librosa
import matplotlib.pyplot as plt

def graficar_senal(y, sr, salida):
    plt.figure(figsize=(10, 3))
    plt.plot(y)
    plt.title("Señal de audio")
    plt.xlabel("Muestras")
    plt.ylabel("Amplitud")
    plt.tight_layout()
    plt.savefig(salida)
    plt.close()


def graficar_fft(y, sr, salida):
    N = len(y)
    fft = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(N, 1/sr)

    plt.figure(figsize=(10, 3))
    plt.plot(freqs, fft)
    plt.title("Espectro FFT")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Magnitud")
    plt.tight_layout()
    plt.savefig(salida)
    plt.close()


def graficar_espectrograma(y, sr, salida):
    S = np.abs(librosa.stft(y))
    S_dB = librosa.amplitude_to_db(S, ref=np.max)

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='log')
    plt.title("Espectrograma")
    plt.colorbar(format='%+2.0f dB')
    plt.tight_layout()
    plt.savefig(salida)
    plt.close()


def generar_graficos(path_audio: str, carpeta_salida: str):
    """
    Carga audio, genera sus gráficos y devuelve rutas de salida.
    """
    os.makedirs(carpeta_salida, exist_ok=True)

    y, sr = librosa.load(path_audio, sr=None)

    outs = {
        "senal": os.path.join(carpeta_salida, "senal.png"),
        "fft": os.path.join(carpeta_salida, "fft.png"),
        "espectrograma": os.path.join(carpeta_salida, "espectrograma.png")
    }

    graficar_senal(y, sr, outs["senal"])
    graficar_fft(y, sr, outs["fft"])
    graficar_espectrograma(y, sr, outs["espectrograma"])

    return outs
