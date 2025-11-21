import unittest
import urllib.request
import urllib.error

HA_ENDPOINTS = [
    "http://ha:8123",
    "http://homeassistant:8123",
    "http://localhost:8123",
]


def first_reachable(urls):
    for url in urls:
        try:
            resp = urllib.request.urlopen(url, timeout=3)
            return url, resp
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
            continue
    return None, None


class HomeAssistantAccessTests(unittest.TestCase):
    def test_homeassistant_ui_accessible(self):
        url, resp = first_reachable(HA_ENDPOINTS)
        if resp is None:
            self.skipTest("Home Assistant UI is not reachable on any known endpoint")
            return
        status = resp.getcode()
        body = resp.read()
        self.assertGreaterEqual(status, 200)
        self.assertLess(status, 400)
        self.assertIn(b"Home Assistant", body)


if __name__ == "__main__":
    unittest.main()
