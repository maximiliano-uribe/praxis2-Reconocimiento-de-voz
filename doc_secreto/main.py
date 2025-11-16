import os
from audio_grabar import record_and_save_flow, grabar_audio, VOICES_DIR
from audio_reconocer import recognize_flow
from procesar_audio import plot_waveform, analyze_voice
from auth_system import (
    register_user,
    login_by_voice,
    append_user_note,
    read_user_notes,
    list_registered_users,
    user_notes_path
)

os.makedirs("usuarios", exist_ok=True)
os.makedirs("notas_privadas", exist_ok=True)


# ===========================
#   MENÚ INICIAL
# ===========================
def menu_inicio():
    duracion_grab = 3  # misma duración para registro y login

    while True:
        print("\n===== SISTEMA DE NOTAS POR VOZ =====")
        print("1. Registrar usuario")
        print("2. Iniciar sesión por voz")
        print("0. Salir")
        op = input("Elige una opción: ").strip()

        if op == "1":
            name = input("Nombre de usuario: ").strip()
            if register_user(name, duration=duracion_grab):
                print(f"✔ Usuario {name} registrado correctamente.")
            else:
                print("❌ Error al registrar usuario.")

        elif op == "2":
            print("Hable para iniciar sesión...")
            usuario = login_by_voice(duration=duracion_grab)
            if usuario:
                print(f"✔ Bienvenido {usuario}")
                menu_usuario(usuario)  # despliega el menú completo de usuario
            else:
                print("❌ Voz no reconocida.")

        elif op == "0":
            break

        else:
            print("Opción inválida.")


# ===========================
#   MENÚ DE USUARIO
# ===========================
def menu_usuario(user):
    while True:
        print(f"\n===== MENÚ DE {user} =====")
        print("1. Agregar nota privada")
        print("2. Leer notas privadas")
        print("3. Graficar voz")
        print("4. Analizar voz")
        print("0. Cerrar sesión")

        op = input("Elige una opción: ").strip()

        if op == "1":
            nota = input("Escribe tu nota: ").strip()
            if append_user_note(user, nota):
                print("✔ Nota agregada correctamente.")
            else:
                print("❌ Error al guardar la nota.")

        elif op == "2":
            contenido = read_user_notes(user)
            print("\n--- Tus notas ---")
            print(contenido or "(no hay notas)")
            print("-----------------")

        elif op == "3":
            path = os.path.join(VOICES_DIR, f"{user}.wav")
            if os.path.exists(path):
                plot_waveform(path)
            else:
                print("❌ No se encontró tu grabación.")

        elif op == "4":
            path = os.path.join(VOICES_DIR, f"{user}.wav")
            if os.path.exists(path):
                info = analyze_voice(path)
                print(f"\n--- Información avanzada de {user} ---")
                print(f"Duración: {info['duration']:.2f} s")
                print(f"RMS: {info['rms']:.4f}")
                print(f"Amplitud máxima: {info['max_amplitud']:.4f}")
                print(f"Zero Crossing Rate: {info['zero_cross_rate']:.2f}")
                print(f"Frecuencia dominante: {info['dom_freq']:.2f} Hz")
                print("Principales picos FFT:")
                for f, m in info['top_peaks']:
                    print(f"  {f:.1f} Hz — {m:.2f}")
                print("------------------------------------")
            else:
                print("❌ No se encontró tu grabación.")

        elif op == "0":
            print(f"⚡ Cerrando sesión de {user}...")
            break

        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu_inicio()
