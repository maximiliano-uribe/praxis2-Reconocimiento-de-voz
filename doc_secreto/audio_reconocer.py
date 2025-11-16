import os
import numpy as np
from scipy.io.wavfile import read
from audio_grabar import record_seconds, save_wav, VOICES_DIR
from procesar_audio import plot_waveform

os.makedirs(VOICES_DIR, exist_ok=True)


def load_wav(path):
    sr, data = read(path)
    # Normalizar a float32 en rango [-1, 1]
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32767.0
    if data.ndim > 1:
        data = data[:, 0]
    return sr, data


def energy_of(data):
    return np.sum(data ** 2)


def recognize_flow(duration=3):
    """
    Graba `duration` segundos, guarda un temporal, compara con WAVs en VOICES_DIR
    y muestra la forma de onda del temporal. Devuelve el nombre del archivo
    más similar (basename) o None.
    """
    print(f"[recognize] Grabando {duration} segundos para reconocimiento...")
    sr, rec_int16 = record_seconds(duration)
    # Normalizar
    rec = rec_int16.astype(np.float32) / 32767.0

    # Guardar temporal para poder graficar con plot_waveform
    tmpfile = "temp_recognize.wav"
    save_wav(tmpfile, sr, rec_int16)

    best_match = None
    best_diff = None

    print("[recognize] Comparando con voces guardadas...")
    for fname in os.listdir(VOICES_DIR):
        if not fname.lower().endswith(".wav"):
            continue
        path = os.path.join(VOICES_DIR, fname)
        try:
            sr2, data2 = load_wav(path)
        except Exception:
            continue

        # Alinear longitudes para comparación simple por energía
        m = min(len(data2), len(rec))
        if m <= 0:
            continue

        e1 = energy_of(data2[:m])
        e2 = energy_of(rec[:m])
        diff = abs(e1 - e2)

        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_match = fname

    # Mostrar gráfica del audio grabado (usa el temporal guardado)
    try:
        plot_waveform(tmpfile)
    except Exception:
        pass

    if best_match:
        print(f"[recognize] La voz coincide más con: {best_match}")
        return best_match
    else:
        print("[recognize] No hay coincidencias.")
        return None
