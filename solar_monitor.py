import SoapySDR
from SoapySDR import *
import numpy as np
import time
from influxdb import InfluxDBClient

INFLUX_HOST = "192.168.178.100"
INFLUX_PORT = 8086
INFLUX_DB = "influx"
INFLUX_USER = "admin"
INFLUX_PASS = "admin"

FREQUENCIES_HZ = [7050000, 10136000, 14074000, 18100000, 29800000]
SAMPLE_RATE = 2e6
DURATION_SEC = 1.5

def open_hackrf():
    devices = SoapySDR.Device.enumerate()
    for dev in devices:
        if "driver" in dev and dev["driver"] == "hackrf":
            return SoapySDR.Device(dev)
    raise RuntimeError("Kein HackRF gefunden.")

def connect_influx():
    return InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PASS, INFLUX_DB)

def measure_power(sdr, freq):
    sdr.setSampleRate(SOAPY_SDR_RX, 0, SAMPLE_RATE)
    sdr.setFrequency(SOAPY_SDR_RX, 0, freq)
    sdr.setGainMode(SOAPY_SDR_RX, 0, True)

    stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
    sdr.activateStream(stream)

    buffs = np.empty(4096, np.complex64)
    samples = []
    start = time.time()
    while time.time() - start < DURATION_SEC:
        sr = sdr.readStream(stream, [buffs], len(buffs))
        if sr.ret > 0:
            samples.extend(buffs[:sr.ret])

    sdr.deactivateStream(stream)
    sdr.closeStream(stream)

    if samples:
        return 10 * np.log10(np.mean(np.abs(samples)**2) + 1e-12)
    return None

def run_once():
    sdr = open_hackrf()
    influx = connect_influx()
    print(f"[*] Einmalige Messung auf {len(FREQUENCIES_HZ)} Frequenzen...")

    for freq in FREQUENCIES_HZ:
        power = measure_power(sdr, freq)
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        freq_mhz = freq / 1e6
        if power is not None:
            print(f"[{now}] {freq_mhz:.3f} MHz: {power:.2f} dBfs")
            point = [{
                "measurement": "solar_monitor",
                "tags": {
                    "band": "HF",
                    "frequency_mhz": f"{freq_mhz:.3f}",
                    "source": "hackrf",
                    "antenna": "ml30"
                },
                "fields": {
                    "power_dbfs": power
                },
                "time": int(time.time() * 1e9)
            }]
            influx.write_points(point)
        else:
            print(f"[{now}] ⚠️ Keine Daten bei {freq_mhz:.3f} MHz")

if __name__ == "__main__":
    run_once()
