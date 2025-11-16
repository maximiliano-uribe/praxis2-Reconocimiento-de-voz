import numpy as np
from scipy.io.wavfile import read
import matplotlib.pyplot as plt

def plot_waveform(path):
    sr, data = read(path)
    data = data.astype(np.float32)

    t = np.linspace(0, len(data)/sr, num=len(data))

    plt.figure("Waveform")
    plt.title("Forma de onda")
    plt.plot(t, data)
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.show()


def analyze_voice(path):
    """Devuelve un dict con análisis completo del audio"""
    sr, data = read(path)
    data = data.astype(np.float32)

    # Normalizar si es int16
    if data.max() > 1:
        data /= 32767.0

    duration = len(data) / sr
    rms = np.sqrt(np.mean(data**2))
    max_amp = np.max(np.abs(data))

    # Zero crossing rate
    zcr = ((data[:-1] * data[1:]) < 0).sum() / duration

    # FFT
    fft = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(len(data), 1/sr)
    magnitude = np.abs(fft)
    dom_freq = freqs[np.argmax(magnitude)]

    # Picos espectrales principales
    peak_indices = magnitude.argsort()[-5:][::-1]
    peaks = [(float(freqs[i]), float(magnitude[i])) for i in peak_indices]

    return {
        "samplerate": sr,
        "duration": duration,
        "rms": rms,
        "max_amplitud": max_amp,
        "zero_cross_rate": zcr,
        "dom_freq": float(dom_freq),
        "top_peaks": peaks,
    }
