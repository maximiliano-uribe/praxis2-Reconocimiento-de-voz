import os
import subprocess

from audio_grabar import VOICES_DIR, grabar_audio
from audio_reconocer import compare_voices, grabar_temp_audio
from voice_crypto import encrypt_with_voice, decrypt_with_voice

NOTES_DIR = "notas_privadas"
os.makedirs(NOTES_DIR, exist_ok=True)

# ==========================================================
#   UTILIDADES
# ==========================================================
def user_voice_path(user: str):
    """Devuelve la ruta del archivo WAV del usuario."""
    return os.path.join(VOICES_DIR, f"{user}.wav")

def user_notes_path(user: str):
    """Devuelve la ruta del archivo de notas cifradas del usuario."""
    return os.path.join(NOTES_DIR, f"{user}.enc")  # archivo cifrado

# ==========================================================
#   REGISTRO DE USUARIO
# ==========================================================
def register_user(name: str, duration=3):
    """
    Registra un usuario grabando su voz y guardándola en voices/<name>.wav
    """
    try:
        out = user_voice_path(name)
        grabar_audio(out, duracion=duration)
        return True
    except Exception as e:
        print("Error en registro:", e)
        return False

# ==========================================================
#   LISTAR USUARIOS
# ==========================================================
def list_registered_users():
    """Lista todos los usuarios registrados (archivos WAV)."""
    users = []
    for f in os.listdir(VOICES_DIR):
        if f.endswith(".wav"):
            users.append(f.replace(".wav", ""))
    return users

# ==========================================================
#   LOGIN POR VOZ
# ==========================================================
def login_by_voice(duration=3):
    """
    Graba una voz temporal y la compara con cada usuario registrado.
    Devuelve el usuario reconocido o None si no coincide.
    """
    temp_file = grabar_temp_audio(duration=duration)
    best_user = None
    best_score = -1  # similitud más alta

    for user in list_registered_users():
        ref_path = user_voice_path(user)
        score = compare_voices(temp_file, ref_path)

        if score > best_score:
            best_score = score
            best_user = user

    threshold = 0.8  # ajustable
    if best_score >= threshold:
        return best_user
    return None

# ==========================================================
#   NOTAS PRIVADAS CIFRADAS
# ==========================================================
def append_user_note(user: str, texto: str):
    """
    Guarda una nota cifrada usando la clave derivada de la voz del usuario.
    """
    try:
        wav = user_voice_path(user)
        encrypted = encrypt_with_voice(wav, texto)
        path = user_notes_path(user)

        # append binario
        with open(path, "ab") as f:
            f.write(encrypted + b"\n===\n")

        return True
    except Exception as e:
        print("Error al cifrar nota:", e)
        return False

def read_user_notes(user: str):
    """
    Descifra todas las notas usando la voz original del usuario.
    """
    wav = user_voice_path(user)
    path = user_notes_path(user)

    if not os.path.exists(path):
        return ""

    content = ""
    with open(path, "rb") as f:
        bloques = f.read().split(b"\n===\n")

    for b in bloques:
        if not b.strip():
            continue
        try:
            decrypted = decrypt_with_voice(wav, b)
            content += "- " + decrypted + "\n"
        except Exception:
            content += "- [No se pudo descifrar con esta voz]\n"

    return content

# ==========================================================
#   ABRIR NOTAS EN EDITOR EXTERNO
# ==========================================================
def open_user_notes_in_editor(user):
    """
    Abre un archivo temporal con notas descifradas para visualización.
    (No edita el archivo cifrado original)
    """
    notes = read_user_notes(user)
    tmp_file = f"notes_view_{user}.txt"

    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(notes)

        if os.name == "nt":  # Windows
            os.startfile(tmp_file)
        else:
            subprocess.call(["xdg-open", tmp_file])

        return True
    except Exception as e:
        print("Error abriendo notas:", e)
        return False
