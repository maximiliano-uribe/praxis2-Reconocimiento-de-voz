import json
import os
import threading
import queue
import pyttsx3

CONFIG_FILE = "config.json"

_default = {
    "tts_mode": "desactivar",  # desactivar | hombre | mujer
    "bg_color": "#121212",
    "fg_color": "#E6E6E6",
    "font_family": "Helvetica",
    "font_size": 14,
    "tts_rate": 160
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = _default.copy()
    else:
        data = _default.copy()

    for k, v in _default.items():
        data.setdefault(k, v)

    return data


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


_cfg = load_config()


def get_config():
    return _cfg


def update_config(newcfg):
    _cfg.update(newcfg)
    save_config(_cfg)


_engine = pyttsx3.init()
_tts_queue = queue.Queue()
_tts_thread = None
_tts_running = True


def _tts_worker():
    global _tts_running
    while _tts_running:
        try:
            text, voice_id, rate = _tts_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        try:
            _engine.setProperty("rate", rate)
            if voice_id:
                _engine.setProperty("voice", voice_id)
            _engine.say(text)
            _engine.runAndWait()
        except Exception as e:
            print("ERROR TTS:", e)


def start_tts_worker():
    global _tts_thread
    if _tts_thread is None:
        _tts_thread = threading.Thread(target=_tts_worker, daemon=True)
        _tts_thread.start()


start_tts_worker()


def list_voices():
    voices = _engine.getProperty("voices")
    return [{"id": v.id, "name": v.name, "gender": getattr(v, "gender", "")} for v in voices]


def play_text(text, voice_choice, rate):
    """
    voice_choice = desactivar | hombre | mujer
    Encola una frase para hablar en el hilo TTS.
    """
    if voice_choice == "desactivar":
        return

    voices = _engine.getProperty("voices")
    voice_id = None

    if voice_choice == "hombre":
        for v in voices:
            if "male" in getattr(v, "gender", "").lower() or "david" in v.name.lower():
                voice_id = v.id
                break

    elif voice_choice == "mujer":
        for v in voices:
            if "female" in getattr(v, "gender", "").lower() or "zira" in v.name.lower():
                voice_id = v.id
                break

    if voice_id is None:
        voice_id = voices[0].id if voices else None

    _tts_queue.put((text, voice_id, rate))


def stop_play():
    """Detiene cualquier frase pendiente en la cola."""
    with _tts_queue.mutex:
        _tts_queue.queue.clear()
    try:
        _engine.stop()
    except:
        pass
