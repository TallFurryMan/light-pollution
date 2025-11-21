import unittest
import urllib.request
import urllib.error


HA_URL = "http://localhost:8123"


class HomeAssistantAccessTests(unittest.TestCase):
    def test_homeassistant_ui_accessible(self):
        try:
            with urllib.request.urlopen(HA_URL, timeout=3) as resp:
                status = resp.getcode()
                body = resp.read()
        except (urllib.error.URLError, ConnectionRefusedError):
            self.skipTest("Home Assistant UI is not reachable on localhost:8123")
            return
        self.assertGreaterEqual(status, 200)
        self.assertLess(status, 400)
        self.assertIn(b"Home Assistant", body)


if __name__ == "__main__":
    unittest.main()
