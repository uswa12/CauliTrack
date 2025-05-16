import threading
import time
import datetime
import math
import random
import logging
from concurrent.futures import ThreadPoolExecutor

from app import socketio
from app.db import insert_sensor_data
from app.edge_processors import compute_freshness

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SimulationManager:
    def __init__(self):
        self.active_phases = set()
        self.patches = range(1, 101)
        self.lock = threading.Lock()
        self.thread = None

    def start_phase(self, phase):
        with self.lock:
            self.active_phases.add(phase)
            if self.thread is None:
                self.thread = threading.Thread(target=self._run_simulation, daemon=True)
                self.thread.start()
                logger.info(f"[SIMULATION] Started thread for phase(s): {self.active_phases}")

    def stop_phase(self, phase):
        with self.lock:
            self.active_phases.discard(phase)
            logger.info(f"[SIMULATION] Stopped phase: {phase}")
            if not self.active_phases and self.thread is not None:
                self.thread = None
                logger.info("[SIMULATION] All phases stopped. Simulation paused.")

    def _run_simulation(self):
        while True:
            time.sleep(1)
            with self.lock:
                if not self.active_phases:
                    continue
                phases = list(self.active_phases)

            timestamp = datetime.datetime.now()
            batch = []
            payloads = []

            def process_patch(phase, pid):
                try:
                    data = self._simulate_phase(phase, timestamp, pid)
                    freshness = compute_freshness(phase, data)

                    db_row = (
                        timestamp, pid, phase,
                        data['temperature'], data['humidity'], data['sunlight'],
                        data['soil_moisture'], data['airflow'], data['vibration'],
                        freshness
                    )

                    payload = {
                        'patch_id': pid,
                        'phase': phase,
                        'time': timestamp.isoformat(),
                        'temperature': data.get('temperature'),
                        'humidity': data.get('humidity'),
                        'soil_moisture': data.get('soil_moisture'),
                        'sunlight': data.get('sunlight'),
                        'airflow': data.get('airflow'),
                        'vibration': data.get('vibration'),
                        'freshness': freshness
                    }

                    logger.debug(f"[SIM] Patch {pid:03} {phase}: F={freshness:.2f}")
                    return db_row, payload

                except Exception as e:
                    logger.error(f"[SIMULATION ERROR] Patch {pid}, Phase {phase} - {e}")
                    return None, None

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for phase in phases:
                    for pid in self.patches:
                        futures.append(executor.submit(process_patch, phase, pid))

                for future in futures:
                    db_row, payload = future.result()
                    if db_row and payload:
                        batch.append(db_row)
                        payloads.append(payload)

            for payload in payloads:
                socketio.emit('sensor_update', payload)

            if batch:
                logger.info(f"[SIMULATION] Inserting {len(batch)} records to TimescaleDB")
                insert_sensor_data(batch)

    def _simulate_phase(self, phase, ts, patch_id):
        """Simulate realistic sensor values with per-patch variability."""
        hour = ts.hour + ts.minute / 60
        local_rand = random.Random(hash((ts.replace(microsecond=0), patch_id, phase)))

        if phase == 'farm':
            temp = 20 + 5 * math.sin((hour - 14) * math.pi / 12) + local_rand.uniform(-1, 1)
            humidity = 85 + 5 * math.sin((hour - 6) * math.pi / 12) + local_rand.uniform(-2, 2)
            sunlight = max(0, 800 * math.sin((hour - 6) * math.pi / 12)) + local_rand.uniform(-50, 50)
            soil = 70 + 5 * math.sin((hour - 12) * math.pi / 12) + local_rand.uniform(-3, 3)
            airflow = 0.3 + local_rand.uniform(-0.1, 0.1)
            vibration = 0.0


        elif phase == 'depot':
            temp = 0 + local_rand.uniform(-0.5, 0.5)
            humidity = 96 + local_rand.uniform(-1, 1)
            sunlight = None
            soil = None
            airflow = 5 + local_rand.uniform(-0.5, 0.5)
            vibration = 0.0


        elif phase == 'transport':
            temp = 0 + local_rand.uniform(-1, 1)
            humidity = 96 + local_rand.uniform(-2, 2)
            sunlight = None
            soil = None
            airflow = 5 + local_rand.uniform(-0.5, 0.5)
            vibration = local_rand.uniform(0, 1) + (local_rand.random() < 0.05) * local_rand.uniform(1, 3)


        elif phase == 'market':
            temp = 22 + 3 * math.sin((hour - 12) * math.pi / 12) + local_rand.uniform(-1, 1)
            humidity = 88 + 5 * math.sin((hour - 12) * math.pi / 12) + local_rand.uniform(-3, 3)
            sunlight = max(0, 500 * math.sin((hour - 8) * math.pi / 12)) + local_rand.uniform(-20, 20)
            soil = None
            airflow = 0.5 + local_rand.uniform(-0.1, 0.1)
            vibration = 0.0

        else:
            temp = humidity = sunlight = soil = airflow = vibration = None

        return {
            'temperature': round(temp, 2) if temp is not None else None,
            'humidity': round(humidity, 2) if humidity is not None else None,
            'sunlight': round(sunlight, 2) if sunlight is not None else None,
            'soil_moisture': round(soil, 2) if soil is not None else None,
            'airflow': round(airflow, 2) if airflow is not None else None,
            'vibration': round(vibration, 2) if vibration is not None else None
        }

# Create the singleton manager
sim_manager = SimulationManager()