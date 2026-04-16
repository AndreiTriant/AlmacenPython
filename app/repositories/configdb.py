"""
configdb.py - Configuración y conexión a la base de datos SQLite.

Provee acceso centralizado a la base de datos para almacenar
las lecturas de temperatura y humedad del almacén farmacéutico,
así como las alarmas generadas.
"""

import sqlite3
import os
from datetime import datetime, timedelta


class ConfigDB:
    """Clase singleton para gestionar la conexión a SQLite."""

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(self):
        if self._inicializado:
            return
        self._ruta_db = self._resolver_ruta_db()
        self._inicializado = True
        self.crear_tablas()

    def _resolver_ruta_db(self):
        """Resuelve una ruta de base de datos compatible con local y Vercel."""
        ruta_configurada = os.getenv("TEMPHR_DB_PATH")
        if ruta_configurada:
            return ruta_configurada

        if os.getenv("VERCEL"):
            return os.path.join("/tmp", "sqlite.db")

        # En local, la base de datos se crea junto a este archivo
        directorio = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(directorio, "sqlite.db")

    # ------------------------------------------------------------------ #
    #  Conexión
    # ------------------------------------------------------------------ #
    def _conectar(self):
        """Crea y devuelve una nueva conexión a SQLite."""
        conn = sqlite3.connect(self._ruta_db)
        conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        return conn

    # ------------------------------------------------------------------ #
    #  DDL
    # ------------------------------------------------------------------ #
    def crear_tablas(self):
        """Crea las tablas 'lecturas' y 'alarmas' si no existen."""
        conn = self._conectar()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lecturas (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    temperatura REAL    NOT NULL,
                    humedad     REAL    NOT NULL,
                    fecha       TEXT    NOT NULL,
                    hora        TEXT    NOT NULL,
                    id_almacen  INTEGER NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alarmas (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha        TEXT    NOT NULL,
                    hora         TEXT    NOT NULL,
                    valor_alarma REAL    NOT NULL,
                    almacen      INTEGER NOT NULL,
                    FOREIGN KEY (almacen) REFERENCES lecturas (id_almacen)
                )
            """)
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------ #
    #  CRUD — Lecturas
    # ------------------------------------------------------------------ #
    def insertar_lectura(self, temperatura, humedad, fecha=None, hora=None, id_almacen=1):
        """Inserta una nueva lectura en la base de datos."""
        ahora = datetime.now()
        if fecha is None:
            fecha = ahora.strftime("%Y-%m-%d")
        if hora is None:
            hora = ahora.strftime("%H:%M:%S")
        conn = self._conectar()
        try:
            cursor = conn.execute(
                "INSERT INTO lecturas (temperatura, humedad, fecha, hora, id_almacen) "
                "VALUES (?, ?, ?, ?, ?)",
                (temperatura, humedad, fecha, hora, id_almacen),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def obtener_lecturas(self):
        """Devuelve todas las lecturas ordenadas por fecha y hora."""
        conn = self._conectar()
        try:
            cursor = conn.execute(
                "SELECT * FROM lecturas ORDER BY fecha ASC, hora ASC"
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def obtener_ultimas_lecturas(self, n=20):
        """Devuelve las últimas *n* lecturas."""
        conn = self._conectar()
        try:
            cursor = conn.execute(
                "SELECT * FROM lecturas ORDER BY fecha DESC, hora DESC LIMIT ?", (n,)
            )
            filas = [dict(row) for row in cursor.fetchall()]
            filas.reverse()  # Orden cronológico
            return filas
        finally:
            conn.close()

    def obtener_lecturas_por_intervalo(self, minutos):
        """Devuelve las lecturas dentro de los últimos *minutos* minutos."""
        limite = datetime.now() - timedelta(minutes=minutos)
        fecha_limite = limite.strftime("%Y-%m-%d")
        hora_limite = limite.strftime("%H:%M:%S")
        conn = self._conectar()
        try:
            cursor = conn.execute(
                "SELECT * FROM lecturas "
                "WHERE (fecha > ? OR (fecha = ? AND hora >= ?)) "
                "ORDER BY fecha ASC, hora ASC",
                (fecha_limite, fecha_limite, hora_limite),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------ #
    #  CRUD — Alarmas
    # ------------------------------------------------------------------ #
    def insertar_alarma(self, fecha, hora, valor_alarma, almacen):
        """Inserta una nueva alarma en la base de datos.

        Args:
            fecha: fecha de la alarma (TEXT)
            hora: hora de la alarma (TEXT)
            valor_alarma: valor de temperatura que disparó la alarma (REAL)
            almacen: id de la lectura asociada (FOREIGN KEY → lecturas.id)
        """
        conn = self._conectar()
        try:
            conn.execute(
                "INSERT INTO alarmas (fecha, hora, valor_alarma, almacen) "
                "VALUES (?, ?, ?, ?)",
                (fecha, hora, valor_alarma, almacen),
            )
            conn.commit()
        finally:
            conn.close()

    def obtener_alarmas(self):
        """Devuelve todas las alarmas ordenadas por fecha y hora."""
        conn = self._conectar()
        try:
            cursor = conn.execute(
                "SELECT * FROM alarmas ORDER BY fecha ASC, hora ASC"
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
