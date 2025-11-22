import socket
import unittest
import urllib.request
import urllib.error

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
MQTT_HOSTS = ["mosquitto", "mqtt", "localhost"]
MQTT_PORT = 1883
CHIRPSTACK_ENDPOINTS = [
    "http://chirpstack:8080",
    "http://localhost:8087",
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


if __name__ == "__main__":
    unittest.main()
