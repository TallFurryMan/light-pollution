"""Light‑pollution monitor firmware."""

import time

try:
    import ujson  # MicroPython
except ImportError:  # CPython fallback for tests
    import json as ujson  # type: ignore

try:
    from machine import ADC, Pin, SPI, I2C
except ImportError:  # Allows importing in CPython tests
    ADC = Pin = SPI = I2C = None  # type: ignore

from lorawan import LoRa

CONFIG_PATH = "config.json"
DEFAULT_CONFIG = {
    "name": "unknown",
    "lat": 0.0,
    "lon": 0.0,
    "sensor_type": "TSL2591",
    "charger_type": "none",
    "poll_interval": 900,
    "lora_chip": "RFM95",
    "lora_cs": 18,
    "lora_rst": 10,
    "lora_dio0": 18,
    "lora_busy": 16,
    "lora_dio1": 17,
}

_sleep_ms = getattr(time, "sleep_ms", lambda ms: time.sleep(ms / 1000))


def load_config(path: str = CONFIG_PATH):
    """Return config dictionary from ``config.json`` or defaults."""
    try:
        with open(path, "r") as f:
            cfg = ujson.load(f)
    except (OSError, ValueError):
        cfg = {}
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg)
    return merged


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
        _sleep_ms(180)
        data = self.i2c.readfrom(self.ADDRESS, 2)
        count = int.from_bytes(data, "big")
        return count / 1.2


class TEMT6000:
    def __init__(self, pin_no: int = 2, adc_cls=ADC, pin_cls=Pin):
        if adc_cls is None or pin_cls is None:
            raise RuntimeError("TEMT6000 requires machine.ADC and machine.Pin")
        self.adc = adc_cls(pin_cls(pin_no))

    def read_lux(self) -> int:
        raw = self.adc.read_u16()
        lux = raw * (3.3 / 65535) * 1000
        return int(lux)


class BaseCharger:
    def status(self):
        return "unknown"


class MCP73871(BaseCharger):
    ADDRESS = 0x2C

    def __init__(self, i2c: I2C):
        self.i2c = i2c

    def status(self):
        try:
            data = self.i2c.readfrom_mem(self.ADDRESS, 0x02, 1)
            mapping = {
                0x00: "Charging",
                0x02: "Full",
                0x04: "Fault",
            }
            return mapping.get(data[0], "unknown")
        except Exception:
            return "error"


class TP4056(BaseCharger):
    def status(self):
        return "charging"


def make_sensor(cfg, i2c_cls=I2C, adc_cls=ADC, pin_cls=Pin):
    sensor_type = cfg.get("sensor_type", DEFAULT_CONFIG["sensor_type"])
    if sensor_type in ("TSL2591", "BH1750"):
        if i2c_cls is None or pin_cls is None:
            raise RuntimeError("I2C sensor requested but machine.I2C is missing")
        sensor_i2c = i2c_cls(0, scl=pin_cls(5), sda=pin_cls(4))
        if sensor_type == "TSL2591":
            return TSL2591(sensor_i2c)
        return BH1750(sensor_i2c)
    return TEMT6000(adc_cls=adc_cls, pin_cls=pin_cls)


def make_charger(cfg, i2c_cls=I2C):
    charger_type = cfg.get("charger_type", DEFAULT_CONFIG["charger_type"])
    if charger_type == "MCP73871":
        if i2c_cls is None:
            raise RuntimeError("MCP73871 requires machine.I2C")
        return MCP73871(i2c_cls(1))
    if charger_type == "TP4056":
        return TP4056()
    return BaseCharger()


def make_lora(cfg, spi=None, pin_cls=Pin, lora_cls=LoRa):
    if pin_cls is None or (spi is None and SPI is None):
        raise RuntimeError("LoRa requires machine.SPI and machine.Pin")
    spi = spi or SPI(0, baudrate=5_000_000, sck=pin_cls(13), mosi=pin_cls(15), miso=pin_cls(14))
    lora_chip = cfg.get("lora_chip", DEFAULT_CONFIG["lora_chip"])
    cs = cfg.get("lora_cs", DEFAULT_CONFIG["lora_cs"])
    rst = cfg.get("lora_rst", DEFAULT_CONFIG["lora_rst"])
    dio0 = cfg.get("lora_dio0", DEFAULT_CONFIG["lora_dio0"])
    if lora_chip.upper() == "SX1262":
        from lorawan import SX1262LoRa  # late import to avoid optional dep when not used
        busy = cfg.get("lora_busy", DEFAULT_CONFIG["lora_busy"])
        dio1 = cfg.get("lora_dio1", DEFAULT_CONFIG["lora_dio1"])
        return SX1262LoRa(spi, cs=cs, busy=busy, rst=rst, dio1=dio1, freq=cfg.get("freq", 868_000_000))
    return lora_cls(spi, cs=cs, rst=rst, dio0=dio0, chip=lora_chip, freq=cfg.get("freq"))


def make_payload(cfg, lux, charger, now_fn=None):
    now_fn = now_fn or (lambda: int(time.time()))
    lat = cfg.get("lat", DEFAULT_CONFIG["lat"])
    lon = cfg.get("lon", DEFAULT_CONFIG["lon"])
    return {
        "name": cfg.get("name", DEFAULT_CONFIG["name"]),
        "latitude": lat,
        "longitude": lon,
        "gps": [lat, lon],
        "state": "home",
        "lux": lux,
        "ts": int(now_fn()),
        "charger_type": cfg.get("charger_type", DEFAULT_CONFIG["charger_type"]),
        "charger_status": charger.status(),
    }


def main(loop_once=False, sleep_fn=time.sleep, now_fn=None):
    cfg = load_config()
    sensor = make_sensor(cfg)
    charger = make_charger(cfg)
    lora = make_lora(cfg)
    interval = cfg.get("poll_interval", DEFAULT_CONFIG["poll_interval"])

    while True:
        lux_val = sensor.read_lux()
        payload = make_payload(cfg, lux_val, charger, now_fn=now_fn)
        lora.send(ujson.dumps(payload).encode())
        if loop_once:
            break
        sleep_fn(interval)


if __name__ == "__main__":
    main()
