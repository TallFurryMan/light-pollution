import os
import sys
import tempfile
import unittest
from unittest import mock

# Allow importing MicroPython firmware modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "firmware"))

import firmware


class FakeADC:
    def __init__(self, pin, value=0x2000):
        self.pin = pin
        self.value = value

    def read_u16(self):
        return self.value


class FakePin:
    def __init__(self, pin_no):
        self.pin_no = pin_no


class FakeI2C:
    def __init__(self, read_map=None):
        self.read_map = read_map or {}
        self.writes = []

    def writeto_mem(self, addr, reg, data):
        self.writes.append(("writeto_mem", addr, reg, bytes(data)))

    def readfrom_mem(self, addr, reg, length):
        return self.read_map.get((addr, reg, length), b"\x00" * length)

    def writeto(self, addr, data):
        self.writes.append(("writeto", addr, bytes(data)))

    def readfrom(self, addr, length):
        return self.read_map.get((addr, length), b"\x00" * length)


class FakeCharger(firmware.BaseCharger):
    def __init__(self, status_text):
        self._status = status_text

    def status(self):
        return self._status


class FirmwareTests(unittest.TestCase):
    def test_load_config_defaults_when_missing(self):
        with tempfile.TemporaryDirectory() as td:
            path = td + "/missing.json"
            cfg = firmware.load_config(path)
            self.assertEqual(cfg["name"], "unknown")
            self.assertEqual(cfg["poll_interval"], 900)

    def test_make_payload_uses_defaults_and_charger_status(self):
        charger = FakeCharger("charging")
        cfg = {"name": "node-1", "lat": 1.1, "lon": 2.2, "charger_type": "TP4056"}
        payload = firmware.make_payload(cfg, lux=123, charger=charger, now_fn=lambda: 42)
        self.assertEqual(payload["name"], "node-1")
        self.assertEqual(payload["lux"], 123)
        self.assertEqual(payload["ts"], 42)
        self.assertEqual(payload["charger_status"], "charging")

    def test_temt6000_conversion(self):
        adc = FakeADC(pin=FakePin(2), value=32768)
        sensor = firmware.TEMT6000(adc_cls=lambda pin: adc, pin_cls=FakePin)
        lux = sensor.read_lux()
        self.assertTrue(1600 < lux < 1700)

    def test_bh1750_reads_expected_value(self):
        i2c = FakeI2C(read_map={(0x23, 2): b"\x01\x20"})
        sensor = firmware.BH1750(i2c)
        self.assertEqual(sensor.read_lux(), 0x0120 / 1.2)

    def test_tsl2591_reads_expected_value(self):
        i2c = FakeI2C(read_map={(0x29, 0x86, 2): b"\x10\x00"})
        sensor = firmware.TSL2591(i2c)
        self.assertEqual(sensor.read_lux(), 0x0010 * 0.064)

    def test_make_sensor_selects_i2c_sensor(self):
        cfg = {"sensor_type": "BH1750"}
        fake_i2c = FakeI2C()
        sensor = firmware.make_sensor(cfg, i2c_cls=lambda *args, **kwargs: fake_i2c, pin_cls=FakePin)
        self.assertIsInstance(sensor, firmware.BH1750)
        self.assertIn(("writeto", 0x23, b"\x10"), fake_i2c.writes)

    def test_make_sensor_selects_adc_sensor(self):
        cfg = {"sensor_type": "TEMT6000"}
        sensor = firmware.make_sensor(cfg, adc_cls=lambda pin: FakeADC(pin, value=1000), pin_cls=FakePin)
        self.assertIsInstance(sensor, firmware.TEMT6000)

    def test_make_charger_defaults_to_base(self):
        cfg = {"charger_type": "none"}
        charger = firmware.make_charger(cfg, i2c_cls=FakeI2C)
        self.assertIsInstance(charger, firmware.BaseCharger)


if __name__ == "__main__":
    unittest.main()
