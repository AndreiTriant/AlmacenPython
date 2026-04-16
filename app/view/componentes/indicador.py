"""
indicador.py - Componente visual de indicador numérico.

Muestra un valor grande con etiqueta y unidad,
cambiando de color según el estado (normal/alerta).
"""

import tkinter as tk


class Indicador(tk.Frame):
    """Widget que muestra un valor numérico grande con etiqueta y color de estado."""

    COLOR_NORMAL = "#10B981"      # Verde esmeralda
    COLOR_ALERTA = "#EF4444"      # Rojo
    COLOR_FONDO = "#1E293B"       # Fondo oscuro
    COLOR_TEXTO = "#F8FAFC"       # Texto claro

    def __init__(self, master, titulo="", unidad="", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=self.COLOR_FONDO, padx=20, pady=15)

        self._titulo = titulo
        self._unidad = unidad

        # Etiqueta del título
        self.lbl_titulo = tk.Label(
            self,
            text=titulo,
            font=("Segoe UI", 12, "bold"),
            fg="#94A3B8",
            bg=self.COLOR_FONDO,
        )
        self.lbl_titulo.pack()

        # Valor numérico
        self.lbl_valor = tk.Label(
            self,
            text="--",
            font=("Segoe UI", 40, "bold"),
            fg=self.COLOR_NORMAL,
            bg=self.COLOR_FONDO,
        )
        self.lbl_valor.pack()

        # Unidad
        self.lbl_unidad = tk.Label(
            self,
            text=unidad,
            font=("Segoe UI", 14),
            fg="#94A3B8",
            bg=self.COLOR_FONDO,
        )
        self.lbl_unidad.pack()

    def actualizar(self, valor, alerta=False):
        """Actualiza el valor mostrado y el color según el estado."""
        self.lbl_valor.config(
            text=f"{valor:.1f}",
            fg=self.COLOR_ALERTA if alerta else self.COLOR_NORMAL,
        )

    def resetear(self):
        """Restaura el indicador a su estado por defecto."""
        self.lbl_valor.config(text="--", fg=self.COLOR_NORMAL)
