#space_weather_logger.py
import requests
from influxdb import InfluxDBClient

# InfluxDB-Zugangsdaten
INFLUX_HOST = "192.168.178.100"
INFLUX_PORT = 8086
INFLUX_DB = "influx"
INFLUX_USER = "admin"
INFLUX_PASS = "admin"

# NOAA API-Quellen
K_INDEX_URL = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
F107_FLUX_URL = "https://services.swpc.noaa.gov/json/f107_cm_flux.json"

def fetch_latest_k_index():
    response = requests.get(K_INDEX_URL, timeout=10)
    response.raise_for_status()
    return response.json()[-1]  # Letzter (aktuellster) Datensatz

def fetch_latest_flux():
    response = requests.get(F107_FLUX_URL, timeout=10)
    response.raise_for_status()
    return response.json()[0]  # Erster Eintrag = aktuellster

def write_to_influx(kp_value, f107_value, timestamp):
    client = InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PASS, INFLUX_DB)
    data_point = [{
        "measurement": "space_weather",
        "time": timestamp,
        "fields": {
            "kp_index": kp_value,
            "f10_7_flux": f107_value
        }
    }]
    client.write_points(data_point)

def main():
    try:
        # Daten abrufen
        kp_data = fetch_latest_k_index()
        flux_data = fetch_latest_flux()

        # Werte extrahieren
        kp_value = float(kp_data["kp_index"])
        kp_time = kp_data["time_tag"]

        f107_value = float(flux_data["flux"])
        f107_time = flux_data["time_tag"]

        # Den aktuelleren Zeitstempel verwenden
        timestamp = max(kp_time, f107_time)

        # In InfluxDB schreiben
        write_to_influx(kp_value, f107_value, timestamp)

        print(f"[✓] Kp={kp_value}, F10.7={f107_value} @ {timestamp}")

    except Exception as e:
        print(f"[!] Fehler: {e}")

if __name__ == "__main__":
    main()
