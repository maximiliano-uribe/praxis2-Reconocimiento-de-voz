# audio_reconocer.py
import os
import numpy as np
import soundfile as sf
import sounddevice as sd

VOICES_DIR = "voices"
TEMP_AUDIO = "temp_rec.wav"
os.makedirs(VOICES_DIR, exist_ok=True)


# =============================================================
#   Funciones internas
# =============================================================

def grabar_temp_audio(duration=4, samplerate=44100):
    """Graba audio temporal para reconocimiento."""
    print(f"Grabando para reconocimiento ({duration} s)...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    sf.write(TEMP_AUDIO, audio, samplerate)
    return TEMP_AUDIO


def extract_voice_features(filepath):
    """
    Extrae características simples de la voz:
    - RMS (energía)
    - Zero crossing rate
    - Frecuencia dominante (dom_freq)
    """
    audio, fs = sf.read(filepath)

    if audio.ndim > 1:
        audio = audio[:, 0]

    # Normalizar
    audio = audio / (np.max(np.abs(audio)) + 1e-9)

    rms = np.sqrt(np.mean(audio ** 2))
    zcr = np.mean(np.abs(np.diff(np.sign(audio))))
    fft_vals = np.abs(np.fft.rfft(audio))
    dom_freq = np.argmax(fft_vals) * fs / len(audio)

    return np.array([rms, zcr, dom_freq])


def compare_voices(voice1, voice2):
    """
    Comparación simple basada en RMS, ZCR y frecuencia dominante.
    Devuelve un valor de similitud entre 0 y 1 (1 = muy similar).
    """
    v1 = extract_voice_features(voice1)
    v2 = extract_voice_features(voice2)

    # Diferencias normalizadas
    diff_rms = abs(v1[0] - v2[0])
    diff_zcr = abs(v1[1] - v2[1])
    diff_freq = abs(v1[2] - v2[2])

    # Similaridad general
    sim = 1 - ((diff_rms * 2) + (diff_zcr * 5) + (diff_freq / 500))
    sim = max(0.0, min(1.0, sim))
    return sim


# =============================================================
#   Flujo principal de reconocimiento
# =============================================================

def recognize_flow(duration=4):
    """
    Compara la voz grabada con las voces registradas
    y retorna el nombre del usuario si coincide.
    """
    temp_file = grabar_temp_audio(duration)

    best_user = None
    best_score = 0
    threshold = 0.7  # más permisivo

    for file in os.listdir(VOICES_DIR):
        if not file.endswith(".wav"):
            continue

        user = file.replace(".wav", "")
        ref_path = os.path.join(VOICES_DIR, file)

        sim = compare_voices(temp_file, ref_path)
        print(f"Comparación con {user}: {sim:.3f}")

        if sim > best_score:
            best_score = sim
            best_user = user

    if best_score >= threshold:
        print(f"Voz reconocida como {best_user} (sim={best_score:.3f})")
        return best_user

    print("No se reconoció la voz")
    return None
