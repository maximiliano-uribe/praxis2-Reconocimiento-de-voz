from flask import Flask, render_template, request, jsonify, redirect, url_for
import numpy as np
import librosa
import librosa.display
import hashlib
import soundfile as sf
import uuid
import hmac
import io, base64, os, json
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from scipy.io import wavfile
from datetime import datetime

app = Flask(__name__)

# --- Rutas / archivos ---
os.makedirs("database", exist_ok=True)
os.makedirs("static/graficos", exist_ok=True)
os.makedirs("voces_autorizadas", exist_ok=True)

VOCES_AUTORIZADAS = "voces_autorizadas"
HISTORIAL_JSON = "database/historial.json"
VOCES_JSON = "database/voces.json"
HUELLA_BASE = "huella_base.txt"
CLAVE_FILE = "clave.txt"

# --- Asegurar JSON ---
def _asegurar_json(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)

_asegurar_json(HISTORIAL_JSON)
_asegurar_json(VOCES_JSON)

# ======================================================
#                  FUNCIONES IMPORTANTES
# ======================================================

def generar_huella(audio_path):
    """Genera huella (SHA256 de MFCC promedio)"""
    y, sr = librosa.load(audio_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return hashlib.sha256(mfcc.mean(axis=1).tobytes()).hexdigest()


def obtener_lista_voces():
    carpeta = VOCES_AUTORIZADAS
    return [f for f in os.listdir(carpeta) if f.lower().endswith(".wav")]


def guardar_voz(data, sr, nombre=None):
    """Guarda array 'data' como wav en voces_autorizadas con nombre único si no se da."""
    if nombre is None:
        nombre = f"voz_{uuid.uuid4().hex[:8]}.wav"
    ruta = os.path.join(VOCES_AUTORIZADAS, nombre)
    sf.write(ruta, data, sr)
    return nombre


def convertir_webm_a_wav(path_webm, path_wav, sr_target=16000):
    """
    Convierte un archivo .webm (o cualquier formato que libsea soporte) a WAV.
    Devuelve la ruta wav.
    """
    y, sr = librosa.load(path_webm, sr=sr_target)
    sf.write(path_wav, y, sr_target)
    return path_wav


# ======================================================
#             FUNCIÓN NUEVA Y CORRECTA DE GRÁFICAS
# ======================================================

def graficar_voz(nombre_archivo):
    ruta_audio = os.path.join(VOCES_AUTORIZADAS, nombre_archivo)
    y, sr = librosa.load(ruta_audio)

    # Carpeta de salida de esta voz
    carpeta_salida = os.path.join("static", "graficos", nombre_archivo.replace(".wav", ""))
    os.makedirs(carpeta_salida, exist_ok=True)

    rutas = {}

    # ==========================
    # Onda
    # ==========================
    plt.figure(figsize=(6,3))
    librosa.display.waveshow(y, sr=sr)
    ruta1 = os.path.join(carpeta_salida, "onda.png")
    plt.savefig(ruta1)
    plt.close()
    rutas["onda"] = ruta1.replace("static/", "")

    # ==========================
    # FFT
    # ==========================
    Y = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(len(y), 1/sr)

    plt.figure(figsize=(6,3))
    plt.plot(freqs, Y)
    ruta2 = os.path.join(carpeta_salida, "fft.png")
    plt.savefig(ruta2)
    plt.close()
    rutas["fft"] = ruta2.replace("static/", "")

    # ==========================
    # Espectrograma
    # ==========================
    S = librosa.stft(y)
    S_db = librosa.amplitude_to_db(np.abs(S))

    plt.figure(figsize=(6,3))
    librosa.display.specshow(S_db, sr=sr, x_axis="time", y_axis="hz")
    ruta3 = os.path.join(carpeta_salida, "espectrograma.png")
    plt.savefig(ruta3)
    plt.close()
    rutas["espectrograma"] = ruta3.replace("static/", "")

    return rutas


# ======================================================
#                     RUTA DE ANÁLISIS
# ======================================================
@app.route("/analisis_voces", methods=["GET"])
def analisis_voces():
    lista = obtener_lista_voces()
    seleccionado = request.args.get("voz", None)
    graficos = None

    if seleccionado:
        graficos = graficar_voz(seleccionado)

    return render_template(
        "analisis_voces.html",
        lista_voces=lista,
        seleccion=seleccionado,
        graficos=graficos
    )


# ======================================================
#                  RESTO DE TU CÓDIGO (NO TOCADO)
# ======================================================

def registrar_evento_json(evento, tipo="INFO"):
    _asegurar_json(HISTORIAL_JSON)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entrada = {"fecha": fecha, "tipo": tipo, "evento": evento}
    try:
        with open(HISTORIAL_JSON, "r", encoding="utf-8") as f:
            historial = json.load(f)
    except Exception:
        historial = []
    historial.append(entrada)
    with open(HISTORIAL_JSON, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4)


def leer_historial_json():
    if not os.path.exists(HISTORIAL_JSON):
        return []
    with open(HISTORIAL_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

# ELIMINADO: generar_graficas()  ← Ya no se usa.

@app.route("/historial")
def historial():
    registros = leer_historial_json()
    registros_texto = [f"{r.get('fecha')} | {r.get('tipo')} | {r.get('evento')}" for r in registros[::-1]]
    return render_template("historial.html", registros=registros_texto)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar')
def analizar():
    return render_template('analisis.html')

@app.route('/contraseña')
def contraseña():
    return render_template('contraseña.html')

@app.route('/acceso')
def acceso():
    registrar_evento_json("Usuario entró a la página de acceso", tipo="ACCESO")
    return render_template('acceso.html')

@app.route('/archivos')
def archivos():
    return render_template('archivos.html')

@app.route('/configuracion')
def configuracion():
    return render_template('configuracion.html')

@app.route('/analisis')
def analisis():
    return render_template('analisis_voces.html')

@app.route('/registrar')
def registrar():
    return render_template('registrar.html')

@app.route('/abrir_pdf', methods=['POST'])
def abrir_pdf():
    # Luego redirigimos al archivo real
    return redirect('/static/reconocimiento de voz (1).pdf')

@app.route('/agregar_pdf', methods=['POST'])
def agregar_pdf():
    archivo = request.files['archivo']
    if archivo:
        nombre = archivo.filename
        ruta_guardado = os.path.join('static', nombre)
        archivo.save(ruta_guardado)
    return redirect(url_for('archivos'))

@app.route('/graficar_voz', methods=['POST'])
def graficar_voz():
    data = request.get_json()
    archivo = data.get("archivo")

    if not archivo:
        return jsonify({"error": "No se recibió archivo"}), 400

    ruta_audio = os.path.join("voces_autorizadas", archivo)

    if not os.path.exists(ruta_audio):
        return jsonify({"error": "El archivo no existe"}), 404

    # Cargar audio
    y, sr = librosa.load(ruta_audio, sr=None)

    # Carpeta donde guardaremos las gráficas
    output_dir = os.path.join("static", "graficos")
    os.makedirs(output_dir, exist_ok=True)

    # Rutas relativas para que HTML funcione
    onda_rel = "graficos/onda.png"
    fft_rel  = "graficos/fft.png"
    spec_rel = "graficos/espectrograma.png"

    # Rutas absolutas
    onda_path = os.path.join("static", onda_rel)
    fft_path  = os.path.join("static", fft_rel)
    spec_path = os.path.join("static", spec_rel)

    # --------------------------
    # 1) GRÁFICA DE ONDA
    # --------------------------
    plt.figure(figsize=(6, 3))
    plt.plot(y)
    plt.title("Onda de Voz")
    plt.tight_layout()
    plt.savefig(onda_path, dpi=120)
    plt.close()

    # --------------------------
    # 2) FFT
    # --------------------------
    Y = np.abs(np.fft.rfft(y))
    f = np.fft.rfftfreq(len(y), 1/sr)

    plt.figure(figsize=(6, 3))
    plt.plot(f, Y)
    plt.title("Espectro FFT")
    plt.tight_layout()
    plt.savefig(fft_path, dpi=120)
    plt.close()

    # --------------------------
    # 3) ESPECTROGRAMA
    # --------------------------
    S = librosa.stft(y)
    S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

    plt.figure(figsize=(6, 3))
    librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(label="dB")
    plt.title("Espectrograma")
    plt.tight_layout()
    plt.savefig(spec_path, dpi=120)
    plt.close()

    # Devolver rutas (relativas)
    return jsonify({
        "onda": onda_rel,
        "fft": fft_rel,
        "spec": spec_rel
    })



# ======================================================
#             RUTAS DE SUBIDA Y VERIFICACIÓN
# ======================================================

@app.route('/agregar_voz', methods=['POST'])
def agregar_voz():
    """
    Recibe un archivo de voz (puede ser .webm o .wav).
    Si llega .webm lo convierte a .wav y guarda la wav en voces_autorizadas.
    Guarda la huella en VOCES_JSON.
    """
    archivo = request.files.get('archivo')
    if not archivo:
        return "❌ No se subió ningún archivo.", 400

    nombre_original = archivo.filename
    nombre_base, ext = os.path.splitext(nombre_original)
    ext = ext.lower()

    # Guardar temporalmente el archivo subido
    tmp_name = f"tmp_upload_{uuid.uuid4().hex[:8]}{ext}"
    archivo.save(tmp_name)

    try:
        if ext == ".webm" or ext == ".ogg" or ext == ".m4a" or ext == ".mp4":
            # convertir a wav
            nombre_wav = f"{nombre_base}.wav"
            ruta_final = os.path.join(VOCES_AUTORIZADAS, nombre_wav)
            convertir_webm_a_wav(tmp_name, ruta_final)
        elif ext == ".wav":
            nombre_wav = nombre_original
            ruta_final = os.path.join(VOCES_AUTORIZADAS, nombre_wav)
            os.replace(tmp_name, ruta_final)
        else:
            # formato no soportado
            os.remove(tmp_name)
            return "Formato no soportado", 400

        # Generar huella y guardar en VOCES_JSON
        try:
            huella = generar_huella(ruta_final)
        except Exception as e:
            print("Error generando huella:", e)
            huella = ""

        # Cargar voces JSON (lista de dicts)
        try:
            with open(VOCES_JSON, "r", encoding="utf-8") as f:
                voces_list = json.load(f)
        except Exception:
            voces_list = []

        voces_list.append({
            "archivo": nombre_wav,
            "huella": huella,
            "fecha": datetime.now().isoformat()
        })

        with open(VOCES_JSON, "w", encoding="utf-8") as f:
            json.dump(voces_list, f, indent=4)

        registrar_evento_json(f"Se agregó nueva voz autorizada: {nombre_wav}", tipo="ARCHIVO")
        return f"✅ Voz '{nombre_wav}' agregada correctamente."

    finally:
        # limpiar temporal si sigue existiendo
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

@app.route("/listar_voces")
def listar_voces():
    voces = [f for f in os.listdir(VOCES_AUTORIZADAS) if f.endswith(".wav")]
    return jsonify(voces)

@app.route('/guardar_voz', methods=['POST'])
def guardar_voz():
    """
    Guarda la voz base (voz_registrada.wav). Recibe .webm desde el navegador,
    lo convierte a wav y lo guarda como voz_registrada.wav, además guarda huella_base.txt
    """
    archivo = request.files.get('audio')
    if not archivo:
        return jsonify({"mensaje":"❌ No se envió audio."}), 400

    # Guardar temporal .webm
    tmp = f"tmp_reg_{uuid.uuid4().hex[:8]}.webm"
    archivo.save(tmp)

    try:
        # Convertir a wav y guardar como voz_registrada.wav
        salida = os.path.join(VOCES_AUTORIZADAS, "voz_registrada.wav")
        convertir_webm_a_wav(tmp, salida)

        # Generar huella base
        huella = generar_huella(salida)
        with open(HUELLA_BASE, 'w', encoding='utf-8') as f:
            f.write(huella)

        registrar_evento_json("Se guardó un nuevo audio del usuario (voz_registrada.wav)", tipo="ACCESO")
        return jsonify({"mensaje": "✅ Voz registrada correctamente.", "acceso": False})

    except Exception as e:
        print("Error en guardar_voz:", e)
        return jsonify({"mensaje":"Error al procesar audio"}), 500

    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


@app.route('/borrar_historial', methods=["POST"])
def borrar_historial():
    # Vacía el historial JSON
    with open(HISTORIAL_JSON, "w", encoding="utf-8") as f:
        json.dump([], f)
    registrar_evento_json("Historial borrado por el usuario", tipo="ACCION")
    return redirect(url_for("historial"))


# ======================================================
#               VERIFICACIÓN DE VOZ / CLAVE
# ======================================================

@app.route('/guardar_clave', methods=['POST'])
def guardar_clave():
    clave = request.form.get("clave", "")
    if not clave:
        return "❌ Debes enviar una contraseña.", 400
    hash_clave = hashlib.sha256(clave.encode()).hexdigest()
    with open(CLAVE_FILE, "w") as f:
        f.write(hash_clave)
    registrar_evento_json("Se guardó una nueva contraseña", tipo="ACCESO")
    return redirect(url_for("acceso"))


@app.route('/verificar_clave', methods=['POST'])
def verificar_clave():
    """
    Verifica la contraseña enviada por el formulario.
    Si coincide con el hash guardado en CLAVE_FILE, muestra acceso.html.
    Si no coincide o no se envía, muestra denegado.html o devuelve error.
    """
    clave_ingresada = request.form.get('clave', '').strip()

    # Si el usuario no envió nada, mostramos la página denegado (como antes)
    if clave_ingresada == '':
        return render_template("denegado.html")

    # Verificar que exista archivo de clave
    if not os.path.exists(CLAVE_FILE):
        # Opcional: podrías redirigir a configuración para crear la clave
        return "❌ No hay clave guardada aún.", 400

    # Leer hash guardado y comparar de forma segura
    with open(CLAVE_FILE, "r", encoding="utf-8") as f:
        hash_guardado = f.read().strip()

    hash_ingresada = hashlib.sha256(clave_ingresada.encode("utf-8")).hexdigest()

    if hmac.compare_digest(hash_guardado, hash_ingresada):
        registrar_evento_json("Acceso por contraseña exitoso", tipo="ACCESO")
        return render_template("acceso.html")
    else:
        registrar_evento_json("Acceso por contraseña fallido", tipo="ERROR")
        return render_template("denegado.html")


@app.route("/verificar_voz", methods=["POST"])
def verificar_voz():
    """
    Verifica una grabación enviada por el cliente comparándola con
    todos los audios en la carpeta VOCES_AUTORIZADAS.
    Devuelve JSON con resultado y (si corresponde) redirect.
    Ahora acepta .webm: lo convierte internamente a wav antes de comparar.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No se recibió audio"}), 400

    archivo = request.files["audio"]

    # Guardar audio temporal (webm)
    tmp_webm = f"tmp_ver_{uuid.uuid4().hex[:8]}.webm"
    archivo.save(tmp_webm)

    try:
        # Convertir a wav temporal
        tmp_wav = f"tmp_ver_{uuid.uuid4().hex[:8]}.wav"
        convertir_webm_a_wav(tmp_webm, tmp_wav, sr_target=16000)

        # Cargar audio temporal con librosa
        y_temp, sr_temp = librosa.load(tmp_wav, sr=16000)

        # Asegurar que la carpeta existe
        if not os.path.exists(VOCES_AUTORIZADAS):
            return jsonify({"error": "No hay voces registradas"}), 400

        archivos_voces = [f for f in os.listdir(VOCES_AUTORIZADAS) if f.lower().endswith(".wav")]
        if len(archivos_voces) == 0:
            return jsonify({"error": "No hay voces registradas"}), 400

        coincidencias = 0
        mejor_coef = -1.0
        mejor_nombre = None

        for nombre in archivos_voces:
            ruta = os.path.join(VOCES_AUTORIZADAS, nombre)
            try:
                y_ref, sr_ref = librosa.load(ruta, sr=16000)
            except Exception:
                continue  # skip si falla cargar referencia

            # Normalizar y recortar a la misma longitud
            min_len = min(len(y_temp), len(y_ref))
            if min_len < 100:  # audio muy corto, saltar
                continue
            y_temp_c = y_temp[:min_len]
            y_ref_c = y_ref[:min_len]

            # Normalizar energía para reducir efecto de volumen
            y_temp_c = y_temp_c / (np.linalg.norm(y_temp_c) + 1e-9)
            y_ref_c = y_ref_c / (np.linalg.norm(y_ref_c) + 1e-9)

            # correlación (coeficiente de Pearson)
            try:
                coef = np.corrcoef(y_temp_c, y_ref_c)[0, 1]
            except Exception:
                coef = 0.0

            if coef > mejor_coef:
                mejor_coef = coef
                mejor_nombre = nombre

            # umbral: 0.80 es razonable pero puede ajustarse
            if coef >= 0.80:
                coincidencias += 1

        # borrar temporales
        try:
            if os.path.exists(tmp_webm):
                os.remove(tmp_webm)
            if os.path.exists(tmp_wav):
                os.remove(tmp_wav)
        except:
            pass

        # registrar en historial (guardar info del mejor match también)
        if coincidencias > 0:
            registrar_evento_json(f"Acceso por voz exitoso (match: {mejor_nombre}, coef={mejor_coef:.3f})", tipo="ACCESO")
            # devuelvo ambos formatos por compatibilidad
            return jsonify({"estado": "ok", "redirect": "/acceso", "match": mejor_nombre, "coef": mejor_coef, "acceso": True, "mensaje": "Acceso concedido"})
        else:
            registrar_evento_json(f"Acceso por voz fallido (mejor coef={mejor_coef:.3f})", tipo="ERROR")
            return jsonify({"estado": "denegado", "match": mejor_nombre, "coef": mejor_coef, "acceso": False, "mensaje": "Voz no coincide"})

    except Exception as e:
        # limpiar temporales si hubo error
        try:
            if os.path.exists(tmp_webm):
                os.remove(tmp_webm)
        except:
            pass
        print("Error en verificar_voz:", e)
        return jsonify({"error": f"Error procesando audio: {e}"}), 500


# ======================================================
#                       EJECUCIÓN
# ======================================================
if __name__ == '__main__':
    import webbrowser, threading
    threading.Timer(1.5, lambda: webbrowser.open_new("http://127.0.0.1:5000")).start()
    app.run(debug=True, use_reloader=False)
