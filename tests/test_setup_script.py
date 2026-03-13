import os
import sys
import unittest
from unittest import mock


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import setup_tool as setup_script


class FakeArgs:
    def __init__(self, **kwargs):
        self.friendly_name = kwargs.get("friendly_name", "node-1")
        self.latitude = kwargs.get("latitude", 48.0)
        self.longitude = kwargs.get("longitude", -1.0)
        self.board_profile = kwargs.get("board_profile", "pico_lora_sx1262_868m")
        self.sensor_type = kwargs.get("sensor_type", "TSL2591")
        self.charger_type = kwargs.get("charger_type", "CN3065")
        self.poll_interval = kwargs.get("poll_interval", 900)
        self.freq = kwargs.get("freq", 868_000_000)


class FakeSerial:
    def __init__(self, response=b"CONFIG_OK"):
        self.response = response
        self.writes = []
        self.flushed = False
        self.reset_called = False

    def write(self, data):
        self.writes.append(data)

    def flush(self):
        self.flushed = True

    def reset_input_buffer(self):
        self.reset_called = True

    def read(self, length):
        return self.response


class SetupScriptTests(unittest.TestCase):
    def test_build_config_keeps_classroom_defaults(self):
        cfg = setup_script.build_config(FakeArgs())
        self.assertEqual(cfg["board_profile"], "pico_lora_sx1262_868m")
        self.assertEqual(cfg["sensor_type"], "TSL2591")
        self.assertEqual(cfg["charger_type"], "CN3065")
        self.assertEqual(cfg["freq"], 868_000_000)

    def test_build_remote_script_embeds_json_safely(self):
        cfg = setup_script.build_config(FakeArgs(friendly_name='node "A"'))
        script = setup_script.build_remote_script(cfg)
        self.assertIn("ujson.loads", script)
        self.assertIn("CONFIG_OK", script)
        self.assertIn('node \\\\"A\\\\"', script)

    def test_provision_device_sends_script_and_checks_confirmation(self):
        fake_serial = FakeSerial()
        with mock.patch.object(setup_script.time, "sleep", lambda _: None):
            setup_script.provision_device(fake_serial, "print('ok')\r\n")
        self.assertTrue(fake_serial.flushed)
        self.assertTrue(fake_serial.reset_called)
        self.assertTrue(any(b"print('ok')" in chunk for chunk in fake_serial.writes))

    def test_provision_device_raises_without_confirmation(self):
        fake_serial = FakeSerial(response=b"")
        with mock.patch.object(setup_script.time, "sleep", lambda _: None):
            with self.assertRaises(RuntimeError):
                setup_script.provision_device(fake_serial, "print('ok')\r\n")


if __name__ == "__main__":
    unittest.main()
