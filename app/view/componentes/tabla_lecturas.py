"""
tabla_lecturas.py - Componente de tabla para mostrar historial de lecturas.

Usa ttk.Treeview para mostrar las últimas lecturas con formato tabular.
"""

import tkinter as tk
from tkinter import ttk


class TablaLecturas(tk.Frame):
    """Widget que muestra un historial de lecturas en formato tabla."""

    COLOR_FONDO = "#1E293B"
    COLOR_TEXTO = "#F8FAFC"
    UMBRAL_TEMP = 25.0

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=self.COLOR_FONDO)

        # Título de la sección
        lbl_titulo = tk.Label(
            self,
            text="📋 Historial de Lecturas",
            font=("Segoe UI", 13, "bold"),
            fg="#94A3B8",
            bg=self.COLOR_FONDO,
        )
        lbl_titulo.pack(anchor="w", padx=10, pady=(10, 5))

        # Estilo personalizado
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background="#0F172A",
            foreground=self.COLOR_TEXTO,
            fieldbackground="#0F172A",
            font=("Segoe UI", 10),
            rowheight=28,
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#334155",
            foreground=self.COLOR_TEXTO,
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#3B82F6")],
        )

        # Treeview
        columnas = ("fecha", "hora", "temperatura", "humedad", "id_almacen", "estado")
        self.tree = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            style="Custom.Treeview",
            height=10,
        )

        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("temperatura", text="Temperatura (°C)")
        self.tree.heading("humedad", text="Humedad (%)")
        self.tree.heading("id_almacen", text="Almacén")
        self.tree.heading("estado", text="Estado")

        self.tree.column("fecha", width=120, anchor="center")
        self.tree.column("hora", width=100, anchor="center")
        self.tree.column("temperatura", width=130, anchor="center")
        self.tree.column("humedad", width=110, anchor="center")
        self.tree.column("id_almacen", width=80, anchor="center")
        self.tree.column("estado", width=110, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 10))

        # Tags para colores de fila
        self.tree.tag_configure("alerta", foreground="#EF4444")
        self.tree.tag_configure("normal", foreground="#10B981")

    def actualizar(self, lecturas):
        """Reemplaza el contenido de la tabla con las lecturas proporcionadas."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insertar lecturas
        for lectura in lecturas:
            temp = lectura["temperatura"]
            hum = lectura["humedad"]
            fecha = lectura["fecha"]
            hora = lectura["hora"]
            id_almacen = lectura["id_almacen"]
            es_alerta = temp > self.UMBRAL_TEMP
            estado = "⚠ ALERTA" if es_alerta else "✓ Normal"
            tag = "alerta" if es_alerta else "normal"

            self.tree.insert(
                "",
                "end",
                values=(fecha, hora, f"{temp:.1f}", f"{hum:.1f}", id_almacen, estado),
                tags=(tag,),
            )

        # Hacer scroll hasta el final
        children = self.tree.get_children()
        if children:
            self.tree.see(children[-1])
