import json
import sys
import urllib.request
import urllib.error
import urllib.parse
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


def post_json(url, payload, headers=None):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers=headers or {"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code}


def onboard(base):
    status = get_json(base + "/api/onboarding")
    proceed = True
    if isinstance(status, dict):
        proceed = status.get("onboarding", True)
    elif isinstance(status, list):
        proceed = any(not item.get("done", False) for item in status if isinstance(item, dict))
    if not proceed:
        return True
    # Step 1: create user
    resp = post_json(
        base + "/api/onboarding/users",
        {
            "client_id": base,
            "language": "en",
            "name": "Admin",
            "username": "admin",
            "password": "adminpw123",
        },
    )
    if isinstance(resp, dict) and resp.get("error"):
        raise RuntimeError(f"User creation failed: {resp}")
    # Step 2: core config
    resp = post_json(
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
    if isinstance(resp, dict) and resp.get("error"):
        raise RuntimeError(f"Core config failed: {resp}")
    # Step 3: analytics
    resp = post_json(
        base + "/api/onboarding/analytics",
        {"analytics": False},
    )
    if isinstance(resp, dict) and resp.get("error"):
        raise RuntimeError(f"Analytics step failed: {resp}")
    return True


def try_login(base):
    data = urllib.parse.urlencode(
        {
            "grant_type": "password",
            "username": "admin",
            "password": "adminpw123",
            "client_id": base,
        }
    ).encode()
    req = urllib.request.Request(
        base + "/auth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.getcode() == 200
    except Exception:
        return False


def main():
    base = None
    for idx in range(30):
        base = first_base()
        if base:
            break
        time.sleep(2)
        if idx == 0:
            print("Home Assistant not reachable yet, waiting for startup...", file=sys.stderr)
    if not base:
        raise SystemExit("Home Assistant not reachable for onboarding")
    if try_login(base):
        return
    if not onboard(base):
        raise SystemExit("Onboarding did not complete")


if __name__ == "__main__":
    main()
