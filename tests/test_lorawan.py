import os
import sys
import unittest
from unittest import mock

# Allow importing MicroPython firmware modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "firmware"))

import lorawan


class FakePin:
    OUT = 1
    IN = 0

    def __init__(self, pin_no, mode=None):
        self.pin_no = pin_no
        self.mode = mode
        self._value = True

    def low(self):
        self._value = False

    def high(self):
        self._value = True

    def value(self):
        return self._value


class FakeSPI:
    def __init__(self, *args, **kwargs):
        self.writes = []
        self.reads = []

    def write(self, data):
        self.writes.append(bytes(data))

    def read(self, n):
        out = b"\x00" * n
        self.reads.append(out)
        return out


class LoRaTests(unittest.TestCase):
    def setUp(self):
        self.pin_patch = mock.patch.object(lorawan, "Pin", FakePin)
        self.sleep_patch = mock.patch.object(lorawan, "_sleep_ms", lambda ms: None)
        self.pin_patch.start()
        self.sleep_patch.start()

    def tearDown(self):
        self.pin_patch.stop()
        self.sleep_patch.stop()

    def test_setup_writes_frequency_and_config(self):
        spi = FakeSPI()
        lorawan.LoRa(spi=spi, cs=5, rst=6, dio0=7, chip="RFM95", freq=915_000_000)
        written_regs = [w[0] for w in spi.writes]
        self.assertIn(0x86, written_regs)
        self.assertIn(0x87, written_regs)
        self.assertIn(0x88, written_regs)
        self.assertIn(0x9D, written_regs)
        self.assertIn(0x9E, written_regs)
        self.assertIn(0x89, written_regs)
        self.assertIn(0x8E, written_regs)

    def test_send_writes_fifo_and_payload_length(self):
        spi = FakeSPI()
        radio = lorawan.LoRa(spi=spi, cs=5, rst=6, dio0=7)
        spi.writes.clear()
        radio.send(b"hi")
        written = spi.writes
        self.assertIn(b"\x8d\x00", written)
        self.assertTrue(any(entry.startswith(b"\x80hi") for entry in written))
        self.assertIn(b"\xa2\x02", written)
        self.assertIn(b"\x81\x83", written)
        self.assertIn(b"\x92\xff", written)


if __name__ == "__main__":
    unittest.main()
