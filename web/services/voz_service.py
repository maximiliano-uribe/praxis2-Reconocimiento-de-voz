import os, uuid, json
from flask import jsonify
import numpy as np
import librosa
from datetime import datetime

# Rutas
from config import VOCES_AUTORIZADAS, VERIFICACIONES, VOCES_JSON

# Servicios
from services.audio_service import convertir_webm_a_wav, cargar_audio, normalizar

# Features mejorados
from utils.audio_features import espectro_fft, mfcc_features, similitud

# Historial
from utils.historial import registrar_evento_json


# =======================================================
# Guardar JSON (no lo usas mucho, pero lo dejo corregido)
# =======================================================
def _guardar_json(data):
    with open(VOCES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# =======================================================
# Registrar voz nueva
# =======================================================
def procesar_registro_voz(archivo, es_agregar=False):
    tmp = f"tmp_reg_{uuid.uuid4().hex[:8]}.webm"
    archivo.save(tmp)

    nombre_wav = (
        "voz_registrada.wav"
        if not es_agregar
        else archivo.filename.replace(".webm", ".wav")
    )

    path_final = os.path.join(VOCES_AUTORIZADAS, nombre_wav)

    convertir_webm_a_wav(tmp, path_final)

    if os.path.exists(tmp):
        os.remove(tmp)

    return f"Voz '{nombre_wav}' agregada correctamente."


# =======================================================
# Listar voces guardadas
# =======================================================
def listar_voces():
    return [f for f in os.listdir(VOCES_AUTORIZADAS) if f.endswith(".wav")]


# =======================================================
# Verificación de voz
# =======================================================
def procesar_verificacion_voz(archivo):

    os.makedirs(VERIFICACIONES, exist_ok=True)

    # Guardar archivo recibido
    nombre = datetime.now().strftime("%Y%m%d_%H%M%S")
    webm = os.path.join(VERIFICACIONES, nombre + ".webm")
    wav = os.path.join(VERIFICACIONES, nombre + ".wav")

    archivo.save(webm)
    convertir_webm_a_wav(webm, wav)

    # ============================
    # Cargar señal temporal
    # ============================
    y_temp, sr_temp = cargar_audio(wav)
    if y_temp is None:
        return jsonify({"error": "No se pudo procesar el audio"}), 500

    # ------------------------------
    # Extraer características robustas
    # ------------------------------
    fft_temp = espectro_fft(y_temp)
    mfcc_temp = mfcc_features(y_temp, sr_temp)  # ← ya promediado en utils

    mejor_score = -1
    mejor_archivo = None

    # ======================================================
    # Comparar contra cada voz registrada
    # ======================================================
    for f in listar_voces():

        ref_path = os.path.join(VOCES_AUTORIZADAS, f)
        y_ref, sr_ref = cargar_audio(ref_path)
        if y_ref is None:
            continue

        # ===== Recorte para señal temporal =====
        L = min(len(y_temp), len(y_ref))
        if L < 3000:  # mínimo 0.18s a 16kHz
            continue

        y1 = normalizar(y_temp[:L])
        y2 = normalizar(y_ref[:L])

        # --------- 1) Correlación temporal ---------
        corr_temp = similitud(y1, y2)

        # --------- 2) FFT (frecuencia) --------------
        fft_ref = espectro_fft(y2)
        L_fft = min(len(fft_temp), len(fft_ref))
        corr_fft = similitud(fft_temp[:L_fft], fft_ref[:L_fft])

        # --------- 3) MFCC (timbre) ----------------
        mfcc_ref = mfcc_features(y2, sr_ref)
        L_m = min(len(mfcc_temp), len(mfcc_ref))
        corr_mfcc = similitud(mfcc_temp[:L_m], mfcc_ref[:L_m])

        # ====== Score combinado ======
        score = (
            0.45 * corr_temp +
            0.35 * corr_fft +
            0.20 * corr_mfcc
        )

        if score > mejor_score:
            mejor_score = score
            mejor_archivo = f

    # ==========================
    # DECISIÓN FINAL
    # ==========================
    UMBRAL = 0.42   # valor recomendado después de FFT + MFCC

    if mejor_score >= UMBRAL:
        registrar_evento_json(
            f"Acceso OK (match={mejor_archivo}, score={mejor_score:.3f})",
            tipo="ACCESO"
        )
        return jsonify({
            "estado": "ok",
            "redirect": "/acceso",
            "match": mejor_archivo,
            "score": mejor_score,
            "acceso": True,
            "mensaje": f"acceso consedido, voz parecida a {mejor_archivo}"
        })

    # Falló
    registrar_evento_json(
        f"Acceso fallido (score={mejor_score:.3f})",
        tipo="ERROR"
    )

    return jsonify({
        "estado": "denegado",
        "match": mejor_archivo,
        "score": mejor_score,
        "acceso": False,
        "mensaje":"acceso denegado, tu voz no esta registrada"
    })
