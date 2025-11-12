"""
analisis_fft_voz_mejorado.py
---------------------------------
Versión adaptada para entornos sin GUI (como Codespaces):
1. Guarda audios en /audios_pruebas/
2. Guarda las gráficas generadas en /graficos_pruebas/
3. No abre ventanas (plt.show), guarda las imágenes como archivos PNG

NOVEDADES:
- Al grabar, se guarda también una versión de audio "mejorada" usando FFT + filtro
  en frecuencia y reconstrucción con la transformada inversa de Fourier (IFFT).
- Opción para comparar / autenticar si dos audios parecen de la misma voz,
  usando características espectrales (FFT) y un índice de similitud.
- Se generan gráficas comparativas de espectros para ver cómo cambia la señal.

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


# === FUNCIONES DE PROCESAMIENTO ===

def mejorar_calidad_audio(senal, fs):
    """
    Mejora simple de calidad de audio:
    - FFT
    - Filtro pasa-banda 80–4000 Hz (banda típica de voz)
    - Eliminación de componentes muy débiles (ruido)
    - Reconstrucción con IFFT (irfft)
    """
    # Asegurarse de que sea vector 1D tipo float64
    senal = np.asarray(senal, dtype=float).flatten()
    N = len(senal)

    # Transformada de Fourier (sólo parte real-positiva)
    espectro = np.fft.rfft(senal)
    freqs = np.fft.rfftfreq(N, d=1/fs)

    # Filtro pasa-banda para voz
    banda_voz = (freqs >= 80) & (freqs <= 4000)
    espectro_filtrado = espectro.copy()

    # Atenuar fuera de la banda de voz
    espectro_filtrado[~banda_voz] *= 0.1

    # Umbral de ruido dentro de la banda
    magnitudes = np.abs(espectro_filtrado)
    umbral = 0.02 * magnitudes.max() if magnitudes.size > 0 else 0.0
    espectro_filtrado[magnitudes < umbral] = 0

    # Reconstruir con IFFT
    senal_mejorada = np.fft.irfft(espectro_filtrado, n=N)

    # Normalizar amplitud para evitar saturación
    max_abs = np.max(np.abs(senal_mejorada)) if senal_mejorada.size > 0 else 0
    if max_abs > 0:
        senal_mejorada = senal_mejorada / max_abs * 0.9

    return senal_mejorada.astype('float32')


def reesample_signal(senal, fs_origen, fs_destino):
    """Re–muestrea la señal si las frecuencias de muestreo son distintas."""
    if fs_origen == fs_destino:
        return senal
    senal = np.asarray(senal, dtype=float).flatten()
    dur = len(senal) / fs_origen
    t_orig = np.linspace(0, dur, len(senal), endpoint=False)
    t_new = np.linspace(0, dur, int(dur * fs_destino), endpoint=False)
    return np.interp(t_new, t_orig, senal)


def extraer_caracteristicas_voz(senal, fs):
    """
    Extrae características espectrales simples para comparación de voz:
    - Toma ~1 s (o todo si es más corto)
    - Ventana de Hann
    - FFT
    - Magnitud en banda 80–4000 Hz
    - Normalización [0,1]
    """
    senal = np.asarray(senal, dtype=float).flatten()

    # Usar 1 segundo central si es posible
    muestras_1s = int(fs * 1.0)
    if len(senal) > muestras_1s:
        inicio = (len(senal) - muestras_1s) // 2
        senal = senal[inicio:inicio + muestras_1s]

    if len(senal) == 0:
        return np.array([0.0])

    # Ventana para suavizar
    ventana = np.hanning(len(senal))
    senal_win = senal * ventana

    # FFT
    N = len(senal_win)
    espectro = np.fft.rfft(senal_win)
    freqs = np.fft.rfftfreq(N, d=1/fs)

    # Banda de voz
    banda_voz = (freqs >= 80) & (freqs <= 4000)
    caracteristicas = np.abs(espectro[banda_voz])

    if caracteristicas.size == 0:
        return np.array([0.0])

    # Normalizar
    max_val = caracteristicas.max()
    if max_val > 0:
        caracteristicas = caracteristicas / max_val

    return caracteristicas


def comparar_voces(senal1, fs1, senal2, fs2):
    """
    Compara dos señales de voz con un índice de similitud (coseno).
    Devuelve un valor entre 0 y 1 (más alto = más parecido).
    """
    # Re–muestrear la segunda al fs de la primera si hace falta
    senal2_res = reesample_signal(senal2, fs2, fs1)

    # Extraer características
    feat1 = extraer_caracteristicas_voz(senal1, fs1)
    feat2 = extraer_caracteristicas_voz(senal2_res, fs1)

    # Ajustar longitud
    n = min(len(feat1), len(feat2))
    if n == 0:
        return 0.0
    feat1 = feat1[:n]
    feat2 = feat2[:n]

    # Similitud coseno
    num = np.dot(feat1, feat2)
    den = np.linalg.norm(feat1) * np.linalg.norm(feat2)
    if den == 0:
        return 0.0
    similitud = num / den
    # Asegurar rango [0,1]
    similitud = float(max(0.0, min(1.0, similitud)))
    return similitud


# === FUNCIONES DE AUDIO BÁSICO ===

def grabar_audio(nombre_archivo, duracion=3, fs=FS):
    """
    Graba audio desde el micrófono y lo guarda en /audios_pruebas/.
    - Guarda el audio original.
    - Genera y guarda una versión mejorada usando FFT + IFFT.
    """
    print(f"\n🎙️ Grabando durante {duracion} segundos...")
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()

    # Audio original
    ruta_original = os.path.join(CARPETA_AUDIOS, f"{nombre_archivo}.wav")
    sf.write(ruta_original, audio, fs)

    # Audio mejorado (procesado en frecuencia)
    senal_mejorada = mejorar_calidad_audio(audio[:, 0], fs)
    ruta_mejorado = os.path.join(CARPETA_AUDIOS, f"{nombre_archivo}_mejorado.wav")
    sf.write(ruta_mejorado, senal_mejorada, fs)

    print(f"✅ Audio original guardado en: {ruta_original}")
    print(f"✅ Audio MEJORADO guardado en: {ruta_mejorado}")

    return ruta_original, ruta_mejorado


def cargar_audio(ruta):
    """Carga un archivo de audio y devuelve la señal (mono) y frecuencia."""
    x, fs = sf.read(ruta)
    if x.ndim > 1:
        x = x.mean(axis=1)  # pasa a mono si es estéreo
    return x.astype('float32'), fs


def simular_audio(fs=FS):
    """Genera una señal senoidal simulada tipo voz."""
    print("⚠️ No se encontró un audio. Se generará una señal simulada.")
    dur = 1.0
    t = np.linspace(0, dur, int(fs * dur), endpoint=False)
    f0 = 250  # frecuencia fundamental (Hz)
    senal = np.sin(2 * np.pi * f0 * t)
    return senal.astype('float32'), fs


# === GRAFICACIÓN ===

def graficar_onda_y_fft(senal, fs, titulo="Audio"):
    """Genera la forma de onda y su espectro FFT y guarda la gráfica como PNG."""
    duracion = len(senal) / fs if fs > 0 else 0
    t = np.linspace(0, duracion, len(senal)) if len(senal) > 0 else np.array([0])

    plt.figure(figsize=(10, 6))

    # === Forma de onda ===
    plt.subplot(2, 1, 1)
    plt.plot(t, senal)
    plt.title(f"Forma de onda ({titulo})")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Amplitud")

    # === FFT ===
    N = len(senal)
    if N > 0:
        frecuencias = np.fft.rfftfreq(N, 1/fs)
        magnitudes = np.abs(np.fft.rfft(senal))
    else:
        frecuencias = np.array([0])
        magnitudes = np.array([0])

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


def graficar_comparacion_fft(senal1, fs1, senal2, fs2, nombre1="audio1", nombre2="audio2"):
    """
    Grafica y guarda en un mismo gráfico las FFT de dos señales para compararlas.
    """
    # Re–muestrear si es necesario
    senal2_res = reesample_signal(senal2, fs2, fs1)

    # Igualar longitud
    N = min(len(senal1), len(senal2_res))
    if N == 0:
        print("No se pudo graficar comparación: alguna de las señales está vacía.")
        return

    s1 = senal1[:N]
    s2 = senal2_res[:N]

    # FFT
    freqs = np.fft.rfftfreq(N, d=1/fs1)
    mag1 = np.abs(np.fft.rfft(s1))
    mag2 = np.abs(np.fft.rfft(s2))

    plt.figure(figsize=(10, 5))
    plt.plot(freqs, mag1, label=nombre1)
    plt.plot(freqs, mag2, label=nombre2, linestyle="--")
    plt.title("Comparación de espectros de voz (FFT)")
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("Magnitud")
    plt.xlim(0, 4000)
    plt.legend()
    plt.tight_layout()

    nombre_sin_ext_1 = nombre1.replace(".wav", "").strip()
    nombre_sin_ext_2 = nombre2.replace(".wav", "").strip()
    nombre_fig = f"comparacion_fft_{nombre_sin_ext_1}_vs_{nombre_sin_ext_2}.png"
    ruta_grafico = os.path.join(CARPETA_GRAFICOS, nombre_fig)
    plt.savefig(ruta_grafico)
    plt.close()

    print(f"📊 Gráfico de comparación de FFT guardado en: {ruta_grafico}")


# === MENÚ INTERACTIVO ===

def menu():
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Grabar un nuevo audio (original + mejorado)")
        print("2. Analizar un audio existente (onda + FFT)")
        print("3. Autenticar / comparar si dos audios son de la misma voz")
        print("4. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            nombre = input("Nombre para el archivo de audio (sin extensión): ").strip()
            try:
                duracion = float(input("Duración en segundos (ej: 3): "))
            except ValueError:
                print("Duración no válida, se usará 3 segundos.")
                duracion = 3.0
            grabar_audio(nombre, duracion)
            print("🎧 Grabación finalizada. Puedes analizar los audios desde el menú.")

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
                try:
                    idx = int(input("Selecciona el número del audio: ")) - 1
                    archivo = audios[idx]
                except (ValueError, IndexError):
                    print("Selección inválida.")
                    continue

                ruta = os.path.join(CARPETA_AUDIOS, archivo)
                senal, fs = cargar_audio(ruta)
                graficar_onda_y_fft(senal, fs, titulo=archivo)

        elif opcion == "3":
            # Autenticación / comparación de voz
            audios = [f for f in os.listdir(CARPETA_AUDIOS) if f.endswith(".wav")]
            if len(audios) < 2:
                print("Se necesitan al menos 2 audios en la carpeta para comparar voces.")
                continue

            print("\n=== Audios disponibles ===")
            for i, a in enumerate(audios, 1):
                print(f"{i}. {a}")

            try:
                idx_ref = int(input("Selecciona el número del AUDIO DE REFERENCIA: ")) - 1
                idx_pru = int(input("Selecciona el número del AUDIO A COMPARAR: ")) - 1
                archivo_ref = audios[idx_ref]
                archivo_pru = audios[idx_pru]
            except (ValueError, IndexError):
                print("Selección inválida.")
                continue

            ruta_ref = os.path.join(CARPETA_AUDIOS, archivo_ref)
            ruta_pru = os.path.join(CARPETA_AUDIOS, archivo_pru)

            senal_ref, fs_ref = cargar_audio(ruta_ref)
            senal_pru, fs_pru = cargar_audio(ruta_pru)

            similitud = comparar_voces(senal_ref, fs_ref, senal_pru, fs_pru)
            print(f"\n🔎 Índice de similitud entre voces: {similitud:.3f} (0 = diferente, 1 = idéntica)")

            if similitud > 0.85:
                print("➡️ Probablemente es la MISMA voz (muy similar).")
            elif similitud > 0.65:
                print("➡️ Voces PARECIDAS, podría ser la misma persona con condiciones diferentes.")
            else:
                print("➡️ Voces bastantes DIFERENTES, probablemente no es la misma persona.")

            # Generar gráfico comparativo de espectros
            graficar_comparacion_fft(
                senal_ref, fs_ref,
                senal_pru, fs_pru,
                nombre1=archivo_ref,
                nombre2=archivo_pru
            )

        elif opcion == "4":
            print("👋 Saliendo del programa...")
            break

        else:
            print("❌ Opción inválida. Intenta nuevamente.")


# === EJECUCIÓN ===
if __name__ == "__main__":
    menu()

