import time
from machine import Pin, SPI

class LoRa:
    """Very small LoRa helper that talks to an RFM95 module.
    Uses the raw API – no LoRaWAN header.
    """

    def __init__(self, spi, cs, rst, dio0, freq=915_000_000):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.dio0 = Pin(dio0, Pin.IN)
        self.freq = freq
        self._setup()

    def _write(self, addr, data):
        self.cs.low()
        self.spi.write(bytearray([addr & 0x7F]) + data)
        self.cs.high()

    def _read(self, addr, n):
        self.cs.low()
        self.spi.write(bytearray([addr | 0x80]))
        result = self.spi.read(n)
        self.cs.high()
        return result

    def _setup(self):
        self.rst.low(); time.sleep_ms(10); self.rst.high(); time.sleep_ms(10)
        self._write(0x01, bytearray([0x80]))   # PLL lock
        self._write(0x00, bytearray([0x00]))   # standby mode
        # Frequency settings
        self._write(0x1D, bytearray([self.freq >> 16 & 0xFF]))
        self._write(0x1E, bytearray([self.freq >> 8 & 0xFF]))
        self._write(0x1F, bytearray([self.freq & 0xFF]))
        self._write(0x1E, bytearray([0x70]))   # SF7, BW125k, CR4/5
        self._write(0x12, bytearray([0x04]))   # PA config
        self._write(0x01, bytearray([0x08]))   # TX mode

    def send(self, payload):
        """Send a payload (up to 255 bytes) over LoRa.
        It blocks until the transmission is finished.
        """
        self._write(0x0F, bytearray([0x40]))  # FIFO address ptr
        self._write(0x00, payload)
        self._write(0x25, bytearray([len(payload)]))
        self._write(0x25, bytearray([0x48]))  # TX request
        while not self.dio0.value():
            pass
        time.sleep_ms(50)

