from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify
from utils.historial import registrar_evento_json
from utils.historial import leer_historial_json
import os
from werkzeug.utils import secure_filename
from urllib.parse import quote
from config import PDFS_FOLDER, CLAVE_FILE

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/analizar")
def analizar():
    return render_template("analisis.html")

@main_bp.route("/contraseña")
def contraseña():
    return render_template("contraseña.html")

@main_bp.route("/acceso")
def acceso():
    registrar_evento_json("Usuario entró a la página de acceso", tipo="ACCESO")
    return render_template("acceso.html")

@main_bp.route("/archivos")
def archivos():
    return render_template("archivos.html")

@main_bp.route("/configuracion")
def configuracion():
    return render_template("configuracion.html")

@main_bp.route("/analisis")
def analisis():
    return render_template("analisis_voces.html")

@main_bp.route("/registrar")
def registrar():
    return render_template("registrar.html")

@main_bp.route("/historial")
def historial():
    registros = leer_historial_json()
    registros_texto = [
        f"{r.get('fecha')} | {r.get('tipo')} | {r.get('evento')}"
        for r in registros[::-1]
    ]
    return render_template("historial.html", registros=registros_texto)

@main_bp.route('/borrar_historial', methods=["POST"])
def borrar_historial():
    import json
    from config import HISTORIAL_JSON

    with open(HISTORIAL_JSON, "w", encoding="utf-8") as f:
        json.dump([], f)

    registrar_evento_json("Historial borrado por el usuario", tipo="ACCION")
    return redirect(url_for("main.historial"))

@main_bp.route('/agregar_pdf', methods=['POST'])
def agregar_pdf():
    archivo = request.files.get('archivo')
    if archivo:
        # Asegura que el nombre sea seguro
        nombre_pdf = secure_filename(archivo.filename)

        # Carpeta de destino
        carpeta_destino = os.path.join('static', 'pdfs')
        os.makedirs(carpeta_destino, exist_ok=True)

        # Ruta completa del archivo
        ruta_guardado = os.path.join(PDFS_FOLDER, nombre_pdf)

        # Guardar el archivo
        archivo.save(ruta_guardado)

        print(f"Archivo guardado en: {ruta_guardado}")  # Para verificar en consola

    return redirect(url_for('main.archivos'))

@main_bp.route('/abrir_pdf', methods=['GET'])
def abrir_pdf():
    nombre_pdf = request.args.get('archivo')
    if not nombre_pdf:
        return "No se indicó archivo", 400

    # Ruta absoluta en disco
    ruta_pdf = os.path.join(PDFS_FOLDER, nombre_pdf)
    if not os.path.exists(ruta_pdf):
        return "Archivo no encontrado", 404

    pdf_url = '/static/pdfs/' + quote(nombre_pdf, safe='')

    return redirect(pdf_url)

@main_bp.route('/guardar_clave', methods=['POST'])
def guardar_clave():
    nueva_clave = request.form.get('clave')
    if not nueva_clave:
        flash("Debe ingresar una contraseña", "error")
        return redirect(url_for('main_bp.configuracion'))

    # Guardar la contraseña en el archivo
    os.makedirs(os.path.dirname(CLAVE_FILE), exist_ok=True)
    with open(CLAVE_FILE, 'w', encoding='utf-8') as f:
        f.write(nueva_clave)

    flash("Contraseña guardada correctamente", "success")
    return redirect(url_for('main.configuracion'))

@main_bp.route('/verificar_clave', methods=['POST'])
def verificar_clave():
    clave_ingresada = request.form.get('clave')
    if not clave_ingresada:
        flash("Ingresa una contraseña", "error")
        return redirect(url_for('main.acceso'))  # redirige al formulario de acceso

    # Verificar que el archivo exista
    if not os.path.exists(CLAVE_FILE):
        flash("No hay contraseña configurada", "error")
        return redirect(url_for('main.acceso'))

    # Leer la contraseña guardada
    with open(CLAVE_FILE, 'r', encoding='utf-8') as f:
        clave_guardada = f.read().strip()

    if clave_ingresada == clave_guardada:
        flash("Acceso concedido", "success")
        return redirect(url_for('main.acceso'))  # o la página principal del usuario
    else:
        flash("Contraseña incorrecta", "error")
        return redirect(url_for('main.acceso'))