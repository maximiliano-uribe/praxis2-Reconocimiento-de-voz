from flask import Blueprint, request, jsonify
from services.voz_service import procesar_registro_voz, procesar_verificacion_voz, listar_voces
from utils.historial import registrar_evento_json

voz_bp = Blueprint("voz", __name__)

@voz_bp.route("/listar_voces")
def listar():
    return jsonify(listar_voces())

@voz_bp.route("/guardar_voz", methods=["POST"])
def guardar_voz():
    archivo = request.files.get("audio")
    if not archivo:
        return jsonify({"mensaje":"❌ No se envió audio."}), 400

    mensaje = procesar_registro_voz(archivo)
    registrar_evento_json("Se guardó un nuevo audio (voz_registrada.wav)", tipo="ACCESO")

    return jsonify({"mensaje": mensaje, "acceso": False})

@voz_bp.route("/agregar_voz", methods=["POST"])
def agregar_voz():
    archivo = request.files.get("archivo")
    if not archivo:
        return "❌ No se subió ningún archivo.", 400

    return procesar_registro_voz(archivo, es_agregar=True)

@voz_bp.route("/verificar_voz", methods=["POST"])
def verificar_voz():
    archivo = request.files.get("audio")
    if not archivo:
        return jsonify({"error":"No se recibió audio"}), 400

    return procesar_verificacion_voz(archivo)
