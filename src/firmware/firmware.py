"""Main loop for the Light‑Pollution Monitor.

The code does not rely on any external libraries beyond MicroPython.
It:
1. Loads configuration JSON from the Pico (name, latitude, longitude).
2. Reads the light sensor every 15 min.
3. Builds a JSON payload.
4. Sends it via the LoRa helper.
"""

import time
from machine import ADC, Pin, SPI
import ujson
from lorawan import LoRa

CONFIG_PATH = "config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return ujson.load(f)
    except OSError:
        return {"name": "unknown", "lat": 0.0, "lon": 0.0}

cfg = load_config()

adc = ADC(Pin(2))  # TEMT6000 on GP2
spi = SPI(0, baudrate=5_000_000, sck=Pin(13), mosi=Pin(15), miso=Pin(14))
lora = LoRa(spi, cs=18, rst=10, dio0=18)

# Default measurement interval in seconds (15 minutes). Can be overridden
# by the config JSON key ``poll_interval``.
TIME_BETWEEN_READING = cfg.get("poll_interval", 900)

def read_lux():
    raw = adc.read_u16()
    lux = raw * (3.3 / 65535) * 1000  # simple linear mapping
    return int(lux)

while True:
    lux_val = read_lux()
    payload = {
        "name": cfg["name"],
        "lat": cfg["lat"],
        "lon": cfg["lon"],
        "lux": lux_val,
        "ts": int(time.time()),
    }
    lora.send(ujson.dumps(payload).encode())
    time.sleep(TIME_BETWEEN_READING)
