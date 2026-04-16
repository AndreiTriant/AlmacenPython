"""
almacen.py - Modelo de datos del almacén farmacéutico.

Representa una lectura de sensor con temperatura, humedad y marca temporal.
Incluye un generador de lecturas simuladas para pruebas.
"""

import random
from datetime import datetime


class Almacen:
    """Modelo que representa una lectura de sensor del almacén."""

    # Umbrales de alerta
    UMBRAL_TEMP_MAX = 25.0   # °C

    def __init__(self, temperatura=0.0, humedad=0.0, fecha=None, hora=None, id_almacen=1):
        self.temperatura = temperatura
        self.humedad = humedad
        ahora = datetime.now()
        self.fecha = fecha or ahora.strftime("%Y-%m-%d")
        self.hora = hora or ahora.strftime("%H:%M:%S")
        self.id_almacen = id_almacen

    # ------------------------------------------------------------------ #
    #  Validaciones
    # ------------------------------------------------------------------ #
    @property
    def alerta_temperatura(self):
        """Devuelve True si la temperatura supera el umbral."""
        return self.temperatura > self.UMBRAL_TEMP_MAX

    @property
    def estado(self):
        """Devuelve el estado de la lectura como texto."""
        if self.alerta_temperatura:
            return "⚠ ALERTA"
        return "✓ Normal"

    # ------------------------------------------------------------------ #
    #  Simulación
    # ------------------------------------------------------------------ #
    @staticmethod
    def generar_lectura_simulada(id_almacen=1):
        """
        Genera una lectura simulada con valores realistas.

        Temperatura: 18 - 30 °C  (con mayor probabilidad cerca de 23-26)
        Humedad:     40 - 80 %
        """
        # Distribución que favorece valores cercanos al umbral para demostrar alertas
        temperatura = round(random.gauss(24.0, 3.0), 1)
        temperatura = max(18.0, min(30.0, temperatura))  # Clamp

        humedad = round(random.uniform(40.0, 80.0), 1)

        ahora = datetime.now()
        return Almacen(
            temperatura=temperatura,
            humedad=humedad,
            fecha=ahora.strftime("%Y-%m-%d"),
            hora=ahora.strftime("%H:%M:%S"),
            id_almacen=id_almacen,
        )

    # ------------------------------------------------------------------ #
    #  Representación
    # ------------------------------------------------------------------ #
    def __repr__(self):
        return (
            f"Almacen(temp={self.temperatura}°C, hum={self.humedad}%, "
            f"fecha={self.fecha}, hora={self.hora}, "
            f"almacen={self.id_almacen}, estado={self.estado})"
        )
