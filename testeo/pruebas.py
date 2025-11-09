"""
analisis_fft_voz_.py
---------------------------------
Versión adaptada para entornos sin GUI (como Codespaces):
1. Guarda audios en /audios_pruebas/
2. Guarda las gráficas generadas en /graficos_pruebas/
3. No abre ventanas (plt.show), guarda las imágenes como archivos PNG

En Codespaces no se pueden guardar audios debes descargar el codigo y ahi si se puede.
si se prueba el codigo deben guardar los audios manualmente en la carpeta AUDIOS_PRUEBAS
para que se pueda probar dentro del Codespace y se guarden las graficas de pruebas.

Requiere:
    pip install soundfile sounddevice numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import sounddevice as sd
import os

# === CONFIGURACIÓN ===
CARPETA_AUDIOS = "audios_pruebas"
CARPETA_GRAFICOS = "graficos_pruebas"
os.makedirs(CARPETA_AUDIOS, exist_ok=True)
os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
FS = 16000  # Frecuencia de muestreo


# === FUNCIONES ===

def grabar_audio(nombre_archivo, duracion=3, fs=FS):
    """Graba audio desde el micrófono y lo guarda en /audios/."""
    print(f"\n🎙️ Grabando durante {duracion} segundos...")
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    ruta = os.path.join(CARPETA_AUDIOS, f"{nombre_archivo}.wav")
    sf.write(ruta, audio, fs)
    print(f"✅ Audio guardado correctamente en: {ruta}")
    return ruta


def cargar_audio(ruta):
    """Carga un archivo de audio y devuelve la señal y frecuencia."""
    x, fs = sf.read(ruta)
    if x.ndim > 1:
        x = x.mean(axis=1)  # pasa a mono si es estéreo
    return x, fs


def simular_audio(fs=FS):
    """Genera una señal senoidal simulada tipo voz."""
    print("⚠️ No se encontró un audio. Se generará una señal simulada.")
    dur = 1.0
    t = np.linspace(0, dur, int(fs * dur), endpoint=False)
    f0 = 250  # frecuencia fundamental (Hz)
    senal = np.sin(2 * np.pi * f0 * t)
    return senal, fs


def graficar_onda_y_fft(senal, fs, titulo="Audio"):
    """Genera la forma de onda y su espectro FFT y guarda la gráfica como PNG."""
    duracion = len(senal) / fs
    t = np.linspace(0, duracion, len(senal))

    plt.figure(figsize=(10, 6))

    # === Forma de onda ===
    plt.subplot(2, 1, 1)
    plt.plot(t, senal)
    plt.title(f"Forma de onda ({titulo})")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Amplitud")

    # === FFT ===
    N = len(senal)
    frecuencias = np.fft.rfftfreq(N, 1/fs)
    magnitudes = np.abs(np.fft.rfft(senal))

    plt.subplot(2, 1, 2)
    plt.plot(frecuencias, magnitudes, color='orange')
    plt.title("Espectro de frecuencias (FFT)")
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("Magnitud")
    plt.xlim(0, 1000)
    plt.tight_layout()

    # === Guardar en carpeta graficos ===
    nombre_sin_ext = titulo.replace(".wav", "").strip()
    ruta_grafico = os.path.join(CARPETA_GRAFICOS, f"grafico_{nombre_sin_ext}.png")
    plt.savefig(ruta_grafico)
    plt.close()

    print(f"📈 Gráfico guardado en: {ruta_grafico}")


# === MENÚ INTERACTIVO ===

def menu():
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Grabar un nuevo audio")
        print("2. Analizar un audio existente")
        print("3. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            nombre = input("Nombre para el archivo de audio: ").strip()
            duracion = float(input("Duración en segundos (ej: 3): "))
            grabar_audio(nombre, duracion)
            print("🎧 Grabación finalizada. Puedes analizarlo desde el menú principal.")

        elif opcion == "2":
            audios = [f for f in os.listdir(CARPETA_AUDIOS) if f.endswith(".wav")]
            if not audios:
                print("No hay audios guardados. Se usará una señal simulada.")
                senal, fs = simular_audio()
                graficar_onda_y_fft(senal, fs, titulo="Simulada")
            else:
                print("\n=== Audios disponibles ===")
                for i, a in enumerate(audios, 1):
                    print(f"{i}. {a}")
                idx = int(input("Selecciona el número del audio: ")) - 1
                archivo = audios[idx]
                ruta = os.path.join(CARPETA_AUDIOS, archivo)
                senal, fs = cargar_audio(ruta)
                graficar_onda_y_fft(senal, fs, titulo=archivo)

        elif opcion == "3":
            print("👋 Saliendo del programa...")
            break

        else:
            print("❌ Opción inválida. Intenta nuevamente.")


# === EJECUCIÓN ===
if __name__ == "__main__":
    menu()
