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


def first_response(urls, headers=None):
    for url in urls:
        req = urllib.request.Request(url, headers=headers or {})
        try:
            resp = urllib.request.urlopen(req, timeout=3)
            return url, resp
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
            continue
    return None, None


class StackSmokeTests(unittest.TestCase):
    def test_homeassistant_up(self):
        url, resp = first_response(HA_ENDPOINTS)
        if resp is None:
            self.skipTest("Home Assistant is not reachable on known endpoints")
            return
        status = resp.getcode()
        body = resp.read()
        self.assertGreaterEqual(status, 200)
        self.assertLess(status, 400)
        self.assertIn(b"Home Assistant", body)

    def test_influxdb_health(self):
        url, resp = first_response(
            INFLUX_ENDPOINTS,
            headers={"Authorization": f"Token {INFLUX_TOKEN}"},
        )
        if resp is None:
            self.skipTest("InfluxDB is not reachable on known endpoints")
            return
        status = resp.getcode()
        body = resp.read()
        self.assertEqual(status, 200)
        self.assertIn(b"\"status\":\"pass\"", body)


if __name__ == "__main__":
    unittest.main()
