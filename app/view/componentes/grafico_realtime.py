"""
grafico_realtime.py - Gráfico en tiempo real embebido en Tkinter.

Usa matplotlib con FigureCanvasTkAgg para mostrar las líneas de
temperatura y humedad directamente dentro de la ventana principal.
"""

import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraficoRealtime(tk.Frame):
    """Widget que muestra un gráfico en tiempo real de temperatura y humedad."""

    COLOR_FONDO_GRAFICO = "#0F172A"
    COLOR_EJES = "#94A3B8"
    UMBRAL_TEMP = 25.0
    MAX_PUNTOS = 60  # Máximo de puntos visibles

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=self.COLOR_FONDO_GRAFICO)

        # Datos acumulados
        self._fechas = []
        self._temperaturas = []
        self._humedades = []

        self._crear_grafico()

    def _crear_grafico(self):
        """Crea la figura de matplotlib con dos ejes Y."""
        self.fig = Figure(figsize=(8, 2.8), dpi=100, facecolor=self.COLOR_FONDO_GRAFICO)
        self.fig.subplots_adjust(left=0.08, right=0.92, top=0.88, bottom=0.18)

        # Eje principal: temperatura
        self.ax_temp = self.fig.add_subplot(111)
        self.ax_temp.set_facecolor("#1E293B")
        self.ax_temp.set_title(
            "📈 Monitorización en Tiempo Real",
            color="#F8FAFC", fontsize=12, fontweight="bold", pad=8,
        )
        self.ax_temp.set_ylabel("Temperatura (°C)", color="#EF4444", fontsize=9)
        self.ax_temp.tick_params(axis="y", colors="#EF4444", labelsize=8)
        self.ax_temp.tick_params(axis="x", colors=self.COLOR_EJES, labelsize=7, rotation=30)
        self.ax_temp.spines["top"].set_visible(False)
        self.ax_temp.spines["bottom"].set_color(self.COLOR_EJES)
        self.ax_temp.spines["left"].set_color("#EF4444")
        self.ax_temp.spines["right"].set_color("#3B82F6")
        self.ax_temp.grid(True, alpha=0.15, color=self.COLOR_EJES)

        # Línea de umbral
        self.ax_temp.axhline(
            y=self.UMBRAL_TEMP, color="#EF4444", linestyle="--", linewidth=1, alpha=0.6, label="Umbral 25°C"
        )

        # Eje secundario: humedad
        self.ax_hum = self.ax_temp.twinx()
        self.ax_hum.set_ylabel("Humedad (%)", color="#3B82F6", fontsize=9)
        self.ax_hum.tick_params(axis="y", colors="#3B82F6", labelsize=8)

        # Líneas iniciales vacías
        self.linea_temp, = self.ax_temp.plot(
            [], [], color="#EF4444", linewidth=2, marker="o", markersize=4, label="Temperatura"
        )
        self.linea_hum, = self.ax_hum.plot(
            [], [], color="#3B82F6", linewidth=2, marker="s", markersize=3, label="Humedad"
        )

        # Leyenda combinada
        lineas = [self.linea_temp, self.linea_hum]
        etiquetas = [l.get_label() for l in lineas]
        self.ax_temp.legend(
            lineas, etiquetas, loc="upper left", fontsize=8,
            facecolor="#1E293B", edgecolor="#334155", labelcolor="#F8FAFC",
        )

        # Canvas de Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.draw()

    def actualizar(self, lecturas):
        """
        Actualiza el gráfico con la lista completa de últimas lecturas.

        Args:
            lecturas: lista de dicts con claves 'fecha', 'hora', 'temperatura', 'humedad'
        """
        if not lecturas:
            return

        # Tomar los últimos MAX_PUNTOS
        datos = lecturas[-self.MAX_PUNTOS:]

        fechas = [l["hora"] for l in datos]  # HH:MM:SS
        temperaturas = [l["temperatura"] for l in datos]
        humedades = [l["humedad"] for l in datos]

        # Actualizar datos de las líneas
        self.linea_temp.set_data(range(len(fechas)), temperaturas)
        self.linea_hum.set_data(range(len(fechas)), humedades)

        # Ajustar ejes
        if fechas:
            self.ax_temp.set_xlim(-0.5, len(fechas) - 0.5)
            self.ax_temp.set_xticks(range(len(fechas)))
            self.ax_temp.set_xticklabels(fechas, rotation=30, ha="right", fontsize=7)

        if temperaturas:
            t_min = min(min(temperaturas), self.UMBRAL_TEMP) - 2
            t_max = max(max(temperaturas), self.UMBRAL_TEMP) + 2
            self.ax_temp.set_ylim(t_min, t_max)

        if humedades:
            h_min = min(humedades) - 5
            h_max = max(humedades) + 5
            self.ax_hum.set_ylim(h_min, h_max)

        # Redibujar
        self.canvas.draw_idle()
