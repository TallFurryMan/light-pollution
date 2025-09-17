"""Light‑pollution monitor firmware.

This version supports three light‑sensors:
* TEMT6000 – inexpensive ambient light sensor, connected to ADC pin GP2.
* TSL2591 – high‑sensitivity I²C sensor.
* BH1750 – widely used digital lux meter.

The sensor type is chosen via the ``sensor_type`` key in ``config.json``.
If not present, the system defaults to the TSL2591 because of its
low‑light sensitivity.

The firmware reads the sensor, packages the data with latitude/longitude
and sensor name into a JSON payload and pushes it over LoRa using the
``lorawan.LoRa`` helper.
"""

import time
from machine import ADC, Pin, SPI, I2C
import ujson
from lorawan import LoRa

CONFIG_PATH = "config.json"

def load_config():
    """Return config dictionary from ``config.json``.

    If the file cannot be read, a minimal default config is returned.
    """
    try:
        with open(CONFIG_PATH, "r") as f:
            return ujson.load(f)
    except OSError:
        return {"name": "unknown", "lat": 0.0, "lon": 0.0}

cfg = load_config()

class TSL2591:
    ADDRESS = 0x29
    REG_CONTROL = 0x80
    REG_TIMING = 0x81
    REG_DATA0LOW = 0x86

    def __init__(self, i2c: I2C):
        self.i2c = i2c
        self.i2c.writeto_mem(self.ADDRESS, self.REG_CONTROL, bytes([0x01]))
        self.i2c.writeto_mem(self.ADDRESS, self.REG_TIMING, bytes([0x02]))

    def read_lux(self) -> float:
        data = self.i2c.readfrom_mem(self.ADDRESS, self.REG_DATA0LOW, 2)
        count = int.from_bytes(data, "little")
        return count * 0.064


class BH1750:
    ADDRESS = 0x23

    def __init__(self, i2c: I2C):
        self.i2c = i2c
        self.i2c.writeto(self.ADDRESS, bytes([0x10]))

    def read_lux(self) -> float:
        time.sleep_ms(180)
        data = self.i2c.readfrom(self.ADDRESS, 2)
        count = int.from_bytes(data, "big")
        return count / 1.2


class TEMT6000:
    def __init__(self, pin_no: int = 2):
        self.adc = ADC(Pin(pin_no))

    def read_lux(self) -> int:
        raw = self.adc.read_u16()
        lux = raw * (3.3 / 65535) * 1000
        return int(lux)


sensor_type = cfg.get("sensor_type", "TSL2591")

if sensor_type in ("TSL2591", "BH1750"):
    i2c = I2C(0, scl=Pin(5), sda=Pin(4))
    if sensor_type == "TSL2591":
        sensor = TSL2591(i2c)
    else:
        sensor = BH1750(i2c)
else:
    sensor = TEMT6000()

spi = SPI(0, baudrate=5_000_000, sck=Pin(13), mosi=Pin(15), miso=Pin(14))
lora = LoRa(spi, cs=18, rst=10, dio0=18)

TIME_BETWEEN_READING = cfg.get("poll_interval", 900)

while True:
    lux_val = sensor.read_lux()
    payload = {
        "name": cfg["name"],
        "lat": cfg["lat"],
        "lon": cfg["lon"],
        "lux": lux_val,
        "ts": int(time.time()),
    }
    lora.send(ujson.dumps(payload).encode())
    time.sleep(TIME_BETWEEN_READING)

