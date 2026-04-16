import os
import json
import sys
from datetime import datetime

# Agregamos la ruta del proyecto actual al PYTHONPATH para evitar errores de modulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from app.repositories.configdb import ConfigDB

app = Flask(__name__)
db = None


def get_db():
    """Inicializa la base de datos bajo demanda para despliegues serverless."""
    global db
    if db is None:
        db = ConfigDB()
    return db

@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/ingest', methods=['POST'])
def ingest_data():
    """Endpoint HTTP Post para la recepción de los datos climáticos del sensor."""
    data = request.json
    if not data or 'temperatura' not in data or 'humedad' not in data:
        return jsonify({"error": "Faltan parametros temperatura o humedad"}), 400
    
    try:
        temp = float(data['temperatura'])
        hum = float(data['humedad'])
        db = get_db()
        # La BD autogenera la fecha u hora si pasamos None o nada
        lectura_id = db.insertar_lectura(temp, hum)
        
        # Registrar alerta si es pertinente, tal como lo hacía el viejo simulador
        if temp > 25.0:
            ahora = datetime.now()
            db.insertar_alarma(
                fecha=ahora.strftime("%Y-%m-%d"), 
                hora=ahora.strftime("%H:%M:%S"), 
                valor_alarma=temp, 
                almacen=lectura_id
            )
            
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Monitor Almacén - Web Dashboard (Plotly.js)</title>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
    <style>
        body { background-color: #1e1e1e; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden;}
        .alert { background-color: #8b0000; padding: 15px; text-align: center; display: none; margin-bottom: 0px; font-weight: bold; flex-shrink: 0;}
        .header { text-align: center; border-bottom: 1px solid #333; padding: 20px; background-color: #252526; flex-shrink: 0;}
        .header h1 { margin: 0 0 5px 0; }
        .container { display: flex; flex-grow: 1; overflow: hidden; }
        .sidebar { width: 300px; background-color: #252526; padding: 20px; border-right: 1px solid #333; display: flex; flex-direction: column; overflow: hidden;}
        .content { flex-grow: 1; padding: 20px; display: flex; justify-content: center; align-items: stretch; overflow: hidden;}
        #plot { width: 100%; height: 100%; }
        .stat-box { background-color: #333; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
        .stat-box h3 { margin-top: 0; margin-bottom: 10px; font-size: 14px; color: #ccc; text-transform: uppercase;}
        .stat-value { font-size: 24px; font-weight: bold; }
        .temp-color { color: #ff4b4b; }
        .hum-color { color: #00d4ff; }
        .btn { background-color: #22559b; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; margin: 0 5px; font-weight: bold; font-size: 14px; border: 1px solid #444; display: inline-block;}
        .btn:hover { background-color: #337ab7; }
    </style>
</head>
<body>
    <div id="alert-banner" class="alert">
        <h2>¡ALERTA CRÍTICA! Temperatura en almacén superó los 25°C</h2>
    </div>
    <div class="header">
        <h1>Sensor de temperatura y humedad</h1>
        <div style="margin-top: 15px;">
            <a href="/api/static?window=5m" target="_blank" class="btn">5 Minutos</a>
            <a href="/api/static?window=1h" target="_blank" class="btn">1 Hora</a>
            <a href="/api/static?window=24h" target="_blank" class="btn">24 Horas</a>
            <a href="/api/static?window=1w" target="_blank" class="btn">1 Semana</a>
        </div>
    </div>
    <div class="container">
        <div class="sidebar">
            <h2 style="margin-top:0;">Estadísticas (Últimas 24h)</h2>
            <div class="stat-box">
                <h3>Temp Máxima</h3>
                <div class="stat-value temp-color" id="max-t">-- °C</div>
            </div>
            <div class="stat-box">
                <h3>Temp Mínima</h3>
                <div class="stat-value temp-color" id="min-t">-- °C</div>
            </div>
            <div class="stat-box">
                <h3>Humedad Máx</h3>
                <div class="stat-value hum-color" id="max-h">-- %</div>
            </div>
            <div class="stat-box">
                <h3>Humedad Mín</h3>
                <div class="stat-value hum-color" id="min-h">-- %</div>
            </div>
            
            <h3 style="margin-top:20px; color:#ff4b4b; font-size:16px;">⚠️ Alertas (>25°C)</h3>
            <div style="flex-grow:1; overflow-y: auto; background-color: #333; padding: 10px; border-radius: 8px;">
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px;">
                    <thead>
                        <tr style="border-bottom: 1px solid #444;">
                            <th style="padding-bottom: 5px;">Temp</th>
                            <th style="padding-bottom: 5px;">Hora</th>
                        </tr>
                    </thead>
                    <tbody id="alerts-table-body">
                        <!-- Llenado vía JS -->
                    </tbody>
                </table>
            </div>
        </div>
        <div class="content">
            <div id="plot"></div>
        </div>
    </div>
    <script>
        function updatePlot() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    if(!data.timestamp || data.timestamp.length === 0) return;
                    
                    const tempTrace = {
                        x: data.timestamp,
                        y: data.temperatura,
                        name: 'Temperatura (°C)',
                        type: 'scatter',
                        mode: 'lines+markers',
                        line: {color: '#ff4b4b', width: 2},
                        marker: {size: 6}
                    };
                    const humTrace = {
                        x: data.timestamp,
                        y: data.humedad,
                        name: 'Humedad (%)',
                        type: 'scatter',
                        mode: 'lines+markers',
                        line: {color: '#00d4ff', width: 2},
                        marker: {size: 6}
                    };
                    
                    const layout = {
                        title: {text: 'Últimas 24h en Tiempo Real', font:{color:'white'}},
                        plot_bgcolor: '#1e1e1e',
                        paper_bgcolor: '#1e1e1e',
                        font: {color: '#ffffff'},
                        xaxis: {title: 'Hora', gridcolor: '#444444'},
                        yaxis: {title: 'Unidades', gridcolor: '#444444'},
                        margin: {t: 50, b: 50, l: 50, r: 50}
                    };
                    
                    Plotly.react('plot', [tempTrace, humTrace], layout);
                    
                    if (data.stats) {
                        document.getElementById('max-t').innerText = data.stats.max_t.toFixed(2) + ' °C';
                        document.getElementById('min-t').innerText = data.stats.min_t.toFixed(2) + ' °C';
                        document.getElementById('max-h').innerText = data.stats.max_h.toFixed(2) + ' %';
                        document.getElementById('min-h').innerText = data.stats.min_h.toFixed(2) + ' %';
                    }
                    
                    if (data.alerts) {
                        const tbody = document.getElementById('alerts-table-body');
                        tbody.innerHTML = '';
                        data.alerts.forEach(a => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `<td style="color:#ff4b4b; padding: 5px 0;">${parseFloat(a.temp).toFixed(2)} °C</td><td style="color:#aaa; padding: 5px 0; font-size:12px;">${a.time}</td>`;
                            tbody.appendChild(tr);
                        });
                    }
                    
                    const latestTemp = data.temperatura[data.temperatura.length - 1];
                    if (latestTemp > 25.0) {
                        document.getElementById('alert-banner').style.display = 'block';
                    } else {
                        document.getElementById('alert-banner').style.display = 'none';
                    }
                })
                .catch(err => console.error("Error fetch:", err));
        }
        
        updatePlot();
        setInterval(updatePlot, 5000);
    </script>
</body>
</html>
"""

@app.route('/dashboard')
def dashboard():
    """Endpoint para servir el panel HTML con Plotly JS embebido."""
    return render_template_string(HTML_TEMPLATE)

def format_data_for_js(lecturas):
    """Convierte el array de dicts de SQLite a dict de arrays (formato JS)."""
    if not lecturas:
        return {"timestamp": [], "temperatura": [], "humedad": []}
    return {
        "timestamp": [f"{row['fecha']} {row['hora']}" for row in lecturas],
        "temperatura": [row['temperatura'] for row in lecturas],
        "humedad": [row['humedad'] for row in lecturas]
    }

def get_stats(lecturas):
    """Calcula stats máximos/mínimos al vuelo."""
    if not lecturas:
        return {"max_t": 0, "min_t": 0, "max_h": 0, "min_h": 0}
    
    temps = [row['temperatura'] for row in lecturas]
    hums = [row['humedad'] for row in lecturas]
    return {
        "max_t": max(temps),
        "min_t": min(temps),
        "max_h": max(hums),
        "min_h": min(hums)
    }

@app.route('/api/data')
def get_historical_data():
    """API de lectura para que el JS cliente obtenga las series del histórico."""
    db = get_db()
    # Obtenemos las últimas 24h
    lecturas = db.obtener_lecturas_por_intervalo(24 * 60)
    data = format_data_for_js(lecturas)
    data["stats"] = get_stats(lecturas)
    
    # Obtenemos las alertas y adaptamos el formato a JS 
    alerts = db.obtener_alarmas()
    data["alerts"] = [{"temp": a['valor_alarma'], "time": f"{a['fecha']} {a['hora']}"} for a in alerts]
    
    return jsonify(data)

@app.route('/api/static')
def static_view():
    db = get_db()
    window = request.args.get('window', '1h')
    names = {'5m': 'Últimos 5 Minutos', '1h': 'Última 1 Hora', '24h': 'Últimas 24 Horas', '1w': 'Última Semana'}
    title = names.get(window, 'Vista Estática')
    
    window_to_mins = {'5m': 5, '1h': 60, '24h': 1440, '1w': 10080}
    mins = window_to_mins.get(window, 60)
    
    lecturas = db.obtener_lecturas_por_intervalo(mins)
    data = format_data_for_js(lecturas)
    
    STATIC_HTML = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Vista Estática - {{title}}</title>
        <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
        <style>
            body { background-color: #1e1e1e; color: white; font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 20px; text-align: center; }
            #plot { width: 90%; height: 80vh; margin: 0 auto; }
        </style>
    </head>
    <body>
        <h2>Reporte Estático Interactivo: {{title}}</h2>
        <div id="plot"></div>
        <script>
            const data = JSON_DATA_HERE;
            if (data.timestamp && data.timestamp.length > 0) {
                const tempTrace = { x: data.timestamp, y: data.temperatura, name: 'Temp (°C)', type: 'scatter', mode: 'lines+markers', line: {color: '#ff4b4b'} };
                const humTrace = { x: data.timestamp, y: data.humedad, name: 'Hum (%)', type: 'scatter', mode: 'lines+markers', line: {color: '#00d4ff'} };
                const layout = {
                    title: {text: 'Grafico - {{title}}', font:{color:'white'}},
                    plot_bgcolor: '#1e1e1e', paper_bgcolor: '#1e1e1e', font: {color: '#ffffff'},
                    xaxis: {gridcolor: '#444444'}, yaxis: {gridcolor: '#444444'},
                };
                Plotly.newPlot('plot', [tempTrace, humTrace], layout);
            } else {
                document.getElementById('plot').innerHTML = '<p>No hay datos almacenados en este periodo de tiempo.</p>';
            }
        </script>
    </body>
    </html>
    """
    return STATIC_HTML.replace("{{title}}", title).replace("JSON_DATA_HERE", json.dumps(data))

def run_server():
    print("Iniciando servidor API Ingest (Web Dashboard)...")
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_server()
