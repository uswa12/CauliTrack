#edge_processors.py working version
# backend/app/edge_processors.py
def freshness_farm(temperature, humidity, soil_moisture, sunlight, airflow, vibration):
    score = 100
    score -= abs(temperature - 21.5) * 1.5  # Optimal midpoint temperature
    score -= abs(humidity - 90) * 0.5
    score -= abs(soil_moisture - 75) * 0.3
    if sunlight < 200 or sunlight > 800:
        score -= abs(sunlight - 500) / 100
    return max(0, min(100, score))


def freshness_depot(temperature, humidity, soil_moisture, sunlight, airflow, vibration):
    score = 100
    score -= abs(temperature - 0.5) * 2.0
    score -= abs(humidity - 96.5) * 0.5
    score -= abs(airflow - 5) * 1.0
    return max(0, min(100, score))

def freshness_transport(temperature, humidity, soil_moisture, sunlight, airflow, vibration):
    score = 100
    score -= abs(temperature - 2.5) * 1.5
    score -= abs(humidity - 90) * 0.3
    score -= vibration * 2.0
    return max(0, min(100, score))

def freshness_market(temperature, humidity, soil_moisture, sunlight, airflow, vibration):
    score = 100
    score -= abs(temperature - 4.0) * 1.0
    score -= abs(humidity - 92.5) * 0.4
    if sunlight > 200:
        score -= (sunlight - 200) / 200
    return max(0, min(100, score))


def compute_freshness(phase, data):
    """
    Dispatcher: choose the right formula based on phase string.
    data is a dict with keys: temperature, humidity, soil_moisture,
                                  sunlight, airflow, vibration.
    """
    if phase == 'farm':
        return freshness_farm(**data)
    if phase == 'depot':
        return freshness_depot(**data)
    if phase == 'transport':
        return freshness_transport(**data)
    if phase == 'market':
        return freshness_market(**data)
    return 0