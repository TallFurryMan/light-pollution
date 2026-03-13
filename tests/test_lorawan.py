import os
import sys
import tempfile
import unittest
from unittest import mock

# Allow importing MicroPython firmware modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "firmware"))

import crypto_utils
import lorawan


class FakePin:
    OUT = 1
    IN = 0

    def __init__(self, pin_no, mode=None, initial=True):
        if isinstance(pin_no, FakePin):
            initial = pin_no._value
        self.pin_no = pin_no
        self.mode = mode
        self._value = initial

    def low(self):
        self._value = False

    def high(self):
        self._value = True

    def value(self, val=None):
        if val is not None:
            self._value = bool(val)
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


class FakeClock:
    def __init__(self):
        self.now = 0
        self.sleeps = []

    def now_ms(self):
        return self.now

    def sleep(self, delay_ms):
        self.sleeps.append(delay_ms)
        self.now += delay_ms


class FakeRadio:
    def __init__(self):
        self.sent = []
        self.receive_queue = []
        self.receives = []
        self.power = None

    def set_tx_power(self, power):
        self.power = power

    def send(self, payload, **kwargs):
        self.sent.append((bytes(payload), kwargs))

    def receive(self, **kwargs):
        self.receives.append(kwargs)
        if self.receive_queue:
            return self.receive_queue.pop(0)
        return None


def build_join_accept(app_key, dev_addr, dev_nonce, dl_settings=0x00, rx_delay=1, cf_list=b""):
    app_nonce = b"\x01\x02\x03"
    net_id = b"\x00\x00\x13"
    plaintext = (
        app_nonce
        + net_id
        + int(dev_addr).to_bytes(4, "little")
        + bytes([dl_settings, rx_delay])
        + cf_list
    )
    mic = lorawan.aes128_cmac(app_key, bytes([lorawan._JOIN_ACCEPT]) + plaintext)[:4]
    encrypted = b""
    complete = plaintext + mic
    for offset in range(0, len(complete), 16):
        encrypted += crypto_utils.aes128_decrypt_block(app_key, complete[offset:offset + 16])
    return bytes([lorawan._JOIN_ACCEPT]) + encrypted


def build_downlink(node, frame_counter, fopts=b"", fport=10, payload=b"", confirmed=False):
    mhdr = bytes([lorawan._CONFIRMED_DATA_DOWN if confirmed else lorawan._UNCONFIRMED_DATA_DOWN])
    fhdr = (
        int(node.dev_addr).to_bytes(4, "little")
        + bytes([len(fopts)])
        + int(frame_counter).to_bytes(2, "little")
        + bytes(fopts)
    )
    frame = mhdr + fhdr
    if fport is not None:
        key = node.nwk_s_key if fport == 0 else node.app_s_key
        encrypted = lorawan._crypt_frm_payload(key, node.dev_addr, frame_counter, 1, bytes(payload))
        frame += bytes([fport]) + encrypted
    mic = lorawan._compute_data_mic(node.nwk_s_key, frame, node.dev_addr, frame_counter, 1)
    return frame + mic


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

    def test_sx1262_command_sequence(self):
        spi = FakeSPI()
        lorawan.SX1262LoRa(
            spi=spi,
            cs=5,
            busy=FakePin(6, initial=False),
            rst=7,
            dio1=FakePin(8, initial=True),
        )
        opcodes = [chunk[0] for chunk in spi.writes if chunk]
        self.assertIn(0x80, opcodes)
        self.assertIn(0x96, opcodes)
        self.assertIn(0x8A, opcodes)
        self.assertIn(0x86, opcodes)
        self.assertIn(0x8B, opcodes)
        self.assertIn(0x8C, opcodes)
        self.assertIn(0x8F, opcodes)
        self.assertIn(0x95, opcodes)


class LoRaWANNodeTests(unittest.TestCase):
    APP_KEY = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    JOIN_EUI = "70B3D57ED005A11A"
    DEV_EUI = "0004A30B001C0530"

    def make_node(self, radio, session_path, clock):
        return lorawan.LoRaWANNode(
            radio,
            dev_eui=self.DEV_EUI,
            join_eui=self.JOIN_EUI,
            app_key=self.APP_KEY,
            app_port=10,
            session_path=session_path,
            data_rate=5,
            join_data_rate=5,
            sleep_ms_fn=clock.sleep,
            clock_ms_fn=clock.now_ms,
        )

    def join_node(self, node, radio):
        join_request = node._build_join_request((1).to_bytes(2, "little"))
        expected_dev_nonce = join_request[-6:-4]
        radio.receive_queue = [
            build_join_accept(self.APP_KEY, 0x26011BDA, expected_dev_nonce),
        ]
        joined = node.join()
        self.assertTrue(joined)
        return expected_dev_nonce

    def test_join_otaa_derives_session_and_persists_state(self):
        with tempfile.TemporaryDirectory() as td:
            session_path = os.path.join(td, "session.json")
            radio = FakeRadio()
            clock = FakeClock()
            node = self.make_node(radio, session_path, clock)

            dev_nonce = self.join_node(node, radio)

            self.assertEqual(dev_nonce, b"\x01\x00")
            self.assertTrue(node.is_joined())
            self.assertEqual(node.dev_addr, 0x26011BDA)
            self.assertEqual(node.f_cnt_up, 0)
            self.assertEqual(clock.sleeps, [5000])
            self.assertEqual(radio.sent[0][0][0], lorawan._JOIN_REQUEST)
            self.assertEqual(radio.power, 14)
            with open(session_path, "r") as handle:
                saved = handle.read()
            self.assertIn('"session"', saved)
            self.assertIn('"dev_nonce": 1', saved)

    def test_send_encrypts_application_payload_and_queues_mac_response(self):
        with tempfile.TemporaryDirectory() as td:
            session_path = os.path.join(td, "session.json")
            radio = FakeRadio()
            clock = FakeClock()
            node = self.make_node(radio, session_path, clock)
            self.join_node(node, radio)
            radio.sent.clear()
            clock.sleeps.clear()

            link_adr_req = bytes([lorawan._CID_LINK_ADR, 0x31, 0x07, 0x00, 0x01])
            radio.receive_queue = [build_downlink(node, 0, fopts=link_adr_req)]
            payload = b'{"lux":123}'

            node.send(payload)

            uplink, tx_kwargs = radio.sent[0]
            self.assertIn(tx_kwargs["freq"], (868_100_000, 868_300_000, 868_500_000))
            self.assertEqual(tx_kwargs["data_rate"], 5)
            self.assertEqual(uplink[0], lorawan._UNCONFIRMED_DATA_UP)
            fopts_len = uplink[5] & 0x0F
            port_index = 8 + fopts_len
            self.assertEqual(uplink[port_index], 10)
            encrypted = uplink[port_index + 1:-4]
            decrypted = lorawan._crypt_frm_payload(node.app_s_key, node.dev_addr, 0, 0, encrypted)
            self.assertEqual(decrypted, payload)
            self.assertEqual(bytes(node.pending_mac_commands), bytes([lorawan._CID_LINK_ADR, 0x07]))
            self.assertEqual(node.data_rate, 3)
            self.assertEqual(node.tx_power_index, 1)
            self.assertEqual(radio.power, 12)
            self.assertEqual(clock.sleeps, [1000])

    def test_next_uplink_flushes_pending_mac_commands_in_fopts(self):
        with tempfile.TemporaryDirectory() as td:
            session_path = os.path.join(td, "session.json")
            radio = FakeRadio()
            clock = FakeClock()
            node = self.make_node(radio, session_path, clock)
            self.join_node(node, radio)
            node.pending_mac_commands = bytearray([lorawan._CID_LINK_ADR, 0x07])
            radio.sent.clear()
            radio.receive_queue = []

            node.send(b"{}")

            uplink, _ = radio.sent[0]
            self.assertEqual(uplink[5] & 0x0F, 2)
            self.assertEqual(uplink[8:10], b"\x03\x07")
            self.assertEqual(bytes(node.pending_mac_commands), b"")

    def test_session_restores_without_joining_again(self):
        with tempfile.TemporaryDirectory() as td:
            session_path = os.path.join(td, "session.json")
            first_radio = FakeRadio()
            first_clock = FakeClock()
            first_node = self.make_node(first_radio, session_path, first_clock)
            self.join_node(first_node, first_radio)

            second_radio = FakeRadio()
            second_clock = FakeClock()
            restored = self.make_node(second_radio, session_path, second_clock)

            self.assertTrue(restored.is_joined())
            restored.send(b"payload")

            first_byte = second_radio.sent[0][0][0]
            self.assertEqual(first_byte, lorawan._UNCONFIRMED_DATA_UP)
            self.assertEqual(len(second_radio.sent), 1)


if __name__ == "__main__":
    unittest.main()
