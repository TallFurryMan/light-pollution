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
BOARD_PROFILES = {
    "pico_lora_sx1262_868m": {
        "lora_chip": "SX1262",
        "freq": 868_000_000,
        "spi_id": 1,
        "spi_sck": 10,
        "spi_mosi": 11,
        "spi_miso": 12,
        "lora_cs": 3,
        "lora_rst": 15,
        "lora_busy": 2,
        "lora_dio1": 20,
        "sensor_i2c_id": 0,
        "sensor_scl": 5,
        "sensor_sda": 4,
        "sensor_adc_pin": 2,
        "battery_adc_pin": 26,
    },
}
DEFAULT_CONFIG = {
    "board_profile": "pico_lora_sx1262_868m",
    "protocol": "lorawan",
    "name": "unknown",
    "lat": 0.0,
    "lon": 0.0,
    "sensor_type": "TSL2591",
    "charger_type": "CN3065",
    "poll_interval": 900,
    "lora_chip": "SX1262",
    "freq": 868_000_000,
    "spi_id": 1,
    "spi_sck": 10,
    "spi_mosi": 11,
    "spi_miso": 12,
    "lora_cs": 3,
    "lora_rst": 15,
    "lora_dio0": 20,
    "lora_busy": 2,
    "lora_dio1": 20,
    "sensor_i2c_id": 0,
    "sensor_scl": 5,
    "sensor_sda": 4,
    "sensor_adc_pin": 2,
    "battery_adc_pin": 26,
    "join_eui": "",
    "dev_eui": "",
    "app_key": "",
    "app_port": 10,
    "lorawan_dr": 5,
    "lorawan_join_dr": 5,
    "lorawan_tx_power": 0,
    "session_path": "lorawan-session.json",
    "adr": True,
    "rx1_delay": 1,
    "rx1_dr_offset": 0,
    "rx2_data_rate": 0,
    "rx2_frequency": 869_525_000,
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
    profile = cfg.get("board_profile", merged["board_profile"])
    merged.update(BOARD_PROFILES.get(profile, {}))
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


class CN3065(BaseCharger):
    pass


def make_sensor(cfg, i2c_cls=I2C, adc_cls=ADC, pin_cls=Pin):
    sensor_type = cfg.get("sensor_type", DEFAULT_CONFIG["sensor_type"])
    if sensor_type in ("TSL2591", "BH1750"):
        if i2c_cls is None or pin_cls is None:
            raise RuntimeError("I2C sensor requested but machine.I2C is missing")
        sensor_i2c = i2c_cls(
            cfg.get("sensor_i2c_id", 0),
            scl=pin_cls(cfg.get("sensor_scl", 5)),
            sda=pin_cls(cfg.get("sensor_sda", 4)),
        )
        if sensor_type == "TSL2591":
            return TSL2591(sensor_i2c)
        return BH1750(sensor_i2c)
    return TEMT6000(
        pin_no=cfg.get("sensor_adc_pin", 2),
        adc_cls=adc_cls,
        pin_cls=pin_cls,
    )


def make_charger(cfg, i2c_cls=I2C):
    charger_type = cfg.get("charger_type", DEFAULT_CONFIG["charger_type"])
    if charger_type == "MCP73871":
        if i2c_cls is None:
            raise RuntimeError("MCP73871 requires machine.I2C")
        return MCP73871(i2c_cls(1))
    if charger_type == "TP4056":
        return TP4056()
    if charger_type == "CN3065":
        return CN3065()
    return BaseCharger()


def make_lora(cfg, spi=None, pin_cls=Pin, lora_cls=LoRa):
    if pin_cls is None or (spi is None and SPI is None):
        raise RuntimeError("LoRa requires machine.SPI and machine.Pin")
    spi = spi or SPI(
        cfg.get("spi_id", 0),
        baudrate=5_000_000,
        sck=pin_cls(cfg.get("spi_sck", 13)),
        mosi=pin_cls(cfg.get("spi_mosi", 15)),
        miso=pin_cls(cfg.get("spi_miso", 14)),
    )
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


def make_transport(cfg, spi=None, pin_cls=Pin, lora_cls=LoRa):
    protocol = str(cfg.get("protocol", DEFAULT_CONFIG["protocol"])).lower()
    radio = make_lora(cfg, spi=spi, pin_cls=pin_cls, lora_cls=lora_cls)
    if protocol in ("raw", "lora"):
        return radio
    if protocol != "lorawan":
        raise RuntimeError("Unsupported radio protocol: %s" % protocol)
    if str(cfg.get("lora_chip", DEFAULT_CONFIG["lora_chip"])).upper() != "SX1262":
        raise RuntimeError("The built-in LoRaWAN path currently supports the SX1262 classroom node profile")
    required = ("join_eui", "dev_eui", "app_key")
    missing = [field for field in required if not cfg.get(field)]
    if missing:
        raise RuntimeError("Missing LoRaWAN credentials: %s" % ", ".join(missing))
    from lorawan import LoRaWANNode  # late import to keep the raw path lightweight

    return LoRaWANNode(
        radio,
        dev_eui=cfg["dev_eui"],
        join_eui=cfg["join_eui"],
        app_key=cfg["app_key"],
        app_port=cfg.get("app_port", DEFAULT_CONFIG["app_port"]),
        session_path=cfg.get("session_path", DEFAULT_CONFIG["session_path"]),
        data_rate=cfg.get("lorawan_dr", DEFAULT_CONFIG["lorawan_dr"]),
        join_data_rate=cfg.get("lorawan_join_dr", DEFAULT_CONFIG["lorawan_join_dr"]),
        tx_power_index=cfg.get("lorawan_tx_power", DEFAULT_CONFIG["lorawan_tx_power"]),
        adr=cfg.get("adr", DEFAULT_CONFIG["adr"]),
        rx1_delay=cfg.get("rx1_delay", DEFAULT_CONFIG["rx1_delay"]),
        rx1_dr_offset=cfg.get("rx1_dr_offset", DEFAULT_CONFIG["rx1_dr_offset"]),
        rx2_data_rate=cfg.get("rx2_data_rate", DEFAULT_CONFIG["rx2_data_rate"]),
        rx2_frequency=cfg.get("rx2_frequency", DEFAULT_CONFIG["rx2_frequency"]),
    )


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
    transport = make_transport(cfg)
    interval = cfg.get("poll_interval", DEFAULT_CONFIG["poll_interval"])

    while True:
        lux_val = sensor.read_lux()
        payload = make_payload(cfg, lux_val, charger, now_fn=now_fn)
        transport.send(ujson.dumps(payload).encode())
        if loop_once:
            break
        sleep_fn(interval)


if __name__ == "__main__":
    main()
