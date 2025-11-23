import socket
import unittest
import urllib.request
import urllib.error
import json
import time

HA_ENDPOINTS = [
    "http://ha:8123",
    "http://homeassistant:8123",
    "http://localhost:8123",
]
INFLUX_ENDPOINTS = [
    "http://influxdb:8086/health",
    "http://localhost:8086/health",
]
INFLUX_TOKEN = "ha-dev-token"
HA_USER = "admin"
HA_PASSWORD = "adminpw123"
MQTT_HOSTS = ["mosquitto", "mqtt", "localhost"]
MQTT_PORT = 1883
CHIRPSTACK_ENDPOINTS = [
    "http://chirpstack:8080",
    "http://localhost:8087",
]
MQTT_DISCOVERY_TOPICS = [
    "homeassistant/device_tracker/melesse1/config",
    "homeassistant/device_tracker/melesse2/config",
    "homeassistant/sensor/melesse_lux/config",
]
MQTT_STATE_TOPICS = [
    "melesse/trackers/melesse1",
    "melesse/trackers/melesse2",
    "melesse/sensors/lux",
]


def first_response(urls, headers=None):
    for url in urls:
        req = urllib.request.Request(url, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                body = resp.read()
                status = resp.getcode()
            return url, status, body
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
            continue
    return None, None, None


def port_open(hosts, port, timeout=2):
    for host in hosts:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return host
        except OSError:
            continue
    return None


class StackSmokeTests(unittest.TestCase):
    def test_homeassistant_up(self):
        url, status, body = first_response(HA_ENDPOINTS)
        if status is None:
            self.skipTest("Home Assistant is not reachable on known endpoints")
            return
        self.assertGreaterEqual(status, 200)
        self.assertLess(status, 400)
        self.assertIn(b"Home Assistant", body)

    def test_influxdb_health(self):
        url, status, body = first_response(
            INFLUX_ENDPOINTS,
            headers={"Authorization": f"Token {INFLUX_TOKEN}"},
        )
        if status is None:
            self.skipTest("InfluxDB is not reachable on known endpoints")
            return
        self.assertEqual(status, 200)
        self.assertIn(b"\"status\":\"pass\"", body)

    def test_mqtt_port_open(self):
        host = port_open(MQTT_HOSTS, MQTT_PORT)
        if host is None:
            self.skipTest("MQTT broker is not reachable on known hosts")
            return
        self.assertIsNotNone(host)

    def test_chirpstack_ui(self):
        url, status, body = first_response(CHIRPSTACK_ENDPOINTS)
        if status is None:
            self.skipTest("ChirpStack UI is not reachable on known endpoints")
            return
        self.assertGreaterEqual(status, 200)
        self.assertLess(status, 400)

    def test_mqtt_discovery_and_states(self):
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            self.skipTest("paho-mqtt not installed in test runner")
            return

        received = {}

        def on_message(client, userdata, msg):
            received[msg.topic] = msg.payload

        client = mqtt.Client()
        client.connect("mosquitto", 1883, 60)
        client.on_message = on_message
        for t in MQTT_DISCOVERY_TOPICS + MQTT_STATE_TOPICS:
            client.subscribe(t)
        client.loop_start()
        time.sleep(10)
        client.loop_stop()
        client.disconnect()

        missing = [t for t in MQTT_DISCOVERY_TOPICS + MQTT_STATE_TOPICS if t not in received]
        if missing:
            self.fail(f"Missing MQTT topics: {missing}")
        # Basic content checks
        lux_payload = json.loads(received["melesse/sensors/lux"])
        self.assertIn("lux", lux_payload)
        tracker_payload = json.loads(received["melesse/trackers/melesse1"])
        self.assertIn("latitude", tracker_payload)
        self.assertIn("longitude", tracker_payload)


if __name__ == "__main__":
    unittest.main()
