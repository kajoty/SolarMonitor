# monitor_wrapper.py
import subprocess
import time
import datetime
import os
from dotenv import load_dotenv
from pysolar.solar import get_altitude
from influxdb import InfluxDBClient

load_dotenv()

LAT = 53.6987
LON = 10.7656

INFLUX_HOST = os.getenv("INFLUX_HOST")
INFLUX_PORT = int(os.getenv("INFLUX_PORT"))
INFLUX_DB = os.getenv("INFLUX_DB")
INFLUX_USER = os.getenv("INFLUX_USER")
INFLUX_PASS = os.getenv("INFLUX_PASS")

def log_solar_altitude():
    now = datetime.datetime.now(datetime.timezone.utc)
    altitude = get_altitude(LAT, LON, now)

    client = InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PASS, INFLUX_DB)
    json_body = [{
        "measurement": "sun_monitor",
        "fields": {
            "solar_altitude_deg": float(altitude)
        },
        "time": now.isoformat()
    }]
    client.write_points(json_body)
    print(f"[✓] Sonnenhöhe geloggt: {altitude:.2f}°")

def run_hf_scan():
    print("[*] Starte HF-Messung via solar_monitor.py ...")
    subprocess.run([
        "/home/user/Projekte/hackrfscanner/.venv/bin/python3",
        "/home/user/Projekte/hackrfscanner/solar_monitor.py"
    ])

if __name__ == "__main__":
    log_solar_altitude()
    run_hf_scan()
