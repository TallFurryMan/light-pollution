import json
import urllib.request
import urllib.error

HA_ENDPOINTS = [
    "http://ha:8123",
    "http://homeassistant:8123",
    "http://localhost:8123",
]


def first_base():
    for base in HA_ENDPOINTS:
        try:
            with urllib.request.urlopen(base + "/api/", timeout=3):
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
    if not status.get("onboarding"):
        return
    # Create user
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
    # Core config
    post_json(
        base + "/api/onboarding/core_config",
        {
            "location": {
                "latitude": 0,
                "longitude": 0,
                "elevation": 0,
                "unit_system": "metric",
                "currency": "USD",
                "language": "en",
                "time_zone": "UTC",
                "country": "US",
            },
        },
    )
    # Analytics opt-out
    post_json(
        base + "/api/onboarding/analytics",
        {"analytics": False},
    )


def main():
    base = first_base()
    if not base:
        raise SystemExit("Home Assistant not reachable for onboarding")
    onboard(base)


if __name__ == "__main__":
    main()
