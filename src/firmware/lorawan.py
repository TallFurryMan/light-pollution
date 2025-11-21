import time

_sleep_ms = getattr(time, "sleep_ms", lambda ms: time.sleep(ms / 1000))

try:
    from machine import Pin, SPI
except ImportError:  # Allows importing in CPython tests
    Pin = SPI = None  # type: ignore

class LoRa:
    """Very small LoRa helper for SX127x modules (RFM95/SX1278).

    Parameters
    ----------
    spi: machine.SPI
        SPI instance.
    cs: int
        Chip‑select GPIO pin.
    rst: int
        Reset GPIO pin.
    dio0: int
        IRQ pin used to detect transmission end.
    chip: str, optional
        ``"RFM95"`` (default) or ``"SX1278"``.
    freq: int, optional
        Frequency in Hz – defaults to 915 MHz for RFM95 and 868 MHz
        for SX1278.
    """

    def __init__(self, spi, cs, rst, dio0, chip="RFM95", freq=None):
        if Pin is None or (spi is None and SPI is None):
            raise RuntimeError("LoRa requires machine.Pin and machine.SPI")
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.dio0 = Pin(dio0, Pin.IN)
        self.chip = chip
        # Default frequency depends on chip type
        if freq is None:
            if chip.lower() == "sx1278":
                self.freq = 868_000_000
            else:
                self.freq = 915_000_000
        else:
            self.freq = freq
        self._setup()

    def _write(self, addr, data):
        self.cs.low()
        self.spi.write(bytearray([addr | 0x80]) + data)
        self.cs.high()

    def _read(self, addr, n):
        self.cs.low()
        self.spi.write(bytearray([addr & 0x7F]))
        result = self.spi.read(n)
        self.cs.high()
        return result

    def _setup(self):
        # Reset and enter LoRa mode
        self.rst.low(); _sleep_ms(10); self.rst.high(); _sleep_ms(10)
        self._write(0x01, bytearray([0x80]))  # LoRa sleep
        self._write(0x01, bytearray([0x81]))  # LoRa standby

        # Frequency settings (FRF registers)
        frf = int(self.freq / 61.03515625)  # FXOSC/2^19
        self._write(0x06, bytearray([(frf >> 16) & 0xFF]))
        self._write(0x07, bytearray([(frf >> 8) & 0xFF]))
        self._write(0x08, bytearray([frf & 0xFF]))

        # Modem config: BW125k, CR4/5, SF7, CRC on
        self._write(0x1D, bytearray([0x72]))
        self._write(0x1E, bytearray([0x74]))
        # PA config and DIO mapping for TxDone on DIO0
        self._write(0x09, bytearray([0x8F]))
        self._write(0x40, bytearray([0x40]))
        # FIFO base addresses
        self._write(0x0E, bytearray([0x00]))
        self._write(0x0F, bytearray([0x00]))

    def send(self, payload):
        """Send a payload (up to 255 bytes) over LoRa.
        It blocks until the transmission is finished.
        """
        length = len(payload)
        if length > 255:
            raise ValueError("payload too large")
        self._write(0x0D, bytearray([0x00]))  # FIFO pointer
        self._write(0x00, payload)            # FIFO
        self._write(0x22, bytearray([length]))
        self._write(0x01, bytearray([0x83]))  # LoRa TX mode
        while not self.dio0.value():
            _sleep_ms(1)
        self._write(0x12, bytearray([0xFF]))  # Clear IRQs
        _sleep_ms(10)


class SX1262LoRa:
    """Minimal SX1262 helper for Waveshare SX1262 868 MHz HATs."""

    def __init__(self, spi, cs, busy, rst, dio1, freq=868_000_000, power=14):
        if Pin is None or (spi is None and SPI is None):
            raise RuntimeError("SX1262 requires machine.Pin and machine.SPI")
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.busy = Pin(busy, Pin.IN)
        self.rst = Pin(rst, Pin.OUT)
        self.dio1 = Pin(dio1, Pin.IN)
        self.freq = freq
        self.power = power
        self._reset()
        self._configure()

    def _wait_busy(self):
        while self.busy.value():
            _sleep_ms(1)

    def _reset(self):
        self.rst.value(0); _sleep_ms(10); self.rst.value(1); _sleep_ms(10)

    def _write_cmd(self, opcode, params=b""):
        self._wait_busy()
        self.cs.value(0)
        self.spi.write(bytearray([opcode]))
        if params:
            self.spi.write(params)
        self.cs.value(1)
        self._wait_busy()

    def _set_rf_frequency(self, freq):
        # Convert Hz to SX1262 freq steps (32e6 / 2^25)
        step = int(freq / 953.67431640625)
        self._write_cmd(0x86, bytearray([
            (step >> 24) & 0xFF,
            (step >> 16) & 0xFF,
            (step >> 8) & 0xFF,
            step & 0xFF,
        ]))

    def _configure(self):
        self._write_cmd(0x80, b"\x00")  # Standby RC
        self._write_cmd(0x96, b"\x00")  # LDO regulator
        self._set_rf_frequency(self.freq)
        # Modulation params: SF7 BW125 CR4/5 LDRO off
        self._write_cmd(0x8B, b"\x07\x04\x01\x00")
        # Packet params: preamble len 8, explicit header, CRC on, IQ standard
        self._write_cmd(0x8C, b"\x00\x08\x00\x00\x01\x00\x00")
        # Buffer bases (TX=0, RX=0)
        self._write_cmd(0x8F, b"\x00\x00")

    def send(self, payload):
        if len(payload) > 255:
            raise ValueError("payload too large")
        # Write payload to buffer at offset 0
        self._write_cmd(0x0E, b"\x00" + bytes(payload))
        # Update packet length (leave other params)
        self._write_cmd(0x8C, b"\x00\x08\x00" + bytes([len(payload)]) + b"\x01\x00\x00")
        # Set TX params (power, ramp)
        self._write_cmd(0x8E, bytes([self.power, 0x04]))
        # SetTx with timeout = 0 (single shot)
        self._write_cmd(0x83, b"\x00\x00\x00")
        while not self.dio1.value():
            _sleep_ms(1)
