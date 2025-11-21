from flask import Blueprint, request, jsonify, current_app
import os
from services.graficos_service import generar_graficos
import config

graficos_bp = Blueprint('graficos', __name__)

@graficos_bp.route('/graficar_voz', methods=['POST'])
def graficar_voz():
    data = request.get_json()
    archivo = data.get('archivo')

    if not archivo:
        return jsonify({"error": "No se especificó un archivo"}), 400

    # Ruta completa del audio
    if os.path.exists(os.path.join(config.VOCES_AUTORIZADAS, archivo)):
        path_audio = os.path.join(config.VOCES_AUTORIZADAS, archivo)
    elif os.path.exists(os.path.join(config.VERIFICACIONES, archivo)):
        path_audio = os.path.join(config.VERIFICACIONES, archivo)
    else:
        return jsonify({"error": "Archivo no encontrado"}), 404

    # Carpeta de salida de imágenes dentro de static/
    nombre_carpeta = os.path.splitext(archivo)[0]
    carpeta_salida = os.path.join(config.STATIC_FOLDER, nombre_carpeta)

    rutas = generar_graficos(path_audio, carpeta_salida)

    # Rutas relativas para el frontend
    return jsonify({
        "onda": os.path.join(nombre_carpeta, "senal.png"),
        "fft": os.path.join(nombre_carpeta, "fft.png"),
        "spec": os.path.join(nombre_carpeta, "espectrograma.png")
    })
