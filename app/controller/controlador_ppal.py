"""
controlador_ppal.py - Controlador principal (MVC).

Gestiona la lógica de negocio conectando el Modelo y la Vista.
Controla el ciclo de monitoreo, alertas y generación de gráficos.
"""

import threading
import queue
from app.models.almacen import Almacen
from app.repositories.configdb import ConfigDB
from app.services.plotly_service import PlotlyService


class ControladorPrincipal:
    """Controlador principal del sistema de monitorización."""

    # Mapeo de botones de intervalo → minutos
    INTERVALOS = {
        "5 Minutos": 5,
        "60 Minutos": 60,
        "2 Horas": 120,
        "7 Días": 10080,
    }

    INTERVALO_ACTUALIZACION_MS = 30_000  # 30 segundos

    def __init__(self, vista):
        self.vista = vista
        self.db = ConfigDB()
        self.plotly_service = PlotlyService()
        self._monitoreo_activo = False
        self._cola = queue.Queue()
        self._job_id = None  # ID del .after() activo

    # ------------------------------------------------------------------ #
    #  Ciclo de monitoreo
    # ------------------------------------------------------------------ #
    def iniciar_monitoreo(self):
        """Inicia el ciclo de captura de datos cada 30 segundos."""
        if self._monitoreo_activo:
            return
        self._monitoreo_activo = True
        self.vista.actualizar_estado_monitoreo(True)
        self._ciclo_lectura()

    def detener_monitoreo(self):
        """Detiene el ciclo de captura."""
        self._monitoreo_activo = False
        self.vista.actualizar_estado_monitoreo(False)
        if self._job_id is not None:
            self.vista.root.after_cancel(self._job_id)
            self._job_id = None

    # ------------------------------------------------------------------ #
    #  Captura de datos (hilo secundario)
    # ------------------------------------------------------------------ #
    def _ciclo_lectura(self):
        """
        Gestiona el ciclo continuo de captura de datos y actualización de la interfaz.

        Este método implementa un bucle lógico mediante la programación de tareas 
        en el event loop de la GUI. Realiza tres acciones clave:
        1. Lanza la captura de sensores en un hilo independiente para mantener la 
           fluidez de la interfaz.
        2. Programa la revisión de la cola de datos para procesar lo capturado.
        3. Se auto-programa para ejecutarse nuevamente tras el intervalo definido.

        Returns:
            None: El ciclo se controla mediante el estado de 'self._monitoreo_activo'.

        Note:
            Utiliza 'self.vista.root.after' para la recursividad, lo que evita el 
            desbordamiento de pila (stack overflow) y permite que la aplicación 
            siga respondiendo a eventos del usuario.
        """
        #Ejecuta una lectura y programa la siguiente.
        if not self._monitoreo_activo:
            return

        # Lanzar captura en hilo secundario para no bloquear la GUI
        hilo = threading.Thread(target=self._capturar_en_hilo, daemon=True)
        hilo.start()

        # Procesar resultados de la cola
        self.vista.root.after(200, self._procesar_cola)

        # Programar siguiente ciclo
        self._job_id = self.vista.root.after(
            self.INTERVALO_ACTUALIZACION_MS, self._ciclo_lectura
        )

    def _capturar_en_hilo(self):
        """
        Ejecuta la captura de datos y su persistencia de forma asíncrona.

        Este método está diseñado para ejecutarse en un hilo secundario. Realiza
        la generación de datos (simulados), los registra en la base de datos 
        SQLite y coloca el objeto resultante en una cola sincronizada para que 
        el hilo principal pueda actualizar la interfaz gráfica.

        Returns:
            None: Los resultados se envían al hilo principal a través de 'self._cola'.

        Note:
            El flujo incluye la actualización del objeto 'lectura' con el ID único 
            generado por la base de datos ('_db_id'), facilitando la trazabilidad 
            o futuras consultas de alarmas específicas.
        """
        lectura = Almacen.generar_lectura_simulada()
        lectura_id = self.db.insertar_lectura(
            lectura.temperatura,
            lectura.humedad,
            lectura.fecha,
            lectura.hora,
            lectura.id_almacen,
        )
        # Guardar el id de la lectura para posible uso en alarmas
        lectura._db_id = lectura_id
        self._cola.put(lectura)

    def _procesar_cola(self):
        """Procesa los resultados pendientes de la cola (hilo principal)."""
        try:
            while True:
                lectura = self._cola.get_nowait()
                self._actualizar_vista(lectura)
        except queue.Empty:
            pass

    # ------------------------------------------------------------------ #
    #  Actualización de la vista
    # ------------------------------------------------------------------ #
    def _actualizar_vista(self, lectura):
        """
        Refresca todos los componentes de la interfaz con los datos más recientes.

        Coordina la actualización de los indicadores numéricos, la tabla de 
        historial y el gráfico de tendencias. Además, dispara el motor de 
        verificación de alertas para la lectura actual.

        Args:
            lectura (Lectura): Objeto que contiene los datos de la última captura 
                (temperatura, humedad, etc.) para los indicadores y alertas.

        Returns:
            None: Actualiza directamente los widgets a través de 'self.vista'.

        Note:
            Para mantener la coherencia del historial, el método realiza una 
            consulta a la base de datos de las últimas 60 lecturas antes de 
            redibujar la tabla y el gráfico de la interfaz.
        """
        # Actualizar indicadores
        self.vista.actualizar_indicador_temperatura(lectura.temperatura)
        self.vista.actualizar_indicador_humedad(lectura.humedad)

        # Actualizar tabla de historial y gráfico en tiempo real
        ultimas = self.db.obtener_ultimas_lecturas(60)
        self.vista.actualizar_tabla(ultimas)
        self.vista.actualizar_grafico(ultimas)

        # Verificar alertas
        self._verificar_alertas(lectura)

    def _verificar_alertas(self, lectura):
        """
        Evalúa si los valores de la lectura superan los límites de seguridad.

        Si se detecta una anomalía térmica, el método realiza una doble acción:
        registra el evento en la base de datos para auditoría histórica y activa 
        el modo visual de alerta en la interfaz. Si la lectura es normal, 
        restablece la apariencia estándar de la vista.

        Args:
            lectura (Lectura): Objeto con los datos capturados. Se espera que 
                tenga evaluado el atributo 'alerta_temperatura' y contenga 
                el '_db_id' para la vinculación en base de datos.

        Returns:
            None: Modifica el estado de la base de datos y la apariencia de la UI.

        Note:
            La vinculación con la tabla de alarmas depende de que la lectura 
            tenga un '_db_id' válido. Si este atributo no existe, la alarma 
            se mostrará visualmente pero no se guardará en el historial.
        """
        if lectura.alerta_temperatura:
            # Registrar la alarma en la base de datos
            lectura_id = getattr(lectura, '_db_id', None)
            if lectura_id is not None:
                self.db.insertar_alarma(
                    fecha=lectura.fecha,
                    hora=lectura.hora,
                    valor_alarma=lectura.temperatura,
                    almacen=lectura.id_almacen,
                )
            self.vista.mostrar_alerta(lectura.temperatura)
        else:
            self.vista.restaurar_estado_normal()

    # ------------------------------------------------------------------ #
    #  Gráficos por intervalo
    # ------------------------------------------------------------------ #
    def mostrar_grafico_intervalo(self, etiqueta):
        """
        Inicia el proceso de consulta y visualización de datos en un hilo secundario.

        Busca el valor en minutos asociado a la etiqueta, recupera los datos de la 
        base de datos y solicita la generación del gráfico. Si no se encuentran 
        datos, envía una notificación a la vista.

        Args:
            etiqueta (str): Nombre del intervalo seleccionado (ej. "5 Minutos", "1 Hora").
                Debe existir como clave en el diccionario 'self.INTERVALOS'.

        Returns:
            None: La ejecución real ocurre de forma asíncrona en un hilo 'daemon'.

        Note:
            Utiliza 'threading.Thread' para evitar que la consulta a la base de datos 
            congele la interfaz gráfica (UI). Las interacciones con la vista se 
            realizan mediante 'root.after' para garantizar la seguridad entre hilos.
        """
        minutos = self.INTERVALOS.get(etiqueta)
        if minutos is None:
            return

        def _generar():
            lecturas = self.db.obtener_lecturas_por_intervalo(minutos)
            if lecturas:
                self.plotly_service.generar_grafico_intervalo(lecturas, etiqueta)
            else:
                # Notificar en el hilo principal que no hay datos
                self.vista.root.after(0, lambda: self.vista.mostrar_info_sin_datos(etiqueta))

        hilo = threading.Thread(target=_generar, daemon=True)
        hilo.start()

    def mostrar_grafico_general(self):
        """
        Recupera el histórico completo de la base de datos y genera el gráfico interactivo.

        Crea un hilo secundario para consultar la totalidad de los registros sin 
        bloquear la interfaz de usuario. Si existen datos, invoca al servicio de 
        Plotly para renderizar y abrir el archivo HTML resultante.

        Returns:
            None: La ejecución es asíncrona y delega la apertura del navegador al 
                'plotly_service'.

        Note:
            Al solicitar todas las lecturas disponibles, el tiempo de procesamiento 
            y renderizado puede ser mayor que en los gráficos por intervalo, por 
            lo que el uso del hilo 'daemon' es crítico para la experiencia del usuario.
        """
        def _generar():
            lecturas = self.db.obtener_lecturas()
            if lecturas:
                self.plotly_service.generar_grafico_combinado(lecturas)

        hilo = threading.Thread(target=_generar, daemon=True)
        hilo.start()
