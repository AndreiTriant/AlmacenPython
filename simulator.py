import time
import random
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

API_URL = "http://127.0.0.1:5000/ingest"

def simulate_sensor():
    logging.info("Iniciando simulador de sensor. Presiona Ctrl+C para detener.")
    while True:
        # Temperatura normal 20-24, ocasionalmente picos >25 para probar la alerta extra
        if random.random() < 0.15:
            temperatura = round(random.uniform(25.1, 28.0), 2)
            logging.warning(f"Generando pico de temperatura! {temperatura}°C")
        else:
            temperatura = round(random.uniform(20.0, 24.5), 2)
            
        humedad = round(random.uniform(40.0, 60.0), 2)
        
        payload = {
            "temperatura": temperatura,
            "humedad": humedad
        }
        
        try:
            response = requests.post(API_URL, json=payload, timeout=2)
            if response.status_code == 201:
                logging.info(f"Datos enviados correctamente: T={temperatura}°C, H={humedad}%")
            else:
                logging.error(f"Error del servidor: {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error de conexión (Asegúrate de que app/api.py esté corriendo): {e}")
            
        # Emitimos con menos frecuencia (cada 10s) para que se observe bien la mezcla
        # con la inyección que hace la interfaz Tkinter por su cuenta cada 30s.
        time.sleep(10)

if __name__ == "__main__":
    try:
        simulate_sensor()
    except KeyboardInterrupt:
        logging.info("Simulador detenido manualmente.")
