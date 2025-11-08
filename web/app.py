from flask import Flask, render_template, request, jsonify
import numpy as np
import librosa
import soundfile as sf
import hashlib
import io, base64, os
import matplotlib.pyplot as plt

app = Flask(__name__)

def generar_huella(audio_path):
    y, sr = librosa.load(audio_path)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return hashlib.sha256(mfcc.mean(axis=1).tobytes()).hexdigest()

def generar_grafica(audio_path):
    y, sr = librosa.load(audio_path)
    Y = np.abs(np.fft.fft(y))
    freqs = np.fft.fftfreq(len(Y), 1/sr)

    plt.figure(figsize=(6,3))
    plt.plot(freqs[:len(freqs)//2], Y[:len(Y)//2])
    plt.title("Espectro de Frecuencias (Transformada de Fourier)")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Amplitud")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar')
def analizar():
    return render_template('analisis.html')

@app.route('/registrar')
def registrar():
    return render_template('registrar.html')

@app.route('/subir_audio', methods=['POST'])
def subir_audio():
    archivo = request.files['audio']
    ruta = 'voz_temp.wav'
    archivo.save(ruta)

    grafica = generar_grafica(ruta)
    return jsonify({"grafica": grafica})

@app.route('/guardar_voz', methods=['POST'])
def guardar_voz():
    archivo = request.files['audio']
    archivo.save('voz_registrada.wav')
    huella = generar_huella('voz_registrada.wav')

    with open('huella_base.txt', 'w') as f:
        f.write(huella)

    return jsonify({"mensaje": "✅ Voz registrada correctamente."})

if __name__ == '__main__':
    import webbrowser, threading
    threading.Timer(1.5, lambda: webbrowser.open_new("http://127.0.0.1:5000")).start()
    app.run(debug=True)
