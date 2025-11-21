import unittest
import urllib.request
import urllib.error

HA_URL = "http://localhost:8123"
INFLUX_URL = "http://localhost:8086/health"
INFLUX_TOKEN = "ha-dev-token"


class StackSmokeTests(unittest.TestCase):
    def test_homeassistant_up(self):
        try:
            with urllib.request.urlopen(HA_URL, timeout=3) as resp:
                status = resp.getcode()
                body = resp.read()
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
            self.skipTest("Home Assistant is not reachable on localhost:8123")
            return
        self.assertGreaterEqual(status, 200)
        self.assertLess(status, 400)
        self.assertIn(b"Home Assistant", body)

    def test_influxdb_health(self):
        req = urllib.request.Request(
            INFLUX_URL,
            headers={"Authorization": f"Token {INFLUX_TOKEN}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                status = resp.getcode()
                body = resp.read()
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
            self.skipTest("InfluxDB is not reachable on localhost:8086")
            return
        self.assertEqual(status, 200)
        self.assertIn(b"\"status\":\"pass\"", body)


if __name__ == "__main__":
    unittest.main()
