import time

try:
    import ujson as json
except ImportError:  # pragma: no cover - CPython fallback
    import json

try:
    import ubinascii as binascii
except ImportError:  # pragma: no cover - CPython fallback
    import binascii

try:
    from machine import Pin, SPI
except ImportError:  # Allows importing in CPython tests
    Pin = SPI = None  # type: ignore

from crypto_utils import aes128_cmac, aes128_encrypt_block


_sleep_ms = getattr(time, "sleep_ms", lambda ms: time.sleep(ms / 1000))
_ticks_ms = getattr(time, "ticks_ms", lambda: int(time.time() * 1000))
_ticks_add = getattr(time, "ticks_add", lambda value, delta: value + delta)
_ticks_diff = getattr(time, "ticks_diff", lambda end, start: end - start)

_SX126X_STEP_HZ = 953.67431640625
_SX126X_TIMEOUT_TICKS_PER_MS = 64
_LORA_PACKET_TYPE = 0x01
_LORA_PUBLIC_SYNC_WORD = b"\x34\x44"

_IRQ_TX_DONE = 0x0001
_IRQ_RX_DONE = 0x0002
_IRQ_HEADER_ERROR = 0x0020
_IRQ_CRC_ERROR = 0x0040
_IRQ_TIMEOUT = 0x0200

_JOIN_REQUEST = 0x00
_JOIN_ACCEPT = 0x20
_UNCONFIRMED_DATA_UP = 0x40
_UNCONFIRMED_DATA_DOWN = 0x60
_CONFIRMED_DATA_UP = 0x80
_CONFIRMED_DATA_DOWN = 0xA0

_CID_LINK_CHECK = 0x02
_CID_LINK_ADR = 0x03
_CID_DUTY_CYCLE = 0x04
_CID_RX_PARAM_SETUP = 0x05
_CID_DEV_STATUS = 0x06
_CID_NEW_CHANNEL = 0x07
_CID_RX_TIMING_SETUP = 0x08
_CID_TX_PARAM_SETUP = 0x09
_CID_DL_CHANNEL = 0x0A
_CID_DEVICE_TIME = 0x0D

_DOWNLINK_MAC_LENGTHS = {
    _CID_LINK_CHECK: 2,
    _CID_LINK_ADR: 4,
    _CID_DUTY_CYCLE: 1,
    _CID_RX_PARAM_SETUP: 4,
    _CID_DEV_STATUS: 0,
    _CID_NEW_CHANNEL: 5,
    _CID_RX_TIMING_SETUP: 1,
    _CID_TX_PARAM_SETUP: 1,
    _CID_DL_CHANNEL: 4,
    _CID_DEVICE_TIME: 5,
}

_EU868_DEFAULT_CHANNELS = (
    868_100_000,
    868_300_000,
    868_500_000,
)
_EU868_DATA_RATES = {
    0: {"sf": 12, "bw_code": 0x04, "bandwidth": 125_000},
    1: {"sf": 11, "bw_code": 0x04, "bandwidth": 125_000},
    2: {"sf": 10, "bw_code": 0x04, "bandwidth": 125_000},
    3: {"sf": 9, "bw_code": 0x04, "bandwidth": 125_000},
    4: {"sf": 8, "bw_code": 0x04, "bandwidth": 125_000},
    5: {"sf": 7, "bw_code": 0x04, "bandwidth": 125_000},
    6: {"sf": 7, "bw_code": 0x05, "bandwidth": 250_000},
}
_EU868_RX1_DR_TABLE = (
    (0, 0, 0, 0, 0, 0),
    (1, 0, 0, 0, 0, 0),
    (2, 1, 0, 0, 0, 0),
    (3, 2, 1, 0, 0, 0),
    (4, 3, 2, 1, 0, 0),
    (5, 4, 3, 2, 1, 0),
    (6, 5, 4, 3, 2, 1),
)


def _xor_bytes(left, right):
    return bytes(a ^ b for a, b in zip(left, right))


def _read_hex(value, expected_length, field_name):
    if isinstance(value, (bytes, bytearray)):
        raw = bytes(value)
    else:
        cleaned = str(value or "").replace(" ", "").replace("-", "").replace(":", "")
        try:
            raw = binascii.unhexlify(cleaned)
        except (TypeError, ValueError):
            raise ValueError("invalid %s" % field_name)
    if len(raw) != expected_length:
        raise ValueError("%s must be %d bytes" % (field_name, expected_length))
    return raw


def _hexlify(value):
    return binascii.hexlify(bytes(value)).decode().upper()


def _encode_lorawan_frequency(freq_hz):
    if freq_hz % 100:
        raise ValueError("LoRaWAN frequencies must be encoded in 100 Hz steps")
    return int(freq_hz // 100).to_bytes(3, "little")


def _decode_lorawan_frequency(encoded):
    return int.from_bytes(encoded, "little") * 100


def _derive_payload_keystream(key, dev_addr, frame_counter, direction, length):
    blocks = []
    block_count = (length + 15) // 16
    dev_addr_bytes = int(dev_addr).to_bytes(4, "little")
    counter_bytes = int(frame_counter).to_bytes(4, "little")
    for block_index in range(1, block_count + 1):
        ai = (
            b"\x01\x00\x00\x00\x00"
            + bytes([direction & 0x01])
            + dev_addr_bytes
            + counter_bytes
            + b"\x00"
            + bytes([block_index])
        )
        blocks.append(aes128_encrypt_block(key, ai))
    return b"".join(blocks)[:length]


def _crypt_frm_payload(key, dev_addr, frame_counter, direction, payload):
    stream = _derive_payload_keystream(key, dev_addr, frame_counter, direction, len(payload))
    return _xor_bytes(payload, stream)


def _compute_data_mic(key, phy_payload, dev_addr, frame_counter, direction):
    b0 = (
        b"\x49\x00\x00\x00\x00"
        + bytes([direction & 0x01])
        + int(dev_addr).to_bytes(4, "little")
        + int(frame_counter).to_bytes(4, "little")
        + b"\x00"
        + bytes([len(phy_payload)])
    )
    return aes128_cmac(key, b0 + phy_payload)[:4]


def _dr_requires_ldro(data_rate):
    return data_rate in (0, 1)


def _rx1_data_rate_eu868(uplink_dr, offset):
    uplink_dr = min(max(int(uplink_dr), 0), len(_EU868_RX1_DR_TABLE) - 1)
    offset = min(max(int(offset), 0), len(_EU868_RX1_DR_TABLE[0]) - 1)
    return _EU868_RX1_DR_TABLE[uplink_dr][offset]


def _tx_power_to_dbm(power_index):
    power_index = max(0, int(power_index))
    return max(2, 14 - (power_index * 2))


class LoRa:
    """Very small LoRa helper for SX127x modules (RFM95/SX1278)."""

    def __init__(self, spi, cs, rst, dio0, chip="RFM95", freq=None):
        if Pin is None or (spi is None and SPI is None):
            raise RuntimeError("LoRa requires machine.Pin and machine.SPI")
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.dio0 = Pin(dio0, Pin.IN)
        self.chip = chip
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
        self.rst.low()
        _sleep_ms(10)
        self.rst.high()
        _sleep_ms(10)
        self._write(0x01, bytearray([0x80]))
        self._write(0x01, bytearray([0x81]))

        frf = int(self.freq / 61.03515625)
        self._write(0x06, bytearray([(frf >> 16) & 0xFF]))
        self._write(0x07, bytearray([(frf >> 8) & 0xFF]))
        self._write(0x08, bytearray([frf & 0xFF]))

        self._write(0x1D, bytearray([0x72]))
        self._write(0x1E, bytearray([0x74]))
        self._write(0x09, bytearray([0x8F]))
        self._write(0x40, bytearray([0x40]))
        self._write(0x0E, bytearray([0x00]))
        self._write(0x0F, bytearray([0x00]))

    def send(self, payload, timeout_ms=5000):
        if len(payload) > 255:
            raise ValueError("payload too large")
        self._write(0x0D, bytearray([0x00]))
        self._write(0x00, payload)
        self._write(0x22, bytearray([len(payload)]))
        self._write(0x01, bytearray([0x83]))
        waited_ms = 0
        while not self.dio0.value():
            _sleep_ms(1)
            waited_ms += 1
            if waited_ms >= timeout_ms:
                raise TimeoutError("SX127x transmit did not complete")
        self._write(0x12, bytearray([0xFF]))
        _sleep_ms(10)


class SX1262LoRa:
    """SX1262 radio helper with enough features for Class A LoRaWAN."""

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
        self.data_rate = 5
        self._reset()
        self._configure()

    def _wait_busy(self):
        while self.busy.value():
            _sleep_ms(1)

    def _reset(self):
        self.rst.value(0)
        _sleep_ms(10)
        self.rst.value(1)
        _sleep_ms(10)

    def _write_cmd(self, opcode, params=b""):
        self._wait_busy()
        self.cs.value(0)
        self.spi.write(bytearray([opcode]))
        if params:
            self.spi.write(params)
        self.cs.value(1)
        self._wait_busy()

    def _read_cmd(self, opcode, length, params=b""):
        self._wait_busy()
        self.cs.value(0)
        self.spi.write(bytearray([opcode]))
        if params:
            self.spi.write(params)
        self.spi.write(b"\x00")
        self.spi.read(1)
        result = self.spi.read(length)
        self.cs.value(1)
        self._wait_busy()
        return result

    def _write_register(self, address, data):
        params = address.to_bytes(2, "big") + bytes(data)
        self._write_cmd(0x0D, params)

    def _write_buffer(self, offset, data):
        self._write_cmd(0x0E, bytes([offset & 0xFF]) + bytes(data))

    def _read_buffer(self, offset, length):
        self._wait_busy()
        self.cs.value(0)
        self.spi.write(b"\x1E")
        self.spi.write(bytes([offset & 0xFF, 0x00]))
        result = self.spi.read(length)
        self.cs.value(1)
        self._wait_busy()
        return result

    def _set_rf_frequency(self, freq):
        step = int(freq / _SX126X_STEP_HZ)
        self._write_cmd(
            0x86,
            bytearray(
                [
                    (step >> 24) & 0xFF,
                    (step >> 16) & 0xFF,
                    (step >> 8) & 0xFF,
                    step & 0xFF,
                ]
            ),
        )
        self.freq = freq

    def _set_modulation_params(self, data_rate):
        params = _EU868_DATA_RATES.get(data_rate)
        if params is None:
            raise ValueError("unsupported EU868 data rate DR%d" % data_rate)
        ldro = 0x01 if _dr_requires_ldro(data_rate) else 0x00
        self._write_cmd(
            0x8B,
            bytes(
                [
                    params["sf"],
                    params["bw_code"],
                    0x01,
                    ldro,
                ]
            ),
        )
        self.data_rate = data_rate

    def _set_packet_params(self, payload_length, invert_iq):
        self._write_cmd(
            0x8C,
            bytes(
                [
                    0x00,
                    0x08,
                    0x00,
                    payload_length & 0xFF,
                    0x01,
                    0x00,
                    0x01 if invert_iq else 0x00,
                ]
            ),
        )

    def _set_dio_irq_params(self, irq_mask, dio1_mask):
        self._write_cmd(
            0x08,
            irq_mask.to_bytes(2, "big")
            + dio1_mask.to_bytes(2, "big")
            + b"\x00\x00\x00\x00",
        )

    def _clear_irq_status(self, irq_mask=0xFFFF):
        self._write_cmd(0x02, irq_mask.to_bytes(2, "big"))

    def _get_irq_status(self):
        return int.from_bytes(self._read_cmd(0x12, 2), "big")

    def _get_rx_buffer_status(self):
        payload_length, start_pointer = self._read_cmd(0x13, 2)
        return payload_length, start_pointer

    def set_tx_power(self, power):
        self.power = int(power)

    def _configure(self):
        self._write_cmd(0x80, b"\x00")
        self._write_cmd(0x96, b"\x00")
        self._write_cmd(0x8A, bytes([_LORA_PACKET_TYPE]))
        self._write_cmd(0x9D, b"\x01")
        self._write_cmd(0x95, b"\x04\x07\x00\x01")
        self._write_register(0x0740, _LORA_PUBLIC_SYNC_WORD)
        self._set_rf_frequency(self.freq)
        self._set_modulation_params(self.data_rate)
        self._set_packet_params(0, False)
        self._write_cmd(0x8F, b"\x00\x00")
        self._clear_irq_status()

    def configure(self, freq=None, data_rate=None, invert_iq=False, payload_length=0):
        if freq is not None and freq != self.freq:
            self._set_rf_frequency(freq)
        if data_rate is not None and data_rate != self.data_rate:
            self._set_modulation_params(data_rate)
        self._set_packet_params(payload_length, invert_iq)

    def _timeout_to_bytes(self, timeout_ms):
        ticks = min(int(timeout_ms * _SX126X_TIMEOUT_TICKS_PER_MS), 0xFFFFFF)
        return ticks.to_bytes(3, "big")

    def send(self, payload, timeout_ms=5000, freq=None, data_rate=None, invert_iq=False):
        payload = bytes(payload)
        if len(payload) > 255:
            raise ValueError("payload too large")
        self.configure(freq=freq, data_rate=data_rate, invert_iq=invert_iq, payload_length=len(payload))
        self._clear_irq_status()
        self._set_dio_irq_params(_IRQ_TX_DONE | _IRQ_TIMEOUT, _IRQ_TX_DONE | _IRQ_TIMEOUT)
        self._write_buffer(0, payload)
        self._write_cmd(0x8E, bytes([self.power & 0xFF, 0x04]))
        self._write_cmd(0x83, b"\x00\x00\x00")
        waited_ms = 0
        while not self.dio1.value():
            _sleep_ms(1)
            waited_ms += 1
            if waited_ms >= timeout_ms:
                raise TimeoutError("SX1262 transmit did not complete")
        irq = self._get_irq_status()
        self._clear_irq_status()
        self._write_cmd(0x80, b"\x00")
        if irq & _IRQ_TIMEOUT:
            raise TimeoutError("SX1262 transmit timed out")

    def receive(self, timeout_ms=1000, freq=None, data_rate=None, invert_iq=True):
        self.configure(freq=freq, data_rate=data_rate, invert_iq=invert_iq, payload_length=255)
        self._clear_irq_status()
        irq_mask = _IRQ_RX_DONE | _IRQ_TIMEOUT | _IRQ_CRC_ERROR | _IRQ_HEADER_ERROR
        self._set_dio_irq_params(irq_mask, irq_mask)
        self._write_cmd(0x82, self._timeout_to_bytes(timeout_ms))
        waited_ms = 0
        limit_ms = timeout_ms + 100
        while not self.dio1.value():
            _sleep_ms(1)
            waited_ms += 1
            if waited_ms >= limit_ms:
                self._write_cmd(0x80, b"\x00")
                return None
        irq = self._get_irq_status()
        if irq & (_IRQ_TIMEOUT | _IRQ_CRC_ERROR | _IRQ_HEADER_ERROR):
            self._clear_irq_status()
            self._write_cmd(0x80, b"\x00")
            return None
        if not (irq & _IRQ_RX_DONE):
            self._clear_irq_status()
            self._write_cmd(0x80, b"\x00")
            return None
        payload_length, start_pointer = self._get_rx_buffer_status()
        payload = self._read_buffer(start_pointer, payload_length)
        self._clear_irq_status()
        self._write_cmd(0x80, b"\x00")
        return payload


class LoRaWANNode:
    """Minimal Class A LoRaWAN 1.0.x node for the classroom SX1262 profile."""

    def __init__(
        self,
        radio,
        dev_eui,
        join_eui,
        app_key,
        app_port=10,
        session_path="lorawan-session.json",
        data_rate=5,
        join_data_rate=5,
        tx_power_index=0,
        adr=True,
        rx1_delay=1,
        rx1_dr_offset=0,
        rx2_data_rate=0,
        rx2_frequency=869_525_000,
        sleep_ms_fn=None,
        clock_ms_fn=None,
    ):
        self.radio = radio
        self.dev_eui = _read_hex(dev_eui, 8, "dev_eui")
        self.join_eui = _read_hex(join_eui, 8, "join_eui")
        self.app_key = _read_hex(app_key, 16, "app_key")
        self.app_port = int(app_port)
        self.session_path = session_path
        self.adr = bool(adr)
        self.data_rate = int(data_rate)
        self.join_data_rate = int(join_data_rate)
        self.tx_power_index = int(tx_power_index)
        self.rx1_delay = max(1, int(rx1_delay))
        self.rx1_dr_offset = int(rx1_dr_offset)
        self.rx2_data_rate = int(rx2_data_rate)
        self.rx2_frequency = int(rx2_frequency)
        self.join_accept_delay1 = 5000
        self.join_accept_delay2 = 6000
        self.sleep_ms_fn = sleep_ms_fn or _sleep_ms
        self.clock_ms_fn = clock_ms_fn or _ticks_ms
        self.pending_mac_commands = bytearray()
        self.awaiting_downlink_ack = False
        self.last_downlink = None
        self.network_time = None
        self.link_margin = None
        self.gateway_count = None
        self.max_duty_cycle = 0
        self.nb_trans = 1
        self.channels = self._default_channels()
        self.channel_cursor = 0
        self.dev_nonce = 0
        self.dev_addr = None
        self.nwk_s_key = None
        self.app_s_key = None
        self.f_cnt_up = 0
        self.f_cnt_down = 0
        self._load_state()
        if hasattr(self.radio, "set_tx_power"):
            self.radio.set_tx_power(_tx_power_to_dbm(self.tx_power_index))

    def _default_channels(self):
        channels = [None] * 16
        for index, freq in enumerate(_EU868_DEFAULT_CHANNELS):
            channels[index] = {
                "uplink_freq": freq,
                "downlink_freq": freq,
                "min_dr": 0,
                "max_dr": 5,
                "enabled": True,
            }
        return channels

    def _serialize_channels(self):
        serialized = []
        for channel in self.channels:
            if channel is None:
                serialized.append(None)
                continue
            serialized.append(
                {
                    "uplink_freq": channel["uplink_freq"],
                    "downlink_freq": channel.get("downlink_freq", channel["uplink_freq"]),
                    "min_dr": channel["min_dr"],
                    "max_dr": channel["max_dr"],
                    "enabled": bool(channel.get("enabled", True)),
                }
            )
        return serialized

    def _load_state(self):
        try:
            with open(self.session_path, "r") as handle:
                state = json.load(handle)
        except (OSError, ValueError, TypeError):
            return

        self.dev_nonce = int(state.get("dev_nonce", 0))
        session = state.get("session")
        if not isinstance(session, dict):
            return

        try:
            self.dev_addr = int(session["dev_addr"])
            self.nwk_s_key = _read_hex(session["nwk_s_key"], 16, "nwk_s_key")
            self.app_s_key = _read_hex(session["app_s_key"], 16, "app_s_key")
        except (KeyError, ValueError, TypeError):
            self.dev_addr = None
            self.nwk_s_key = None
            self.app_s_key = None
            return

        self.f_cnt_up = int(session.get("f_cnt_up", 0))
        self.f_cnt_down = int(session.get("f_cnt_down", 0))
        self.data_rate = int(session.get("data_rate", self.data_rate))
        self.tx_power_index = int(session.get("tx_power_index", self.tx_power_index))
        self.rx1_delay = max(1, int(session.get("rx1_delay", self.rx1_delay)))
        self.rx1_dr_offset = int(session.get("rx1_dr_offset", self.rx1_dr_offset))
        self.rx2_data_rate = int(session.get("rx2_data_rate", self.rx2_data_rate))
        self.rx2_frequency = int(session.get("rx2_frequency", self.rx2_frequency))
        self.max_duty_cycle = int(session.get("max_duty_cycle", self.max_duty_cycle))
        self.nb_trans = max(1, int(session.get("nb_trans", self.nb_trans)))
        self.channel_cursor = int(session.get("channel_cursor", self.channel_cursor))
        channels = session.get("channels")
        if isinstance(channels, list) and len(channels) == 16:
            restored = []
            for channel in channels:
                if channel is None:
                    restored.append(None)
                    continue
                restored.append(
                    {
                        "uplink_freq": int(channel["uplink_freq"]),
                        "downlink_freq": int(channel.get("downlink_freq", channel["uplink_freq"])),
                        "min_dr": int(channel.get("min_dr", 0)),
                        "max_dr": int(channel.get("max_dr", 5)),
                        "enabled": bool(channel.get("enabled", True)),
                    }
                )
            self.channels = restored
        if hasattr(self.radio, "set_tx_power"):
            self.radio.set_tx_power(_tx_power_to_dbm(self.tx_power_index))

    def _save_state(self):
        state = {"dev_nonce": self.dev_nonce}
        if self.dev_addr is not None and self.nwk_s_key is not None and self.app_s_key is not None:
            state["session"] = {
                "dev_addr": int(self.dev_addr),
                "nwk_s_key": _hexlify(self.nwk_s_key),
                "app_s_key": _hexlify(self.app_s_key),
                "f_cnt_up": self.f_cnt_up,
                "f_cnt_down": self.f_cnt_down,
                "data_rate": self.data_rate,
                "tx_power_index": self.tx_power_index,
                "rx1_delay": self.rx1_delay,
                "rx1_dr_offset": self.rx1_dr_offset,
                "rx2_data_rate": self.rx2_data_rate,
                "rx2_frequency": self.rx2_frequency,
                "max_duty_cycle": self.max_duty_cycle,
                "nb_trans": self.nb_trans,
                "channel_cursor": self.channel_cursor,
                "channels": self._serialize_channels(),
            }
        try:
            with open(self.session_path, "w") as handle:
                json.dump(state, handle)
        except OSError:
            pass

    def _clear_session(self):
        self.dev_addr = None
        self.nwk_s_key = None
        self.app_s_key = None
        self.f_cnt_up = 0
        self.f_cnt_down = 0
        self.channels = self._default_channels()
        self.channel_cursor = 0
        self.pending_mac_commands = bytearray()
        self.awaiting_downlink_ack = False
        self._save_state()

    def is_joined(self):
        return self.dev_addr is not None and self.nwk_s_key is not None and self.app_s_key is not None

    def _next_dev_nonce(self):
        self.dev_nonce = (self.dev_nonce + 1) & 0xFFFF
        if self.dev_nonce == 0:
            self.dev_nonce = 1
        self._save_state()
        return self.dev_nonce.to_bytes(2, "little")

    def _select_channel(self, data_rate):
        available = []
        for index, channel in enumerate(self.channels):
            if not channel or not channel.get("enabled", True):
                continue
            if channel["min_dr"] <= data_rate <= channel["max_dr"]:
                available.append((index, channel))
        if not available:
            raise RuntimeError("no enabled channel matches DR%d" % data_rate)
        start = self.channel_cursor % len(self.channels)
        for offset in range(len(self.channels)):
            channel_index = (start + offset) % len(self.channels)
            for index, channel in available:
                if index == channel_index:
                    self.channel_cursor = (index + 1) % len(self.channels)
                    return index, channel
        index, channel = available[0]
        self.channel_cursor = (index + 1) % len(self.channels)
        return index, channel

    def _receive_window(self, started_ms, delay_ms, freq, data_rate, timeout_ms=1200):
        deadline = _ticks_add(started_ms, delay_ms)
        wait_ms = _ticks_diff(deadline, self.clock_ms_fn())
        if wait_ms > 0:
            self.sleep_ms_fn(wait_ms)
        return self.radio.receive(
            timeout_ms=timeout_ms,
            freq=freq,
            data_rate=data_rate,
            invert_iq=True,
        )

    def _build_join_request(self, dev_nonce):
        payload = bytes([_JOIN_REQUEST]) + self.join_eui[::-1] + self.dev_eui[::-1] + dev_nonce
        mic = aes128_cmac(self.app_key, payload)[:4]
        return payload + mic

    def _apply_cf_list(self, cf_list):
        if len(cf_list) != 16 or cf_list[-1] != 0x00:
            return
        for index in range(5):
            encoded = cf_list[index * 3:(index + 1) * 3]
            freq = _decode_lorawan_frequency(encoded)
            channel_index = index + 3
            if freq == 0:
                self.channels[channel_index] = None
                continue
            self.channels[channel_index] = {
                "uplink_freq": freq,
                "downlink_freq": freq,
                "min_dr": 0,
                "max_dr": 5,
                "enabled": True,
            }

    def _process_join_accept(self, phy_payload, dev_nonce):
        encrypted = phy_payload[1:]
        if len(encrypted) not in (16, 32):
            return False
        decrypted = []
        for offset in range(0, len(encrypted), 16):
            decrypted.append(aes128_encrypt_block(self.app_key, encrypted[offset:offset + 16]))
        payload = b"".join(decrypted)
        plaintext = bytes([phy_payload[0]]) + payload
        mic = plaintext[-4:]
        computed = aes128_cmac(self.app_key, plaintext[:-4])[:4]
        if mic != computed:
            return False
        body = payload[:-4]
        app_nonce = body[0:3]
        net_id = body[3:6]
        dev_addr = int.from_bytes(body[6:10], "little")
        dl_settings = body[10]
        rx_delay = body[11] or 1
        cf_list = body[12:] if len(body) > 12 else b""

        self.dev_addr = dev_addr
        self.nwk_s_key = aes128_encrypt_block(
            self.app_key,
            b"\x01" + app_nonce + net_id + dev_nonce + (b"\x00" * 7),
        )
        self.app_s_key = aes128_encrypt_block(
            self.app_key,
            b"\x02" + app_nonce + net_id + dev_nonce + (b"\x00" * 7),
        )
        self.f_cnt_up = 0
        self.f_cnt_down = 0
        self.rx1_dr_offset = (dl_settings >> 4) & 0x07
        self.rx2_data_rate = dl_settings & 0x0F
        self.rx1_delay = rx_delay
        self.channels = self._default_channels()
        if cf_list:
            self._apply_cf_list(cf_list)
        self._save_state()
        return True

    def join(self):
        dev_nonce = self._next_dev_nonce()
        join_request = self._build_join_request(dev_nonce)
        _, channel = self._select_channel(self.join_data_rate)
        self.radio.send(
            join_request,
            freq=channel["uplink_freq"],
            data_rate=self.join_data_rate,
            invert_iq=False,
        )
        sent_at = self.clock_ms_fn()
        rx1 = self._receive_window(
            sent_at,
            self.join_accept_delay1,
            channel.get("downlink_freq", channel["uplink_freq"]),
            _rx1_data_rate_eu868(self.join_data_rate, 0),
        )
        if rx1 and rx1[0] == _JOIN_ACCEPT and self._process_join_accept(rx1, dev_nonce):
            return True
        rx2 = self._receive_window(
            sent_at,
            self.join_accept_delay2,
            self.rx2_frequency,
            self.rx2_data_rate,
        )
        if rx2 and rx2[0] == _JOIN_ACCEPT and self._process_join_accept(rx2, dev_nonce):
            return True
        self._clear_session()
        return False

    def ensure_joined(self):
        if self.is_joined():
            return True
        return self.join()

    def _expand_frame_counter(self, short_counter):
        full_counter = (self.f_cnt_down & 0xFFFF0000) | int(short_counter)
        if full_counter < self.f_cnt_down:
            full_counter += 0x10000
        return full_counter

    def _queue_mac_response(self, payload):
        self.pending_mac_commands.extend(payload)

    def _set_channel_mask(self, mask, control):
        if control == 6:
            for channel in self.channels:
                if channel is not None:
                    channel["enabled"] = True
            return True
        if control != 0:
            return False
        any_enabled = False
        for index in range(16):
            enabled = bool(mask & (1 << index))
            channel = self.channels[index]
            if enabled and channel is None:
                return False
            if channel is not None:
                channel["enabled"] = enabled
                any_enabled = any_enabled or enabled
        return any_enabled

    def _handle_link_adr_req(self, payload):
        data_rate_tx_power = payload[0]
        data_rate = (data_rate_tx_power >> 4) & 0x0F
        tx_power = data_rate_tx_power & 0x0F
        channel_mask = int.from_bytes(payload[1:3], "little")
        redundancy = payload[3]
        channel_mask_control = (redundancy >> 4) & 0x07
        nb_trans = redundancy & 0x0F

        status = 0x07
        if data_rate != 0x0F:
            if data_rate in _EU868_DATA_RATES:
                self.data_rate = data_rate
            else:
                status &= ~0x02
        if tx_power != 0x0F:
            if tx_power <= 7:
                self.tx_power_index = tx_power
                if hasattr(self.radio, "set_tx_power"):
                    self.radio.set_tx_power(_tx_power_to_dbm(self.tx_power_index))
            else:
                status &= ~0x04
        if not self._set_channel_mask(channel_mask, channel_mask_control):
            status &= ~0x01
        if nb_trans:
            self.nb_trans = nb_trans
        self._queue_mac_response(bytes([_CID_LINK_ADR, status]))

    def _handle_rx_param_setup_req(self, payload):
        dl_settings = payload[0]
        frequency = _decode_lorawan_frequency(payload[1:4])
        rx1_dr_offset = (dl_settings >> 4) & 0x07
        rx2_dr = dl_settings & 0x0F
        status = 0x07
        if rx1_dr_offset > 5:
            status &= ~0x04
        if rx2_dr not in _EU868_DATA_RATES:
            status &= ~0x02
        if frequency == 0:
            status &= ~0x01
        if status == 0x07:
            self.rx1_dr_offset = rx1_dr_offset
            self.rx2_data_rate = rx2_dr
            self.rx2_frequency = frequency
        self._queue_mac_response(bytes([_CID_RX_PARAM_SETUP, status]))

    def _handle_new_channel_req(self, payload):
        channel_index = payload[0]
        frequency = _decode_lorawan_frequency(payload[1:4])
        dr_range = payload[4]
        min_dr = dr_range & 0x0F
        max_dr = (dr_range >> 4) & 0x0F
        status = 0x03
        if min_dr > max_dr or max_dr > 5:
            status &= ~0x02
        if channel_index >= len(self.channels):
            status &= ~0x01
        if frequency and frequency < 863_000_000:
            status &= ~0x01
        if status == 0x03 and channel_index < len(self.channels):
            if frequency == 0:
                self.channels[channel_index] = None
            else:
                self.channels[channel_index] = {
                    "uplink_freq": frequency,
                    "downlink_freq": frequency,
                    "min_dr": min_dr,
                    "max_dr": max_dr,
                    "enabled": True,
                }
        self._queue_mac_response(bytes([_CID_NEW_CHANNEL, status]))

    def _handle_dl_channel_req(self, payload):
        channel_index = payload[0]
        frequency = _decode_lorawan_frequency(payload[1:4])
        status = 0x03
        channel = self.channels[channel_index] if channel_index < len(self.channels) else None
        if channel is None:
            status &= ~0x02
        if frequency == 0:
            status &= ~0x01
        if status == 0x03:
            channel["downlink_freq"] = frequency
        self._queue_mac_response(bytes([_CID_DL_CHANNEL, status]))

    def _handle_mac_command(self, cid, payload):
        if cid == _CID_LINK_CHECK:
            self.link_margin = payload[0]
            self.gateway_count = payload[1]
            return
        if cid == _CID_LINK_ADR:
            self._handle_link_adr_req(payload)
            return
        if cid == _CID_DUTY_CYCLE:
            self.max_duty_cycle = payload[0] & 0x0F
            self._queue_mac_response(bytes([_CID_DUTY_CYCLE]))
            return
        if cid == _CID_RX_PARAM_SETUP:
            self._handle_rx_param_setup_req(payload)
            return
        if cid == _CID_DEV_STATUS:
            self._queue_mac_response(bytes([_CID_DEV_STATUS, 0xFF, 0x20]))
            return
        if cid == _CID_NEW_CHANNEL:
            self._handle_new_channel_req(payload)
            return
        if cid == _CID_RX_TIMING_SETUP:
            self.rx1_delay = payload[0] & 0x0F or 1
            self._queue_mac_response(bytes([_CID_RX_TIMING_SETUP]))
            return
        if cid == _CID_TX_PARAM_SETUP:
            self._queue_mac_response(bytes([_CID_TX_PARAM_SETUP]))
            return
        if cid == _CID_DL_CHANNEL:
            self._handle_dl_channel_req(payload)
            return
        if cid == _CID_DEVICE_TIME:
            self.network_time = int.from_bytes(payload[0:4], "little")

    def _parse_mac_commands(self, commands):
        index = 0
        while index < len(commands):
            cid = commands[index]
            index += 1
            size = _DOWNLINK_MAC_LENGTHS.get(cid)
            if size is None or index + size > len(commands):
                return
            payload = commands[index:index + size]
            index += size
            self._handle_mac_command(cid, payload)

    def _parse_downlink(self, phy_payload):
        if len(phy_payload) < 12:
            return None
        mhdr = phy_payload[0]
        mtype = mhdr & 0xE0
        if mtype not in (_UNCONFIRMED_DATA_DOWN, _CONFIRMED_DATA_DOWN):
            return None

        dev_addr = int.from_bytes(phy_payload[1:5], "little")
        if dev_addr != self.dev_addr:
            return None

        fctrl = phy_payload[5]
        short_counter = int.from_bytes(phy_payload[6:8], "little")
        frame_counter = self._expand_frame_counter(short_counter)
        fopts_len = fctrl & 0x0F
        fhdr_end = 8 + fopts_len
        if fhdr_end > len(phy_payload) - 4:
            return None
        frame = phy_payload[:-4]
        mic = phy_payload[-4:]
        computed = _compute_data_mic(self.nwk_s_key, frame, self.dev_addr, frame_counter, 1)
        if mic != computed:
            return None

        fopts = phy_payload[8:fhdr_end]
        frm_payload = b""
        fport = None
        if fhdr_end < len(phy_payload) - 4:
            fport = phy_payload[fhdr_end]
            encrypted = phy_payload[fhdr_end + 1:-4]
            key = self.nwk_s_key if fport == 0 else self.app_s_key
            frm_payload = _crypt_frm_payload(key, self.dev_addr, frame_counter, 1, encrypted)

        self.f_cnt_down = frame_counter + 1
        if fopts:
            self._parse_mac_commands(fopts)
        if fport == 0:
            self._parse_mac_commands(frm_payload)
            app_payload = b""
        else:
            app_payload = frm_payload
        if mtype == _CONFIRMED_DATA_DOWN:
            self.awaiting_downlink_ack = True
        self.last_downlink = app_payload
        return app_payload

    def _build_uplink(self, payload, confirmed, f_port):
        if self.dev_addr is None or self.nwk_s_key is None or self.app_s_key is None:
            raise RuntimeError("LoRaWAN session is not established")

        payload = bytes(payload or b"")
        fopts = bytes(self.pending_mac_commands[:15])
        del self.pending_mac_commands[:len(fopts)]

        frm_payload = payload
        port = f_port if payload else None
        if not payload and self.pending_mac_commands:
            frm_payload = bytes(self.pending_mac_commands)
            self.pending_mac_commands = bytearray()
            port = 0

        fctrl = len(fopts)
        if self.adr:
            fctrl |= 0x80
        if self.awaiting_downlink_ack:
            fctrl |= 0x20

        fhdr = (
            int(self.dev_addr).to_bytes(4, "little")
            + bytes([fctrl])
            + int(self.f_cnt_up).to_bytes(2, "little")
            + fopts
        )
        mhdr = bytes([_CONFIRMED_DATA_UP if confirmed else _UNCONFIRMED_DATA_UP])
        frame = mhdr + fhdr
        if port is not None:
            key = self.nwk_s_key if port == 0 else self.app_s_key
            encrypted = _crypt_frm_payload(key, self.dev_addr, self.f_cnt_up, 0, frm_payload)
            frame += bytes([port]) + encrypted
        mic = _compute_data_mic(self.nwk_s_key, frame, self.dev_addr, self.f_cnt_up, 0)
        self.awaiting_downlink_ack = False
        return frame + mic

    def _await_downlink(self, channel, uplink_dr):
        sent_at = self.clock_ms_fn()
        rx1_payload = self._receive_window(
            sent_at,
            self.rx1_delay * 1000,
            channel.get("downlink_freq", channel["uplink_freq"]),
            _rx1_data_rate_eu868(uplink_dr, self.rx1_dr_offset),
        )
        if rx1_payload:
            return self._parse_downlink(rx1_payload)
        rx2_payload = self._receive_window(
            sent_at,
            (self.rx1_delay + 1) * 1000,
            self.rx2_frequency,
            self.rx2_data_rate,
        )
        if rx2_payload:
            return self._parse_downlink(rx2_payload)
        return None

    def send(self, payload, confirmed=False, f_port=None):
        if not self.ensure_joined():
            raise RuntimeError("LoRaWAN join failed")
        port = self.app_port if f_port is None else int(f_port)
        frame = self._build_uplink(payload, confirmed, port)
        _, channel = self._select_channel(self.data_rate)
        self.radio.send(
            frame,
            freq=channel["uplink_freq"],
            data_rate=self.data_rate,
            invert_iq=False,
        )
        downlink = self._await_downlink(channel, self.data_rate)
        self.f_cnt_up += 1
        self._save_state()
        return downlink
