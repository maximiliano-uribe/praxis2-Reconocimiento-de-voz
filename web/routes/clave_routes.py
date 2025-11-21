from flask import Blueprint, render_template, redirect, url_for
from utils.historial import registrar_evento_json
from utils.historial import leer_historial_json

clave_bp = Blueprint("clave", __name__)

@clave_bp.route("/")
def index():
    return render_template("index.html")

@clave_bp.route("/analizar")
def analizar():
    return render_template("analisis.html")

@clave_bp.route("/contraseña")
def contraseña():
    return render_template("contraseña.html")

@clave_bp.route("/acceso")
def acceso():
    registrar_evento_json("Usuario entró a la página de acceso", tipo="ACCESO")
    return render_template("acceso.html")

@clave_bp.route("/archivos")
def archivos():
    return render_template("archivos.html")

@clave_bp.route("/configuracion")
def configuracion():
    return render_template("configuracion.html")

@clave_bp.route("/analisis")
def analisis():
    return render_template("analisis_voces.html")

@clave_bp.route("/registrar")
def registrar():
    return render_template("registrar.html")

@clave_bp.route("/historial")
def historial():
    registros = leer_historial_json()
    registros_texto = [
        f"{r.get('fecha')} | {r.get('tipo')} | {r.get('evento')}"
        for r in registros[::-1]
    ]
    return render_template("historial.html", registros=registros_texto)

@clave_bp.route('/borrar_historial', methods=["POST"])
def borrar_historial():
    import json
    from config import HISTORIAL_JSON

    with open(HISTORIAL_JSON, "w", encoding="utf-8") as f:
        json.dump([], f)

    registrar_evento_json("Historial borrado por el usuario", tipo="ACCION")
    return redirect(url_for("main.historial"))
