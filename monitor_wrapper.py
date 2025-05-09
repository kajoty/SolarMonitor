import subprocess
import time
import datetime
from pysolar.solar import get_altitude
from influxdb import InfluxDBClient

# Standort
LAT = 53.6987
LON = 10.7656

# InfluxDB-Zugang
INFLUX_HOST = "192.168.178.100"
INFLUX_PORT = 8086
INFLUX_DB = "influx"
INFLUX_USER = "admin"
INFLUX_PASS = "admin"

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
