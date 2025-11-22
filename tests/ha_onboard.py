import json
import urllib.request
import urllib.error
import time

HA_ENDPOINTS = [
    "http://ha:8123",
    "http://homeassistant:8123",
    "http://localhost:8123",
]


def first_base():
    for base in HA_ENDPOINTS:
        try:
            urllib.request.urlopen(base + "/api/", timeout=3)
            return base
        except urllib.error.HTTPError:
            # Any HTTP response means the host is reachable
            return base
        except Exception:
            continue
    return None


def get_json(url):
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode())


def post_json(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())


def onboard(base):
    status = get_json(base + "/api/onboarding")
    proceed = True
    if isinstance(status, dict):
        proceed = status.get("onboarding", True)
    elif isinstance(status, list):
        proceed = any(not item.get("done", False) for item in status if isinstance(item, dict))
    if not proceed:
        return
    # Create user
    try:
        post_json(
            base + "/api/onboarding/users",
            {
                "client_id": base,
                "language": "en",
                "name": "Admin",
                "username": "admin",
                "password": "adminpw123",
            },
        )
    except urllib.error.HTTPError:
        pass
    # Core config
    try:
        post_json(
            base + "/api/onboarding/core_config",
            {
                "location": {
                    "latitude": 48.2167,
                    "longitude": -1.6986,
                    "elevation": 60,
                    "unit_system": "metric",
                    "currency": "EUR",
                    "language": "en",
                    "time_zone": "Europe/Paris",
                    "country": "FR",
                },
            },
        )
    except urllib.error.HTTPError:
        pass
    # Analytics opt-out
    try:
        post_json(
            base + "/api/onboarding/analytics",
            {"analytics": False},
        )
    except urllib.error.HTTPError:
        pass


def main():
    base = None
    for _ in range(30):
        base = first_base()
        if base:
            break
        time.sleep(2)
    if not base:
        raise SystemExit("Home Assistant not reachable for onboarding")
    onboard(base)


if __name__ == "__main__":
    main()
