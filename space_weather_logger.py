# space_weather_logger.py
import requests
import os
from dotenv import load_dotenv
from influxdb import InfluxDBClient

# .env laden
load_dotenv()

# InfluxDB-Zugangsdaten aus Umgebungsvariablen
INFLUX_HOST = os.getenv("INFLUX_HOST")
INFLUX_PORT = int(os.getenv("INFLUX_PORT"))
INFLUX_DB = os.getenv("INFLUX_DB")
INFLUX_USER = os.getenv("INFLUX_USER")
INFLUX_PASS = os.getenv("INFLUX_PASS")

K_INDEX_URL = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
F107_FLUX_URL = "https://services.swpc.noaa.gov/json/f107_cm_flux.json"

def fetch_latest_k_index():
    response = requests.get(K_INDEX_URL, timeout=10)
    response.raise_for_status()
    return response.json()[-1]

def fetch_latest_flux():
    response = requests.get(F107_FLUX_URL, timeout=10)
    response.raise_for_status()
    return response.json()[0]

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
        kp_data = fetch_latest_k_index()
        flux_data = fetch_latest_flux()

        kp_value = float(kp_data["kp_index"])
        kp_time = kp_data["time_tag"]

        f107_value = float(flux_data["flux"])
        f107_time = flux_data["time_tag"]

        timestamp = max(kp_time, f107_time)

        write_to_influx(kp_value, f107_value, timestamp)

        print(f"[✓] Kp={kp_value}, F10.7={f107_value} @ {timestamp}")

    except Exception as e:
        print(f"[!] Fehler: {e}")

if __name__ == "__main__":
    main()
