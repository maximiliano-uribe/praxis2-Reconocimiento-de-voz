import os
import json
from pathlib import Path

from audio_grabar import grabar_audio, VOICES_DIR
from audio_reconocer import recognize_flow

USERS_DIR = "users"
os.makedirs(USERS_DIR, exist_ok=True)
os.makedirs(VOICES_DIR, exist_ok=True)


def user_metadata_path(username: str) -> str:
    return os.path.join(USERS_DIR, f"{username}.json")


def user_notes_path(username: str) -> str:
    return os.path.join(USERS_DIR, f"{username}_notes.txt")


def register_user(username: str, duration: int = 3) -> bool:
    """
    Registra un nuevo usuario:
    - Graba la voz y guarda en voices/<username>.wav
    - Crea users/<username>.json con metadatos
    - Crea users/<username>_notes.txt vacío
    """
    username_safe = "".join(c for c in username if c.isalnum() or c in ("_", "-")).strip()
    if not username_safe:
        return False

    voice_path = os.path.join(VOICES_DIR, f"{username_safe}.wav")

    try:
        # Grabar la voz del nuevo usuario
        grabar_audio(voice_path, duracion=duration)

        # Crear metadatos
        meta = {
            "name": username,
            "voice_file": voice_path
        }
        with open(user_metadata_path(username_safe), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        # Crear archivo de notas si no existe
        notes = user_notes_path(username_safe)
        if not os.path.exists(notes):
            with open(notes, "w", encoding="utf-8") as nf:
                nf.write(f"Notas de {username}\n\n")

        return True
    except Exception as e:
        print("Error al registrar usuario:", e)
        return False


def list_registered_users():
    """Devuelve lista de usernames registrados (basename sin extensión)."""
    users = []
    for p in Path(USERS_DIR).glob("*.json"):
        users.append(p.stem)
    return users


def login_by_voice(duration: int = 3):
    """
    Graba una muestra y utiliza recognize_flow() para obtener el mejor match.
    Recibe la condena del recognize_flow (nombre de archivo en voices).
    Devuelve username (sin .wav) si coincide con un usuario, o None.
    """
    match = recognize_flow(duration=duration)  # devuelve, por ejemplo, "juan.wav" o None
    if not match:
        return None

    # normalize returned match to username stem
    match_stem = os.path.splitext(match)[0]

    # Only accept if there's a user metadata file for that stem
    meta_path = user_metadata_path(match_stem)
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            return match_stem
        except Exception:
            return match_stem
    return None


def read_user_notes(username: str) -> str:
    path = user_notes_path(username)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def append_user_note(username: str, text: str) -> bool:
    try:
        path = user_notes_path(username)
        with open(path, "a", encoding="utf-8") as f:
            f.write(text.rstrip() + "\n\n")
        return True
    except Exception as e:
        print("Error guardar nota:", e)
        return False


def open_user_notes_in_editor(username: str):
    """
    Intenta abrir el archivo de notas con el editor por defecto.
    - En Windows, usa notepad.
    - En otros sistemas, solo imprime la ruta (puedes personalizarlo).
    """
    path = user_notes_path(username)
    if not os.path.exists(path):
        return False
    try:
        if os.name == "nt":
            os.system(f'notepad "{path}"')
            return True
        else:
            # en Linux/Mac intentaremos xdg-open / open si existen
            if os.system(f'xdg-open "{path}"') == 0:
                return True
            if os.system(f'open "{path}"') == 0:
                return True
            # si no se pudo abrir, devolvemos la ruta (para inspección)
            print(f"Archivo de notas: {path}")
            return True
    except Exception as e:
        print("No se pudo abrir el editor:", e)
        return False
