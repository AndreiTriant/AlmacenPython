"""
main.py - Punto de entrada de la aplicación.

Sistema de Monitorización Climática para Almacén Farmacéutico.
Inicializa la base de datos, crea las instancias del patrón MVC
y lanza la interfaz gráfica.
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.repositories.configdb import ConfigDB
from app.view.ventana_ppal import VentanaPrincipal
from app.controller.controlador_ppal import ControladorPrincipal


def main():
    """Función principal que arranca la aplicación."""

    # 1. Inicializar base de datos (singleton)
    print("[INFO] Inicializando base de datos...")
    db = ConfigDB()
    print(f"[INFO] Base de datos lista.")

    # 2. Crear la Vista
    print("[INFO] Creando interfaz gráfica...")
    vista = VentanaPrincipal()

    # 3. Crear el Controlador e inyectar la vista
    controlador = ControladorPrincipal(vista)

    # 4. Inyectar el controlador en la vista (conexión bidireccional)
    vista.set_controlador(controlador)

    print("[INFO] Aplicación lista. Iniciando...")
    print("=" * 50)
    print("  Monitor Climático — Almacén Farmacéutico")
    print("  Actualización cada 30 segundos")
    print("  Alerta si temperatura > 25°C")
    print("=" * 50)

    # 5. Lanzar el loop principal de Tkinter
    vista.ejecutar()


if __name__ == "__main__":
    main()
