# procesar_audio.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
from scipy.signal import find_peaks
import sounddevice as sd
from scipy.io.wavfile import write
import os

VOICES_DIR = "usuarios"
os.makedirs(VOICES_DIR, exist_ok=True)


# ==================================================
#   GRABAR VOZ
# ==================================================
def grabar_voz(duracion=3, samplerate=44100):
    """
    Graba audio desde el micrófono y devuelve el path del archivo WAV guardado.
    """
    print(f"[Grabar] Grabando {duracion} segundos...")
    audio = sd.rec(int(duracion * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    data_int16 = (audio.flatten() * 32767).astype(np.int16)

    nombre_archivo = "temp_grabacion.wav"
    write(nombre_archivo, samplerate, data_int16)
    print(f"[Grabar] Guardado temporal como {nombre_archivo}")
    return nombre_archivo, samplerate, data_int16


def guardar_voz(nombre_usuario, samplerate, data_int16):
    """
    Guarda la grabación final en la carpeta de usuarios.
    """
    safe_name = "".join(c for c in nombre_usuario if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    path = os.path.join(VOICES_DIR, f"{safe_name}.wav")
    write(path, samplerate, data_int16)
    print(f"[Guardar] Grabación guardada como {path}")
    return path


# ==================================================
#   GRAFICAR: Onda y Espectro FFT
# ==================================================
def plot_waveform(path):
    sr, data = read(path)

    if data.ndim > 1:
        data = data[:, 0]  # canal izquierdo

    data = data.astype(np.float32)
    t = np.linspace(0, len(data) / sr, len(data))

    # Forma de onda
    plt.figure(figsize=(10, 4))
    plt.title("Onda temporal de la voz")
    plt.plot(t, data)
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.grid()
    plt.show()

    # FFT
    N = len(data)
    fft_vals = np.fft.rfft(data)
    fft_freqs = np.fft.rfftfreq(N, 1 / sr)
    mag = np.abs(fft_vals)

    plt.figure(figsize=(10, 4))
    plt.title("Espectro de frecuencias (FFT)")
    plt.plot(fft_freqs, mag)
    plt.xlim(0, 4000)
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Magnitud")
    plt.grid()
    plt.show()


# ==================================================
#   ANALIZAR VOZ (info avanzada)
# ==================================================
def analyze_voice(path):
    sr, data = read(path)

    if data.ndim > 1:
        data = data[:, 0]

    data = data.astype(np.float32)

    duration = len(data) / sr
    rms = float(np.sqrt(np.mean(data ** 2)))
    max_amp = float(np.max(np.abs(data)))

    zero_cross = int(np.sum(np.abs(np.diff(np.sign(data))))) / duration / 2

    # FFT
    N = len(data)
    fft_vals = np.fft.rfft(data)
    fft_freqs = np.fft.rfftfreq(N, 1 / sr)
    mag = np.abs(fft_vals)

    dom_idx = np.argmax(mag)
    dom_freq = float(fft_freqs[dom_idx])

    # picos principales
    peaks, _ = find_peaks(mag, height=np.max(mag) * 0.2)
    top_peaks = [(float(fft_freqs[p]), float(mag[p])) for p in peaks[:10]]

    return {
        "samplerate": sr,
        "duration": duration,
        "rms": rms,
        "max_amplitud": max_amp,
        "zero_cross_rate": zero_cross,
        "dom_freq": dom_freq,
        "top_peaks": top_peaks,
        "raw_data": data
    }
