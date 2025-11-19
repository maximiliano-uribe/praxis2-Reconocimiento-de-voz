import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import numpy as np   # <-- IMPORTANTE para FFT
import configuracion as cfg

from audio_grabar import grabar_audio, VOICES_DIR
from audio_reconocer import recognize_flow
from procesar_audio import plot_waveform, analyze_voice

from auth_system import (
    register_user, list_registered_users, login_by_voice,
    read_user_notes, append_user_note, open_user_notes_in_editor, user_notes_path
)

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

AUDIO_FILE = "nueva_grabacion.wav"
os.makedirs(VOICES_DIR, exist_ok=True)


def start_gui():
    root = tk.Tk()
    root.title("Sistema de Voz")
    root.geometry("480x630")
    root.resizable(False, False)

    # Ocultar ventana principal hasta después del login
    root.withdraw()

    current_user = {"name": None}

    title_lbl = tk.Label(root, text="Sistema de Autenticación por Voz", font=("Arial", 16, "bold"))
    title_lbl.pack(pady=12)

    status_var = tk.StringVar(value="No autenticado")
    status_lbl = tk.Label(root, textvariable=status_var, font=("Arial", 10, "italic"))
    status_lbl.pack(pady=(0, 8))

    # ==========================================================
    #   LOGIN / REGISTER DIALOG
    # ==========================================================
    def show_login_dialog():
        dlg = tk.Toplevel(root)
        dlg.title("Inicio / Registro")
        dlg.geometry("380x260")
        dlg.grab_set()  # modal
        tk.Label(dlg, text="Bienvenido — Elige una opción", font=("Arial", 12, "bold")).pack(pady=8)

        def do_register():
            name = simpledialog.askstring("Registro", "Introduce tu nombre (ej. Juan):", parent=dlg)
            if not name:
                return

            dur = simpledialog.askinteger("Duración", "Duración de grabación (segundos):",
                                          parent=dlg, minvalue=2, maxvalue=10, initialvalue=3)
            if dur is None:
                dur = 3

            ok = register_user(name, duration=dur)
            if ok:
                messagebox.showinfo("Registro", f"Usuario '{name}' registrado correctamente.", parent=dlg)
            else:
                messagebox.showerror("Registro", "No se pudo registrar el usuario.", parent=dlg)

        def do_login():
            messagebox.showinfo("Login", "Se grabarán 3 segundos para identificar la voz.", parent=dlg)
            user = login_by_voice(duration=3)

            if user:
                current_user["name"] = user
                status_var.set(f"Autenticado: {user}")
                messagebox.showinfo("Login", f"Bienvenido {user}.", parent=dlg)
                dlg.destroy()
                root.deiconify()   # <-- Mostrar ventana principal
                enable_main_menu()
            else:
                messagebox.showwarning("Login", "Voz no reconocida.", parent=dlg)

        def show_users():
            users = list_registered_users()
            if not users:
                messagebox.showinfo("Usuarios", "No hay usuarios registrados.", parent=dlg)
                return
            messagebox.showinfo("Usuarios registrados", "\n".join(users), parent=dlg)

        tk.Button(dlg, text="Registrar nuevo usuario", width=28, command=do_register).pack(pady=8)
        tk.Button(dlg, text="Iniciar sesión por voz", width=28, command=do_login).pack(pady=8)
        tk.Button(dlg, text="Ver usuarios registrados", width=28, command=show_users).pack(pady=6)

    show_login_dialog()

    # ==========================================================
    #   BOTONERA PRINCIPAL
    # ==========================================================
    btn_frame = tk.Frame(root)
    btn_frame.pack(expand=True)

    def disabled_command():
        messagebox.showwarning("No autenticado", "Inicia sesión primero.")

    # botones
    btn_grabar = tk.Button(btn_frame, text="🎙️ Grabar voz", width=28, command=disabled_command)
    btn_reconocer = tk.Button(btn_frame, text="🔍 Reconocer voz", width=28, command=disabled_command)
    btn_graficar = tk.Button(btn_frame, text="📈 Mostrar gráfica de mi voz", width=28, command=disabled_command)
    btn_info_voice = tk.Button(btn_frame, text="🔎 Información avanzada de mi voz", width=28, command=disabled_command)
    btn_create_note = tk.Button(btn_frame, text="📝 Crear nota privada", width=28, command=disabled_command)
    btn_view_notes = tk.Button(btn_frame, text="📂 Ver mis notas", width=28, command=disabled_command)
    btn_open_notes_editor = tk.Button(btn_frame, text="📄 Abrir bloc de notas privado", width=28, command=disabled_command)
    btn_logout = tk.Button(btn_frame, text="🔒 Cerrar sesión", width=28, command=disabled_command)

    btn_grabar.pack(pady=6)
    btn_reconocer.pack(pady=6)
    btn_graficar.pack(pady=6)
    btn_info_voice.pack(pady=6)
    btn_create_note.pack(pady=6)
    btn_view_notes.pack(pady=6)
    btn_open_notes_editor.pack(pady=6)
    btn_logout.pack(pady=6)

    # ==========================================================
    #   HABILITAR BOTONES DESPUÉS DEL LOGIN
    # ==========================================================
    def enable_main_menu():

        # -----------------------------
        #  Información avanza + GRÁFICAS
        # -----------------------------
        def do_info_voice():
            user = current_user["name"]
            if not user:
                messagebox.showerror("Error", "No has iniciado sesión.")
                return

            voice_file = os.path.join(VOICES_DIR, f"{user}.wav")

            if not os.path.exists(voice_file):
                messagebox.showwarning("Info", "No se encontró la voz registrada.")
                return

            info = analyze_voice(voice_file)

            win = tk.Toplevel(root)
            win.title("Información avanzada de la voz")
            win.geometry("850x500")

            # Texto a la derecha
            txt_info = (
                f"Frecuencia de muestreo: {info['samplerate']} Hz\n"
                f"Duración: {info['duration']:.3f} s\n"
                f"RMS (energía): {info['rms']:.6f}\n"
                f"Amplitud Máxima: {info['max_amplitud']:.6f}\n"
                f"Zero Crossing Rate: {info['zero_cross_rate']:.2f} cruces/s\n"
                f"Frecuencia dominante: {info['dom_freq']:.2f} Hz\n\n"
                "Picos principales:\n" +
                "\n".join([f"{p[0]:.1f} Hz — {p[1]:.2f}" for p in info["top_peaks"]])
            )

            right = tk.Frame(win, width=300)
            right.pack(side="right", fill="y")

            txt = tk.Text(right, wrap="word")
            txt.pack(fill="both", expand=True)
            txt.insert("1.0", txt_info)
            txt.config(state="disabled")

            # Gráficas a la izquierda
            left = tk.Frame(win)
            left.pack(side="left", fill="both", expand=True)

            fig = Figure(figsize=(7, 4), dpi=100)
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)

            # Cargar audio
            samplerate = info['samplerate']
            data = info['raw_data']

            # Forma de onda
            t = np.linspace(0, len(data) / samplerate, num=len(data))
            ax1.plot(t, data)
            ax1.set_title("Forma de onda")

            # FFT
            freqs = np.fft.rfftfreq(len(data), d=1/samplerate)
            mags = np.abs(np.fft.rfft(data))
            ax2.plot(freqs, mags)
            ax2.set_title("FFT")
            ax2.set_xlim(0, samplerate/2)

            canvas = FigureCanvasTkAgg(fig, master=left)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        # -----------------------------
        #  Funciones ya existentes
        # -----------------------------
        def do_grabar():
            dur = simpledialog.askinteger("Duración", "Duración de grabación:", parent=root,
                                          minvalue=1, maxvalue=20, initialvalue=3)
            if dur:
                grabar_audio(AUDIO_FILE, duracion=dur)
                messagebox.showinfo("Grabación", "Grabación guardada localmente.")

        def do_reconocer():
            messagebox.showinfo("Reconocer", "Se grabarán 3 segundos.", parent=root)
            match = recognize_flow(duration=3)
            if match:
                messagebox.showinfo("Resultado", f"Voz reconocida: {match}", parent=root)
            else:
                messagebox.showwarning("Resultado", "Voz no reconocida.", parent=root)

        def do_graficar():
            user = current_user["name"]
            voice_file = os.path.join(VOICES_DIR, f"{user}.wav")
            if not os.path.exists(voice_file):
                messagebox.showwarning("Gráfico", "No se encontró la voz registrada.")
                return
            plot_waveform(voice_file)

        def do_create_note():
            user = current_user["name"]
            txt = simpledialog.askstring("Nueva nota", "Escribe la nota:", parent=root)
            if txt:
                append_user_note(user, txt)
                messagebox.showinfo("Nota", "Nota guardada correctamente.")

        def do_view_notes():
            user = current_user["name"]
            content = read_user_notes(user) or "(no hay notas)"
            win = tk.Toplevel(root)
            win.title(f"Notas de {user}")
            win.geometry("600x400")
            txtw = tk.Text(win, wrap="word")
            txtw.pack(expand=True, fill="both")
            txtw.insert("1.0", content)
            txtw.config(state="disabled")

        def do_open_notes_editor():
            user = current_user["name"]
            if not open_user_notes_in_editor(user):
                messagebox.showerror("Error", "No se pudo abrir.")

        def do_logout():
            current_user["name"] = None
            status_var.set("No autenticado")
            root.withdraw()
            show_login_dialog()

        # asignación
        btn_grabar.config(command=do_grabar)
        btn_reconocer.config(command=do_reconocer)
        btn_graficar.config(command=do_graficar)
        btn_info_voice.config(command=do_info_voice)
        btn_create_note.config(command=do_create_note)
        btn_view_notes.config(command=do_view_notes)
        btn_open_notes_editor.config(command=do_open_notes_editor)
        btn_logout.config(command=do_logout)

        status_var.set(f"Autenticado: {current_user['name']}")

    # ==========================================================
    #   DESHABILITAR BOTONES
    # ==========================================================
    def disable_main_menu():
        btn_grabar.config(command=disabled_command)
        btn_reconocer.config(command=disabled_command)
        btn_graficar.config(command=disabled_command)
        btn_info_voice.config(command=disabled_command)
        btn_create_note.config(command=disabled_command)
        btn_view_notes.config(command=disabled_command)
        btn_open_notes_editor.config(command=disabled_command)
        btn_logout.config(command=disabled_command)

    disable_main_menu()

    root.mainloop()
