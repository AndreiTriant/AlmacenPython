"""
alarma.py - Modelo de datos de alarmas.

Representa una alarma generada cuando una lectura
supera los umbrales definidos en el sistema.
"""

from datetime import datetime


class Alarma:
    """Modelo que representa una alarma del sistema de monitorización."""

    def __init__(self, fecha=None, hora=None, valor_alarma=0.0, almacen=None):
        ahora = datetime.now()
        self.fecha = fecha or ahora.strftime("%Y-%m-%d")
        self.hora = hora or ahora.strftime("%H:%M:%S")
        self.valor_alarma = valor_alarma
        self.almacen = almacen  # FK → lecturas.id

    # ------------------------------------------------------------------ #
    #  Representación
    # ------------------------------------------------------------------ #
    def __repr__(self):
        return (
            f"Alarma(fecha={self.fecha}, hora={self.hora}, "
            f"valor={self.valor_alarma}, almacen={self.almacen})"
        )
