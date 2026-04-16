# TempHrAlmacén
Registro y control de temperatura y humedad relativa de un almacén

## 🚀 Características

- **Dashboard en Tiempo Real**: Visualización de temperatura y humedad con gráficos interactivos.
- **Alertas Automáticas**: Notificaciones cuando los niveles exceden los umbrales seguros.
- **Persistencia de Datos**: Almacenamiento seguro en base de datos SQLite.
- **Simulador Integrado**: Herramienta para simular lecturas de sensores y probar el sistema.

## 🛠️ Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd TempHrAlmacen
   ```

2. **Crear y activar entorno virtual**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Ejecución

### Opción 1: Modo Desarrollo (Recomendado)
Ejecuta el backend y el frontend en terminales separadas.

**Terminal 1: Backend**
```bash
python app/api.py
```

**Terminal 2: Frontend**
```bash
python app/frontend.py
```

Accede al dashboard en: [http://localhost:5000](http://localhost:5000)

### Opción 2: Modo Producción
```bash
python app/api.py
```

## 🧪 Simulación

Para probar el sistema sin hardware real, ejecuta el simulador:

```bash
python simulator.py
```

El simulador enviará datos cada 10 segundos y generará picos de temperatura aleatorios para probar las alertas.

## 📂 Estructura del Proyecto

```
TempHrAlmacen/
├── app/
│   ├── api.py       # Servidor API y lógica de negocio
│   ├── frontend.py         # Interfaz de usuario (Streamlit)
│   ├── database.py         # Gestión de base de datos
│   └── models.py           # Modelos de datos
├── simulator.py            # Simulador de sensores
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación
```
