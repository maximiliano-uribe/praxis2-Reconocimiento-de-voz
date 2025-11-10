from flask import Flask, render_template, request, jsonify, redirect, url_for
import numpy as np
import librosa
import soundfile as sf
import hashlib
import hmac
import io, base64, os
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import resample

app = Flask(__name__)

# === Funciones auxiliares ===
def generar_huella(audio_path):
    y, sr = librosa.load(audio_path)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return hashlib.sha256(mfcc.mean(axis=1).tobytes()).hexdigest()

def generar_graficas(archivo_audio, nombre_salida):
    fs, data = wavfile.read(archivo_audio)

    # --- Onda ---
    plt.figure(figsize=(6,3))
    plt.plot(data)
    plt.title("Onda de la voz")
    plt.savefig(f"static/{nombre_salida}_onda.png")
    plt.close()

    # --- FFT ---
    fft = np.abs(np.fft.fft(data))
    freqs = np.fft.fftfreq(len(data), 1/fs)
    plt.figure(figsize=(6,3))
    plt.plot(freqs[:len(freqs)//2], fft[:len(fft)//2])
    plt.title("Espectro de frecuencia (FFT)")
    plt.savefig(f"static/{nombre_salida}_fft.png")
    plt.close()



# === Rutas principales ===
@app.route("/graficas_voces")
def graficas_voces():
    archivos = ["voz_registrada.wav"]
    imagenes = []

    for archivo in archivos:
        try:
            fs, data = wavfile.read(archivo)
            if len(data.shape) > 1:
                data = data[:, 0]  # Si es estéreo, toma solo un canal

            # --- Señal en el tiempo ---
            tiempo = np.linspace(0, len(data)/fs, num=len(data))
            plt.figure(figsize=(6, 3))
            plt.plot(tiempo, data, color='cyan')
            plt.title(f"Onda temporal - {archivo}")
            plt.xlabel("Tiempo [s]")
            plt.ylabel("Amplitud")
            plt.grid(True)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close()
            buf.seek(0)
            img_tiempo = base64.b64encode(buf.read()).decode('utf-8')

            # --- Espectro FFT ---
            fft_data = np.abs(np.fft.rfft(data))
            freqs = np.fft.rfftfreq(len(data), 1/fs)
            plt.figure(figsize=(6, 3))
            plt.plot(freqs, fft_data, color='orange')
            plt.title(f"Espectro FFT - {archivo}")
            plt.xlabel("Frecuencia [Hz]")
            plt.ylabel("Magnitud")
            plt.grid(True)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close()
            buf.seek(0)
            img_fft = base64.b64encode(buf.read()).decode('utf-8')

            imagenes.append({
                "archivo": archivo,
                "onda": img_tiempo,
                "fft": img_fft
            })

        except Exception as e:
            print(f"Error con {archivo}: {e}")

    return jsonify(imagenes)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar')
def analizar():
    return render_template('analisis.html')

@app.route('/registrar')
def registrar():
    return render_template('registrar.html')

@app.route('/contraseña')
def contraseña():
    return render_template('contraseña.html')

@app.route('/acceso')
def acceso():
    return render_template('acceso.html')

@app.route('/analisis')
def analisis():
    return render_template('analisis_voces.html')

@app.route('/historial')
def historial():
    return render_template('historial.html')

@app.route('/archivos')
def archivos():
    return render_template('archivos.html')

@app.route('/entrenamiento')
def entrenamiento():
    return render_template('entrenamiento.html')

@app.route('/configuracion')
def configuracion():
    return render_template('configuracion.html')

# === Rutas funcionales ===
@app.route('/subir_audio', methods=['POST'])
def subir_audio():
    if 'audio' not in request.files:
        return "No se envió archivo", 400

    archivo = request.files['audio']
    if archivo.filename == '':
        return "Archivo vacío", 400

    # Guarda el archivo temporalmente (probablemente es .webm)
    entrada = 'voz_temp.webm'
    salida = 'voz_temp.wav'
    archivo.save(entrada)
    print(f"Archivo recibido: {entrada} ({os.path.getsize(entrada)} bytes)")

    # Convierte a WAV usando ffmpeg
    try:
        os.system(f'ffmpeg -y -i "{entrada}" -ac 1 -ar 44100 "{salida}"')
        print("Conversión a WAV completada:", salida)
    except Exception as e:
        print("Error al convertir audio:", e)
        return "Error al convertir el audio", 500

    # Verifica si el archivo resultante existe y tiene tamaño válido
    if not os.path.exists(salida) or os.path.getsize(salida) == 0:
        print("Error: archivo WAV no generado correctamente")
        return "Error al procesar el audio", 500

    # Genera la gráfica
    try:
        grafica = generar_grafica(salida)
        return jsonify({"grafica": grafica})
    except Exception as e:
        print("Error al analizar el audio:", e)
        return "Error en análisis", 500

@app.route('/agregar_voz', methods=['POST'])
def agregar_voz():
    archivo = request.files['archivo']
    if not archivo:
        return "❌ No se subió ningún archivo.", 400

    nombre = archivo.filename
    carpeta = "voces_autorizadas"
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre)
    archivo.save(ruta)

    # Generar huella
    huella = generar_huella(ruta)

    # Guardar huella en archivo
    with open("voces_autorizadas.txt", "a", encoding="utf-8") as f:
        f.write(f"{nombre},{huella}\n")

    return f"✅ Voz '{nombre}' agregada correctamente como voz autorizada."


@app.route('/guardar_voz', methods=['POST'])
def guardar_voz():
    """Guarda la voz base (voz registrada)."""
    archivo = request.files['audio']
    entrada = 'voz_registrada.webm'
    salida = 'voz_registrada.wav'
    archivo.save(entrada)

    # Convertir a WAV (formato estándar)
    os.system(f'ffmpeg -y -i "{entrada}" -ac 1 -ar 44100 "{salida}"')

    # Generar huella
    huella = generar_huella(salida)
    with open('huella_base.txt', 'w') as f:
        f.write(huella)

    return jsonify({"mensaje": "✅ Voz registrada correctamente."})

# === Manejo de contraseña ===
@app.route('/guardar_clave', methods=['POST'])
def guardar_clave():
    clave = request.form.get('clave', '')
    if not clave:
        return "❌ Debes enviar una contraseña.", 400

    # Calcular hash SHA-256 y guardarlo
    hash_clave = hashlib.sha256(clave.encode('utf-8')).hexdigest()
    with open('clave.txt', 'w', encoding='utf-8') as f:
        f.write(hash_clave)

    print("Nueva clave guardada (hash).")
    return redirect(url_for('acceso')) 

@app.route('/verificar_voz', methods=['POST'])
def verificar_voz():
    """Compara una voz nueva con la registrada."""
    if not os.path.exists("huella_base.txt"):
        return jsonify({"mensaje": "❌ No hay voz registrada para comparar."}), 400

    archivo = request.files['audio']
    entrada = 'voz_prueba.webm'
    salida = 'voz_prueba.wav'
    archivo.save(entrada)

    # Convertir a WAV
    os.system(f'ffmpeg -y -i "{entrada}" -ac 1 -ar 44100 "{salida}"')

    # Generar huella de la nueva voz
    huella_nueva = generar_huella(salida)
    huella_guardada = open('huella_base.txt').read().strip()

    # Calcular similitud entre huellas (puedes usar distancia Hamming o correlación)
    similitud = sum(a == b for a, b in zip(huella_guardada, huella_nueva)) / len(huella_guardada)

    print(f"Similitud de voces: {similitud:.4f}")

    if comparar_voces("voz_registrada.wav", "voz_prueba.wav"):
        return jsonify({"mensaje": "✅ Acceso concedido", "acceso": True})
    else:
        return jsonify({"mensaje": "❌ Voz no coincide. Acceso denegado.", "acceso": False})

def comparar_con_autorizadas(archivo_temp):
    huella_temp = generar_huella(archivo_temp)

    if not os.path.exists("voces_autorizadas.txt"):
        return False

    with open("voces_autorizadas.txt", "r", encoding="utf-8") as f:
        for linea in f:
            nombre, huella = linea.strip().split(",")
            if huella == huella_temp:
                print(f"✅ Coincidencia encontrada con {nombre}")
                return True

    print("❌ No coincide con ninguna voz autorizada")
    return False

@app.route('/verificar_clave', methods=['POST'])
def verificar_clave():
    clave_ingresada = request.form.get('clave', '')
    if clave_ingresada == '':
        return render_template("denegado.html")

    if not os.path.exists("clave.txt"):
        return "❌ No hay clave guardada aún.", 400

    with open("clave.txt", "r", encoding='utf-8') as f:
        hash_guardado = f.read().strip()

    hash_ingresada = hashlib.sha256(clave_ingresada.encode('utf-8')).hexdigest()

    # Usar compare_digest para evitar diferencias de tiempo
    if hmac.compare_digest(hash_guardado, hash_ingresada):
        return render_template("acceso.html")
    else:
        return render_template("denegado.html")

def comparar_voces(archivo1, archivo2, tolerancia=0.5):
    # Leer ambos audios
    fs1, data1 = wavfile.read(archivo1)
    fs2, data2 = wavfile.read(archivo2)

    # Asegurar que tengan el mismo tamaño
    min_len = min(len(data1), len(data2))
    data1, data2 = data1[:min_len], data2[:min_len]

    # Convertir a flotante y normalizar
    data1 = data1.astype(float) / np.max(np.abs(data1))
    data2 = data2.astype(float) / np.max(np.abs(data2))

    # Calcular espectros de frecuencia
    fft1 = np.abs(np.fft.rfft(data1))
    fft2 = np.abs(np.fft.rfft(data2))

    # Normalizar espectros
    fft1 /= np.max(fft1)
    fft2 /= np.max(fft2)

    # Calcular similitud por correlación
    similitud = np.corrcoef(fft1, fft2)[0, 1]

    print(f"Similitud de voz: {similitud:.2f}")

    # Evaluar si se acepta según tolerancia
    return similitud > (1 - tolerancia)

# === Ejecución ===
if __name__ == '__main__':
    import webbrowser, threading
    threading.Timer(1.5, lambda: webbrowser.open_new("http://127.0.0.1:5000")).start()
    app.run(debug=True, use_reloader=False)
