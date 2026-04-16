"""
ventana_ppal.py - Ventana principal de la aplicación (Vista MVC).

Interfaz de usuario Tkinter con indicadores, tabla de historial,
botones de control y botones de intervalo temporal para gráficos Plotly.
"""

import tkinter as tk
from tkinter import messagebox
from app.view.componentes.indicador import Indicador
from app.view.componentes.tabla_lecturas import TablaLecturas
from app.view.componentes.grafico_realtime import GraficoRealtime


class VentanaPrincipal:
    """Vista principal de la aplicación de monitorización climática."""

    # Colores
    COLOR_FONDO = "#0F172A"          # Azul muy oscuro
    COLOR_PANEL = "#1E293B"          # Panel oscuro
    COLOR_ALERTA = "#7F1D1D"         # Rojo oscuro para fondo de alerta
    COLOR_BOTON = "#3B82F6"          # Azul
    COLOR_BOTON_STOP = "#EF4444"     # Rojo
    COLOR_BOTON_INTERVALO = "#6366F1"  # Indigo
    COLOR_TEXTO = "#F8FAFC"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏭 Monitor Climático — Almacén Farmacéutico")
        self.root.geometry("950x900")
        self.root.configure(bg=self.COLOR_FONDO)
        self.root.resizable(True, True)

        self._controlador = None
        self._estado_alerta = False

        self._construir_interfaz()

    def set_controlador(self, controlador):
        """Inyecta el controlador después de la construcción."""
        self._controlador = controlador

    # ================================================================== #
    #  Construcción de la interfaz
    # ================================================================== #
    def _construir_interfaz(self):
        """Construye todos los widgets de la ventana principal."""

        # ---- Titulo ----
        frame_titulo = tk.Frame(self.root, bg=self.COLOR_FONDO)
        frame_titulo.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(
            frame_titulo,
            text="🏭 Monitor Climático",
            font=("Segoe UI", 22, "bold"),
            fg=self.COLOR_TEXTO,
            bg=self.COLOR_FONDO,
        ).pack(side="left")

        self.lbl_estado = tk.Label(
            frame_titulo,
            text="⏸ Detenido",
            font=("Segoe UI", 11),
            fg="#94A3B8",
            bg=self.COLOR_FONDO,
        )
        self.lbl_estado.pack(side="right")

        # ---- Indicadores ----
        frame_indicadores = tk.Frame(self.root, bg=self.COLOR_FONDO)
        frame_indicadores.pack(fill="x", padx=20, pady=10)

        self.indicador_temp = Indicador(
            frame_indicadores, titulo="🌡️ Temperatura", unidad="°C"
        )
        self.indicador_temp.pack(side="left", expand=True, fill="both", padx=(0, 5))

        self.indicador_hum = Indicador(
            frame_indicadores, titulo="💧 Humedad", unidad="%"
        )
        self.indicador_hum.pack(side="left", expand=True, fill="both", padx=(5, 0))

        # ---- Gráfico en tiempo real ----
        self.grafico = GraficoRealtime(self.root)
        self.grafico.pack(fill="both", expand=True, padx=20, pady=(5, 5))

        # ---- Panel de botones de control ----
        frame_botones = tk.Frame(self.root, bg=self.COLOR_FONDO)
        frame_botones.pack(fill="x", padx=20, pady=(5, 0))

        self.btn_iniciar = tk.Button(
            frame_botones,
            text="▶  Iniciar Monitoreo",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLOR_BOTON,
            fg="white",
            activebackground="#2563EB",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._on_iniciar,
        )
        self.btn_iniciar.pack(side="left", padx=(0, 8))

        self.btn_detener = tk.Button(
            frame_botones,
            text="⏹  Detener",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLOR_BOTON_STOP,
            fg="white",
            activebackground="#DC2626",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            state="disabled",
            command=self._on_detener,
        )
        self.btn_detener.pack(side="left")

        # ---- Panel de botones de intervalo temporal ----
        frame_intervalos = tk.Frame(self.root, bg=self.COLOR_FONDO)
        frame_intervalos.pack(fill="x", padx=20, pady=(10, 5))

        tk.Label(
            frame_intervalos,
            text="📊 Ver gráfico por intervalo:",
            font=("Segoe UI", 10, "bold"),
            fg="#94A3B8",
            bg=self.COLOR_FONDO,
        ).pack(side="left", padx=(0, 10))

        intervalos = ["5 Minutos", "60 Minutos", "2 Horas", "7 Días"]
        for etiqueta in intervalos:
            btn = tk.Button(
                frame_intervalos,
                text=etiqueta,
                font=("Segoe UI", 10),
                bg=self.COLOR_BOTON_INTERVALO,
                fg="white",
                activebackground="#4F46E5",
                activeforeground="white",
                relief="flat",
                padx=12,
                pady=5,
                cursor="hand2",
                command=lambda e=etiqueta: self._on_intervalo(e),
            )
            btn.pack(side="left", padx=3)

        # ---- Separador ----
        sep = tk.Frame(self.root, height=2, bg="#334155")
        sep.pack(fill="x", padx=20, pady=10)

        # ---- Tabla de historial ----
        self.tabla = TablaLecturas(self.root)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    # ================================================================== #
    #  Callbacks de botones
    # ================================================================== #
    def _on_iniciar(self):
        if self._controlador:
            self._controlador.iniciar_monitoreo()

    def _on_detener(self):
        if self._controlador:
            self._controlador.detener_monitoreo()

    def _on_intervalo(self, etiqueta):
        if self._controlador:
            self._controlador.mostrar_grafico_intervalo(etiqueta)

    # ================================================================== #
    #  Métodos públicos para el controlador
    # ================================================================== #
    def actualizar_indicador_temperatura(self, valor):
        """Actualiza el indicador de temperatura."""
        self.indicador_temp.actualizar(valor, alerta=(valor > 25.0))

    def actualizar_indicador_humedad(self, valor):
        """Actualiza el indicador de humedad."""
        self.indicador_hum.actualizar(valor)

    def actualizar_tabla(self, lecturas):
        """Actualiza la tabla del historial con las lecturas proporcionadas."""
        self.tabla.actualizar(lecturas)

    def actualizar_grafico(self, lecturas):
        """Actualiza el gráfico en tiempo real con las lecturas proporcionadas."""
        self.grafico.actualizar(lecturas)

    def actualizar_estado_monitoreo(self, activo):
        """Actualiza los botones y la etiqueta de estado."""
        if activo:
            self.lbl_estado.config(text="🟢 Monitoreando (cada 30s)", fg="#10B981")
            self.btn_iniciar.config(state="disabled")
            self.btn_detener.config(state="normal")
        else:
            self.lbl_estado.config(text="⏸ Detenido", fg="#94A3B8")
            self.btn_iniciar.config(state="normal")
            self.btn_detener.config(state="disabled")

    def mostrar_alerta(self, temperatura):
        """Cambia el fondo a rojo y muestra un pop-up de alerta."""
        if not self._estado_alerta:
            self._estado_alerta = True
            self.root.configure(bg=self.COLOR_ALERTA)
            messagebox.showwarning(
                "⚠ Alerta de Temperatura",
                f"¡La temperatura ha superado los 25°C!\n\n"
                f"Temperatura actual: {temperatura:.1f}°C\n\n"
                f"Revise el sistema de refrigeración del almacén.",
            )

    def restaurar_estado_normal(self):
        """Restaura el fondo a su color normal."""
        if self._estado_alerta:
            self._estado_alerta = False
            self.root.configure(bg=self.COLOR_FONDO)

    def mostrar_info_sin_datos(self, etiqueta):
        """Muestra un mensaje informativo cuando no hay datos para el intervalo."""
        messagebox.showinfo(
            "Sin datos",
            f"No hay lecturas registradas en los últimos {etiqueta}.\n"
            f"Inicie el monitoreo y espere a que se acumulen datos.",
        )

    # ================================================================== #
    #  Loop principal
    # ================================================================== #
    def ejecutar(self):
        """Inicia el mainloop de Tkinter."""
        self.root.mainloop()
