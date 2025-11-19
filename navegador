import soundfile as sf
import sounddevice as sd
import os
import platform
import numpy as np


# CONFIG
fs = 44100
CARPETA_AUDIOS = "audios"
if not os.path.exists(CARPETA_AUDIOS):
    os.makedirs(CARPETA_AUDIOS)

VOICE_PRINT_FILE = "huella_voz.npy"

def mejorar_calidad_audio(senal, fs):
    senal = np.asarray(senal, dtype=float).flatten()
    N = len(senal)

    if N == 0:
        return np.zeros(1, dtype='float32')

    espectro = np.fft.rfft(senal)
    freqs = np.fft.rfftfreq(N, d=1/fs)

    banda_voz = (freqs >= 80) & (freqs <= 4000)
    espectro_filtrado = espectro.copy()

    espectro_filtrado[~banda_voz] *= 0.1

    magnitudes = np.abs(espectro_filtrado)
    umbral = 0.02 * magnitudes.max() if magnitudes.size > 0 else 0
    espectro_filtrado[magnitudes < umbral] = 0

    senal_mejorada = np.fft.irfft(espectro_filtrado, n=N)

    max_abs = np.max(np.abs(senal_mejorada)) if senal_mejorada.size > 0 else 0
    if max_abs > 0:
        senal_mejorada = senal_mejorada / max_abs * 0.9

    return senal_mejorada.astype("float32")


def extraer_caracteristicas_voz(senal, fs):
    senal = np.asarray(senal, dtype=float).flatten()

    muestras_1s = int(fs * 1.0)
    if len(senal) > muestras_1s:
        inicio = (len(senal) - muestras_1s) // 2
        senal = senal[inicio:inicio + muestras_1s]

    if len(senal) == 0:
        return np.array([0.0])

    ventana = np.hanning(len(senal))
    senal_win = senal * ventana

    N = len(senal_win)
    espectro = np.fft.rfft(senal_win)
    freqs = np.fft.rfftfreq(N, d=1/fs)

    banda_voz = (freqs >= 80) & (freqs <= 4000)
    caracteristicas = np.abs(espectro[banda_voz])

    if caracteristicas.size == 0:
        return np.array([0.0])

    max_val = caracteristicas.max()
    if max_val > 0:
        caracteristicas = caracteristicas / max_val

    return caracteristicas


def similitud_fft(vec1, vec2):
    n = min(len(vec1), len(vec2))
    if n == 0:
        return 0.0

    v1 = vec1[:n]
    v2 = vec2[:n]

    num = np.dot(v1, v2)
    den = np.linalg.norm(v1) * np.linalg.norm(v2)
    if den == 0:
        return 0.0

    return num / den


def detectar_comando_abrir_google(senal, fs):
    """
    Detecta el comando 'abrir google' usando FFT analizando:
    - Energía en bandas específicas
    - Forma espectral aproximada
    """

    espectro = np.abs(np.fft.rfft(senal))
    freqs = np.fft.rfftfreq(len(senal), 1/fs)

    # Bandas típicas en la frase "abrir google"
    banda1 = (freqs >= 300) & (freqs <= 700)     # "a-bri"
    banda2 = (freqs >= 800) & (freqs <= 1200)    # "ir"
    banda3 = (freqs >= 400) & (freqs <= 900)     # "gú"
    banda4 = (freqs >= 1500) & (freqs <= 2500)   # "gol"

    e1 = espectro[banda1].mean()
    e2 = espectro[banda2].mean()
    e3 = espectro[banda3].mean()
    e4 = espectro[banda4].mean()

    score = e1 + e2 + e3 + e4

    print("Intensidad espectral comando:", score)

    return score > 2.5   # Ajustar según tu voz


def grabar_audio(duracion, archivo):
    print("Grabando audio...")
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    sf.write(archivo, audio, fs)
    print(f"Audio guardado en {archivo}")
    return archivo


def registrar_voz_autorizada():
    print("Diga su frase secreta para registrar su voz...")
    ruta = os.path.join(CARPETA_AUDIOS, "voz_autorizada_fft.wav")
    grabar_audio(3, ruta)

    senal, fs1 = sf.read(ruta)
    if senal.ndim > 1:
        senal = senal[:, 0]

    huella = extraer_caracteristicas_voz(senal, fs1)
    np.save(VOICE_PRINT_FILE, huella)

    print("✔ Voz autorizada registrada correctamente.\n")


def voz_es_autorizada(ruta_audio):
    if not os.path.exists(VOICE_PRINT_FILE):
        print("No hay voz registrada.")
        return False

    huella_reg = np.load(VOICE_PRINT_FILE)

    senal, fs1 = sf.read(ruta_audio)
    if senal.ndim > 1:
        senal = senal[:, 0]

    huella_actual = extraer_caracteristicas_voz(senal, fs1)

    similitud = similitud_fft(huella_reg, huella_actual)
    print("Similitud FFT:", similitud)

    return similitud > 0.75


def abrir_navegador(url):
    sistema = platform.system()

    if sistema == "Windows":
        os.system(f'start "" "{url}"')
    elif sistema == "Darwin":
        os.system(f'open "{url}"')
    else:
        os.system(f'xdg-open "{url}"')


def escuchar_comando():
    print("Hable para verificar su identidad…")

    ruta_temp = os.path.join(CARPETA_AUDIOS, "temp_fft.wav")
    grabar_audio(3, ruta_temp)

    senal, fs1 = sf.read(ruta_temp)
    if senal.ndim > 1:
        senal = senal[:, 0]

    if not voz_es_autorizada(ruta_temp):
        print("❌ Voz NO autorizada.")
        return

    print("✔ Voz autorizada reconocida.")

    # ---------- DETECTAR COMANDO ----------
    if detectar_comando_abrir_google(senal, fs1):
        print("✔ Comando 'abrir google' detectado.")
        abrir_navegador("https://www.google.com")
    else:
        print("❌ No se detectó el comando.")


# ------------------- MENÚ -------------------

while True:
    print("\n===== MENÚ =====")
    print("1. Registrar voz autorizada")
    print("2. Escuchar comando")
    print("3. Salir")
    op = input("Seleccione opción: ")

    if op == "1":
        registrar_voz_autorizada()
    elif op == "2":
        escuchar_comando()
    elif op == "3":
        break
    else:
        print("Opción no válida.")
