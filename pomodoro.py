import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import json
from datetime import datetime
from PIL import Image, ImageTk
import os
import winsound
import threading
import tkinter.font as tkFont

class PomodoroApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Pomodoro App")
        self.root.geometry("800x600")
        
        # Configuración visual
        self.settings = {
            "theme": "dark",
            "color_theme": "blue",
            "font_family": "Helvetica",
            "font_size": 24,
            "custom_colors": {
                "primary": "#1A1B26",        # Fondo principal (azul oscuro)
                "secondary": "#24283B",      # Fondo secundario (azul medio)
                "accent": "#7AA2F7",         # Acento (azul brillante)
                "text": "#A9B1D6",          # Texto principal (gris claro)
                "warning": "#F7768E"         # Alertas (rosa)
            },
            "transparency": 0.97,            # Transparencia de los widgets
            "alert_sound": True              # Sonido de alerta activado/desactivado
        }
        
        # Obtener todas las fuentes disponibles en el sistema
        self.available_fonts = list(set(tkFont.families()))
        self.available_fonts.sort()
        
        # Cargar configuración
        self.load_visual_settings()
        ctk.set_appearance_mode(self.settings["theme"])
        ctk.set_default_color_theme(self.settings["color_theme"])
        
        # Variables de tiempo
        self.work_time = 25
        self.break_time = 5
        self.time_left = self.work_time * 60
        self.is_running = False
        self.is_break = False
        self.timer_id = None
        self.sessions_completed = 0
        
        # Crear interfaz
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        # Frame principal con padding y esquinas redondeadas
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Título y materia en un frame elegante
        self.title_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.title_frame.pack(pady=10, padx=15, fill="x")

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="✨ Enfócate en lo importante",
            font=(self.settings["font_family"], 28, "bold")
        )
        self.title_label.pack(pady=10)

        self.subtitle_label = ctk.CTkLabel(
            self.title_frame,
            text="Minimiza las distracciones y maximiza tu productividad",
            font=(self.settings["font_family"], 14),
            text_color=self.settings["custom_colors"]["text"]
        )
        self.subtitle_label.pack(pady=(0, 10))

        self.subject_entry = ctk.CTkEntry(
            self.title_frame,
            placeholder_text="¿Qué estás estudiando hoy?",
            width=400,
            height=35,
            font=(self.settings["font_family"], 14),
            corner_radius=8
        )
        self.subject_entry.pack(pady=10)

        # Timer Frame con diseño moderno
        self.timer_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.timer_frame.pack(pady=20, padx=15, fill="x")

        # Marco para el temporizador con efecto de profundidad
        timer_display = ctk.CTkFrame(self.timer_frame, corner_radius=15)
        timer_display.pack(pady=15, padx=20, fill="x")

        self.timer_label = ctk.CTkLabel(
            timer_display,
            text=self.format_time(self.time_left),
            font=(self.settings["font_family"], 72, "bold")
        )
        self.timer_label.pack(pady=20)

        # Configuración de tiempo con diseño mejorado
        self.time_config_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.time_config_frame.pack(pady=10, padx=15, fill="x")

        # Contenedor para los controles de tiempo
        time_controls = ctk.CTkFrame(self.time_config_frame, fg_color="transparent")
        time_controls.pack(pady=10, padx=20)

        # Frame para tiempo de trabajo
        work_frame = ctk.CTkFrame(time_controls, fg_color="transparent")
        work_frame.pack(side="left", padx=20)
        
        self.work_time_label = ctk.CTkLabel(
            work_frame,
            text="⏱️ Tiempo de trabajo",
            font=(self.settings["font_family"], 14)
        )
        self.work_time_label.pack()

        self.work_time_entry = ctk.CTkEntry(
            work_frame,
            width=70,
            height=32,
            font=(self.settings["font_family"], 14),
            corner_radius=8,
            justify="center"
        )
        self.work_time_entry.insert(0, str(self.work_time))
        self.work_time_entry.pack(pady=5)

        # Frame para tiempo de descanso
        break_frame = ctk.CTkFrame(time_controls, fg_color="transparent")
        break_frame.pack(side="left", padx=20)

        self.break_time_label = ctk.CTkLabel(
            break_frame,
            text="☕ Tiempo de descanso",
            font=(self.settings["font_family"], 14)
        )
        self.break_time_label.pack()

        self.break_time_entry = ctk.CTkEntry(
            break_frame,
            width=70,
            height=32,
            font=(self.settings["font_family"], 14),
            corner_radius=8,
            justify="center"
        )
        self.break_time_entry.insert(0, str(self.break_time))
        self.break_time_entry.pack(pady=5)

        # Botones de control
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20, fill="x")

        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Iniciar",
            command=self.start_timer,
            width=120
        )
        self.start_button.pack(side="left", padx=10, expand=True)

        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text="Pausar",
            command=self.pause_timer,
            width=120
        )
        self.pause_button.pack(side="left", padx=10, expand=True)

        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Reiniciar",
            command=self.reset_timer,
            width=120
        )
        self.reset_button.pack(side="left", padx=10, expand=True)

        # Botón de ajustes
        self.settings_button = ctk.CTkButton(
            self.button_frame,
            text="⚙️ Ajustes",
            command=self.open_settings_window,
            width=120
        )
        self.settings_button.pack(side="left", padx=10, expand=True)

        # Botón para mostrar/ocultar ventana flotante
        self.float_button = ctk.CTkButton(
            self.button_frame,
            text="🔲 Ventana flotante",
            command=self.toggle_float_window,
            width=120
        )
        self.float_button.pack(side="left", padx=10, expand=True)

        # Estadísticas
        self.stats_frame = ctk.CTkFrame(self.main_frame)
        self.stats_frame.pack(pady=10, fill="x")

        self.sessions_label = ctk.CTkLabel(
            self.stats_frame,
            text=f"Sesiones completadas hoy: {self.sessions_completed}",
            font=("Helvetica", 14)
        )
        self.sessions_label.pack(pady=5)

    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def update_timer(self):
        if self.is_running:
            if self.time_left > 0:
                self.time_left -= 1
                # Actualizar ambos temporizadores
                self.timer_label.configure(text=self.format_time(self.time_left))
                self.update_floating_timer()
                self.timer_id = self.root.after(1000, self.update_timer)
            else:
                self.is_running = False
                if not self.is_break:
                    self.sessions_completed += 1
                    self.sessions_label.configure(
                        text=f"Sesiones completadas hoy: {self.sessions_completed}"
                    )
                    self.save_settings()
                    self.play_alert_sound()
                    self.show_break_alert()
                    self.time_left = int(self.break_time_entry.get()) * 60
                    self.is_break = True
                    self.start_timer()
                else:
                    messagebox.showinfo(
                        "¡Descanso terminado!",
                        "Es hora de volver al estudio."
                    )
                    self.time_left = int(self.work_time_entry.get()) * 60
                    self.is_break = False
                    self.start_timer()

    def start_timer(self):
        try:
            if not self.is_running:
                if not self.is_break:
                    self.work_time = int(self.work_time_entry.get())
                    if self.time_left == self.break_time * 60:
                        self.time_left = self.work_time * 60
                self.is_running = True
                self.start_button.configure(state="disabled")
                self.pause_button.configure(state="normal")
                self.update_timer()
        except ValueError:
            messagebox.showerror(
                "Error",
                "Por favor, ingresa números válidos para los tiempos de trabajo y descanso"
            )

    def pause_timer(self):
        if self.is_running:
            self.is_running = False
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.start_button.configure(state="normal")
            self.pause_button.configure(state="disabled")

    def reset_timer(self):
        self.pause_timer()
        self.is_break = False
        self.time_left = int(self.work_time_entry.get()) * 60
        self.timer_label.configure(text=self.format_time(self.time_left))
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled")
        # Actualizar la ventana flotante si existe
        if hasattr(self, 'float_window'):
            self.update_floating_timer()

    def open_settings_window(self):
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Ajustes")
        settings_window.geometry("600x700")
        settings_window.grab_set()  # Hace la ventana modal

        # Frame principal de ajustes con scroll
        settings_frame = ctk.CTkScrollableFrame(settings_window)
        settings_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Sección de Apariencia
        appearance_label = ctk.CTkLabel(
            settings_frame, 
            text="Apariencia",
            font=(self.settings["font_family"], 20, "bold")
        )
        appearance_label.pack(pady=10)

        # Tema
        theme_label = ctk.CTkLabel(settings_frame, text="Tema:", font=(self.settings["font_family"], 16))
        theme_label.pack(pady=5)
        theme_var = ctk.StringVar(value=self.settings["theme"])
        theme_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["dark", "light"],
            variable=theme_var,
            command=lambda x: self.change_theme(x)
        )
        theme_menu.pack(pady=5)

        # Transparencia
        transparency_frame = ctk.CTkFrame(settings_frame)
        transparency_frame.pack(pady=10, fill="x")
        
        transparency_label = ctk.CTkLabel(
            transparency_frame,
            text="Transparencia:",
            font=(self.settings["font_family"], 16)
        )
        transparency_label.pack(side="left", padx=10)
        
        transparency_slider = ctk.CTkSlider(
            transparency_frame,
            from_=0.5,
            to=1.0,
            number_of_steps=50,
            command=lambda x: self.change_transparency(x)
        )
        transparency_slider.set(self.settings.get("transparency", 0.95))
        transparency_slider.pack(side="right", padx=10, fill="x", expand=True)

        # Colores
        colors_label = ctk.CTkLabel(settings_frame, text="Colores:", font=(self.settings["font_family"], 16))
        colors_label.pack(pady=5)
        
        # Frame para los botones de colores
        colors_frame = ctk.CTkFrame(settings_frame)
        colors_frame.pack(pady=5, fill="x")
        
        color_options = [
            ("Color principal", "primary"),
            ("Color secundario", "secondary"),
            ("Color de acento", "accent"),
            ("Color de texto", "text"),
            ("Color de alerta", "warning")
        ]
        
        for color_name, color_key in color_options:
            color_frame = ctk.CTkFrame(colors_frame)
            color_frame.pack(pady=2, fill="x")
            
            preview = tk.Label(
                color_frame,
                bg=self.settings["custom_colors"][color_key],
                width=3,
                height=1
            )
            preview.pack(side="left", padx=5, pady=5)
            
            label = ctk.CTkLabel(
                color_frame,
                text=color_name,
                font=(self.settings["font_family"], 14)
            )
            label.pack(side="left", padx=5)
            
            button = ctk.CTkButton(
                color_frame,
                text="Cambiar",
                width=100,
                command=lambda k=color_key: self.choose_color(k)
            )
            button.pack(side="right", padx=5)

        # Fuentes
        font_section = ctk.CTkLabel(
            settings_frame,
            text="Fuentes",
            font=(self.settings["font_family"], 20, "bold")
        )
        font_section.pack(pady=10)

        # Frame para la fuente
        font_frame = ctk.CTkFrame(settings_frame)
        font_frame.pack(pady=10, fill="x")
        
        font_label = ctk.CTkLabel(
            font_frame,
            text="Fuente:",
            font=(self.settings["font_family"], 16)
        )
        font_label.pack(side="left", padx=10)
        
        # Crear un Combobox para las fuentes con búsqueda
        font_var = ctk.StringVar(value=self.settings["font_family"])
        font_entry = ctk.CTkEntry(
            font_frame,
            textvariable=font_var,
            width=200
        )
        font_entry.pack(side="left", padx=10)
        

        
        def select_font(font_name):
            font_var.set(font_name)
            font_preview.configure(font=(font_name, 14))
            self.change_font(font_name)
            
        def show_font_list():
            nonlocal font_preview  # Hacer font_preview accesible en el scope interno
            
            # Crear ventana de selección de fuente
            font_list = ctk.CTkToplevel(settings_frame)
            font_list.title("Seleccionar Fuente")
            font_list.geometry("400x600")
            font_list.grab_set()  # Hacer la ventana modal
            
            # Barra de búsqueda
            search_frame = ctk.CTkFrame(font_list)
            search_frame.pack(pady=10, padx=10, fill="x")
            
            search_label = ctk.CTkLabel(
                search_frame,
                text="Buscar fuente:",
                font=(self.settings["font_family"], 14)
            )
            search_label.pack(side="left", padx=5)
            
            search_var = ctk.StringVar()
            search_var.trace('w', lambda *args: update_filtered_list())
            
            search_entry = ctk.CTkEntry(
                search_frame,
                textvariable=search_var,
                width=200
            )
            search_entry.pack(side="left", padx=5, fill="x", expand=True)
            
            # Frame con scroll para las fuentes
            global list_frame  # Hacer accesible para la función de actualización
            list_frame = ctk.CTkScrollableFrame(font_list)
            list_frame.pack(pady=10, padx=10, fill="both", expand=True)
            
            def update_filtered_list():
                search_text = search_var.get().lower()
                filtered_fonts = [f for f in self.available_fonts if search_text in f.lower()]
                
                # Limpiar lista actual
                for widget in list_frame.winfo_children():
                    widget.destroy()
                
                # Mostrar fuentes filtradas
                for font in filtered_fonts[:100]:
                    font_button = ctk.CTkButton(
                        list_frame,
                        text=f"{font} - AaBbCc",
                        font=(font, 14),
                        command=lambda f=font: [
                            select_font(f),
                            font_list.destroy()
                        ]
                    )
                    font_button.pack(pady=2, fill="x")
            
            # Mostrar todas las fuentes inicialmente
            update_filtered_list()
        
        font_button = ctk.CTkButton(
            font_frame,
            text="Buscar",
            command=show_font_list,
            width=100
        )
        font_button.pack(side="left", padx=10)
        
        # Preview de la fuente
        font_preview = ctk.CTkLabel(
            font_frame,
            text="Vista previa AaBbCc",
            font=(font_var.get(), 14)
        )
        font_preview.pack(side="right", padx=10)

        # Tamaño de fuente
        size_label = ctk.CTkLabel(font_frame, text="Tamaño:", font=(self.settings["font_family"], 16))
        size_label.pack(side="left", padx=10)
        
        size_var = ctk.StringVar(value=str(self.settings["font_size"]))
        size_entry = ctk.CTkEntry(font_frame, width=50, textvariable=size_var)
        size_entry.pack(side="left", padx=10)

        # Espacio para futuras secciones de configuración
        spacer = ctk.CTkFrame(settings_frame, height=20)
        spacer.pack()

        # Botón para guardar
        save_button = ctk.CTkButton(
            settings_frame,
            text="Guardar cambios",
            command=lambda: self.save_visual_settings(size_var.get())
        )
        save_button.pack(pady=20)

    def choose_color(self, color_key):
        color = colorchooser.askcolor(title="Elige un color")[1]
        if color:
            self.settings["custom_colors"][color_key] = color
            self.apply_colors()

    def change_theme(self, theme):
        self.settings["theme"] = theme
        ctk.set_appearance_mode(theme)

    def change_font(self, font_family):
        self.settings["font_family"] = font_family
        self.apply_font()

    def apply_font(self):
        # Actualizar fuentes en widgets principales
        self.title_label.configure(font=(self.settings["font_family"], self.settings["font_size"], "bold"))
        self.timer_label.configure(font=(self.settings["font_family"], self.settings["font_size"] * 2))
        self.sessions_label.configure(font=(self.settings["font_family"], int(self.settings["font_size"] * 0.6)))

    def apply_colors(self):
        # Aplicar colores personalizados a los widgets
        colors = self.settings["custom_colors"]
        
        # Configurar colores del root y frames
        self.root.configure(fg_color=colors["primary"])
        for frame in [self.main_frame, self.title_frame, self.timer_frame, 
                     self.time_config_frame, self.button_frame, self.stats_frame]:
            frame.configure(
                fg_color=colors["secondary"],
                bg_color=colors["primary"]
            )

        # Configurar colores de las etiquetas
        for label in [self.title_label, self.timer_label, self.work_time_label,
                     self.break_time_label, self.sessions_label]:
            label.configure(
                text_color=colors["text"],
                fg_color="transparent"
            )

        # Configurar colores de los botones
        for button in [self.start_button, self.pause_button, self.reset_button, self.settings_button]:
            button.configure(
                fg_color=colors["accent"],
                text_color=colors["primary"],
                hover_color=colors["text"]
            )
            
        # Configurar colores de las entradas
        for entry in [self.subject_entry, self.work_time_entry, self.break_time_entry]:
            entry.configure(
                fg_color=colors["text"],
                text_color=colors["primary"],
                border_color=colors["accent"]
            )
            
        # Ajustar transparencia
        self.apply_transparency()

    def save_visual_settings(self, font_size):
        try:
            self.settings["font_size"] = int(font_size)
            self.apply_font()
            
            # Guardar configuración en archivo
            visual_settings = {
                "theme": self.settings["theme"],
                "color_theme": self.settings["color_theme"],
                "font_family": self.settings["font_family"],
                "font_size": self.settings["font_size"],
                "custom_colors": self.settings["custom_colors"]
            }
            
            with open("pomodoro_visual_settings.json", "w") as f:
                json.dump(visual_settings, f)
                
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        except ValueError:
            messagebox.showerror("Error", "El tamaño de fuente debe ser un número")

    def load_visual_settings(self):
        try:
            with open("pomodoro_visual_settings.json", "r") as f:
                visual_settings = json.load(f)
                self.settings.update(visual_settings)
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings = {
            "work_time": self.work_time,
            "break_time": self.break_time,
            "sessions_completed": self.sessions_completed,
            "last_date": datetime.now().strftime("%Y-%m-%d")
        }
        with open("pomodoro_settings.json", "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open("pomodoro_settings.json", "r") as f:
                settings = json.load(f)
                if settings["last_date"] == datetime.now().strftime("%Y-%m-%d"):
                    self.sessions_completed = settings["sessions_completed"]
                self.work_time = settings["work_time"]
                self.break_time = settings["break_time"]
                self.work_time_entry.delete(0, tk.END)
                self.work_time_entry.insert(0, str(self.work_time))
                self.break_time_entry.delete(0, tk.END)
                self.break_time_entry.insert(0, str(self.break_time))
        except FileNotFoundError:
            pass

    def apply_transparency(self):
        opacity = self.settings.get("transparency", 0.95)
        self.root.attributes('-alpha', opacity)

    def play_alert_sound(self):
        if self.settings.get("alert_sound", True):
            try:
                # Reproducir el sonido en un hilo separado para no bloquear la interfaz
                sound_thread = threading.Thread(
                    target=lambda: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                )
                sound_thread.start()
            except Exception:
                pass  # Si hay error al reproducir el sonido, lo ignoramos

    def show_break_alert(self):
        # Actualizar la ventana flotante si existe
        self.update_floating_timer()
        
        # Crear una nueva ventana de alerta
        alert = ctk.CTkToplevel(self.root)
        alert.title("¡Tiempo de descanso!")
        alert.geometry("400x300")
        
        # Configurar colores
        alert.configure(fg_color=self.settings["custom_colors"]["warning"])
        
        # Mensaje principal
        message = ctk.CTkLabel(
            alert,
            text="¡Es hora de descansar!\n\nToma un respiro, estírate\ny descansa la vista.",
            font=(self.settings["font_family"], 20),
            text_color=self.settings["custom_colors"]["text"]
        )
        message.pack(pady=20)
        
        # Tiempo restante de descanso
        time_label = ctk.CTkLabel(
            alert,
            text=f"Tiempo de descanso: {self.break_time} minutos",
            font=(self.settings["font_family"], 16),
            text_color=self.settings["custom_colors"]["text"]
        )
        time_label.pack(pady=10)
        
        # Botón para cerrar
        close_button = ctk.CTkButton(
            alert,
            text="Entendido",
            command=alert.destroy,
            fg_color=self.settings["custom_colors"]["accent"],
            text_color=self.settings["custom_colors"]["primary"]
        )
        close_button.pack(pady=20)
        
        # Centrar la ventana
        alert.lift()
        alert.grab_set()

    def change_transparency(self, value):
        self.settings["transparency"] = value
        self.apply_transparency()

    def create_floating_timer(self):
        # Crear ventana flotante
        self.float_window = ctk.CTkToplevel(self.root)
        self.float_window.overrideredirect(True)  # Quitar bordes de la ventana
        self.float_window.geometry("250x100")
        self.float_window.attributes('-topmost', True)  # Mantener siempre visible
        
        # Frame principal
        float_frame = ctk.CTkFrame(self.float_window)
        float_frame.pack(expand=True, fill="both")
        
        # Título del estudio
        self.float_title_label = ctk.CTkLabel(
            float_frame,
            text=self.subject_entry.get() or "Estudiando...",
            font=(self.settings["font_family"], 12),
            text_color=self.settings["custom_colors"]["text"]
        )
        self.float_title_label.pack(pady=(5, 0))
        
        # Etiqueta del temporizador
        self.float_timer_label = ctk.CTkLabel(
            float_frame,
            text=self.format_time(self.time_left),
            font=(self.settings["font_family"], 36)
        )
        self.float_timer_label.pack(pady=5)
        
        # Control de transparencia (oculto por defecto)
        self.transparency_frame = ctk.CTkFrame(float_frame, fg_color="transparent")
        transparency_slider = ctk.CTkSlider(
            self.transparency_frame,
            from_=0.1,
            to=1.0,
            number_of_steps=90,
            width=150,
            command=self.change_float_transparency
        )
        transparency_slider.set(0.8)
        transparency_slider.pack(pady=5)
        
        # Configurar colores
        float_frame.configure(
            fg_color=self.settings["custom_colors"]["secondary"],
            bg_color=self.settings["custom_colors"]["primary"]
        )
        self.float_timer_label.configure(
            text_color=self.settings["custom_colors"]["text"]
        )
        
        # Hacer la ventana draggable
        float_frame.bind('<Button-1>', self.start_drag)
        float_frame.bind('<B1-Motion>', self.do_drag)
        
        # Mostrar/ocultar controles de transparencia al hacer doble clic
        float_frame.bind('<Double-Button-1>', self.toggle_transparency_controls)
        
        # Iniciar con una transparencia predeterminada
        self.change_float_transparency(0.8)

    def change_float_transparency(self, value):
        if hasattr(self, 'float_window'):
            self.float_window.attributes('-alpha', value)

    def start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def do_drag(self, event):
        if hasattr(self, 'float_window'):
            x = self.float_window.winfo_x() + (event.x - self._drag_start_x)
            y = self.float_window.winfo_y() + (event.y - self._drag_start_y)
            self.float_window.geometry(f"+{x}+{y}")
            
    def toggle_transparency_controls(self, event):
        if hasattr(self, 'transparency_frame'):
            if self.transparency_frame.winfo_manager():
                self.transparency_frame.pack_forget()
                self.float_window.geometry("250x100")
            else:
                self.transparency_frame.pack(fill="x", pady=5)
                self.float_window.geometry("250x140")

    def toggle_float_window(self):
        if hasattr(self, 'float_window'):
            self.float_window.destroy()
            delattr(self, 'float_window')
            self.float_button.configure(text="🔲 Ventana flotante")
        else:
            self.create_floating_timer()
            self.float_button.configure(text="✖️ Cerrar flotante")

    def update_floating_timer(self):
        try:
            if hasattr(self, 'float_window') and self.float_window.winfo_exists():
                if hasattr(self, 'float_timer_label'):
                    self.float_timer_label.configure(text=self.format_time(self.time_left))
                if hasattr(self, 'float_title_label'):
                    self.float_title_label.configure(text=self.subject_entry.get() or "Estudiando...")
        except (tk.TclError, AttributeError):
            # Si hay algún error con la ventana, la eliminamos completamente
            if hasattr(self, 'float_window'):
                delattr(self, 'float_window')
            if hasattr(self, 'float_timer_label'):
                delattr(self, 'float_timer_label')
            if hasattr(self, 'float_title_label'):
                delattr(self, 'float_title_label')
            # Restaurar el estado del botón
            self.float_button.configure(text="🔲 Ventana flotante")

if __name__ == "__main__":
    app = PomodoroApp()
    app.root.mainloop()
