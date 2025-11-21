import json, os
from datetime import datetime
from config import HISTORIAL_JSON

def registrar_evento_json(evento, tipo="INFO"):
    entrada = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo,
        "evento": evento
    }

    if not os.path.exists(HISTORIAL_JSON):
        historial = []
    else:
        with open(HISTORIAL_JSON, "r", encoding="utf-8") as f:
            try: historial = json.load(f)
            except: historial = []

    historial.append(entrada)

    with open(HISTORIAL_JSON, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4)

def leer_historial_json():
    if not os.path.exists(HISTORIAL_JSON):
        return []
    with open(HISTORIAL_JSON, "r", encoding="utf-8") as f:
        return json.load(f)
