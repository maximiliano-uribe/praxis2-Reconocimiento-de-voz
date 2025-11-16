import os
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write, read

VOICES_DIR = "voices"
os.makedirs(VOICES_DIR, exist_ok=True)


def record_seconds(duration_sec=3, samplerate=44100):
    """Graba desde el micrófono y devuelve (samplerate, data_int16)."""
    print(f"[record] grabando {duration_sec}s a {samplerate}Hz...")
    audio = sd.rec(int(duration_sec * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    audio_int16 = (audio.flatten() * 32767).astype(np.int16)
    return samplerate, audio_int16


def save_wav(filename, samplerate, data_int16):
    """Guarda un array int16 a WAV."""
    write(filename, samplerate, data_int16)


def play_wav(path):
    """Reproduce un WAV (normaliza a float internamente para sounddevice)."""
    sr, data = read(path)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32767.0
    # si es mono 1D o 2D, sounddevice acepta
    sd.play(data, sr)
    sd.wait()


def record_and_save_flow():
    """
    Interactivo: graba, reproduce lo grabado, pide nombre y guarda en voices/<name>.wav
    Devuelve path guardado (o None)
    """
    try:
        dur = int(input("Duración de grabación en segundos: "))
    except Exception:
        dur = 3

    sr, data = record_seconds(dur)
    tmpfile = "temp_record.wav"
    save_wav(tmpfile, sr, data)
    print("Grabación completa. Reproduciendo...")
    play_wav(tmpfile)

    name = input("Nombre de la persona (para guardar, o ENTER para descartar): ").strip()
    if name:
        safe = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        path = os.path.join(VOICES_DIR, f"{safe}.wav")
        save_wav(path, sr, data)
        print(f"Guardado como: {path}")
        return path
    else:
        print("No guardado.")
        return None


def grabar_audio(nombre_archivo="nueva_grabacion.wav", duracion=3):
    """
    Función simple para grabar y guardar en un archivo (útil para la GUI).
    nombre_archivo puede contener ruta.
    """
    sr, data = record_seconds(duracion)
    save_wav(nombre_archivo, sr, data)
    print(f"Audio guardado en {nombre_archivo}")
    return nombre_archivo
