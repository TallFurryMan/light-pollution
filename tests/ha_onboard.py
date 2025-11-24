import sys
import time
import urllib.request
import urllib.error
import urllib.parse

HA_ENDPOINTS = [
    "http://ha:8123",
    "http://homeassistant:8123",
    "http://localhost:8123",
]

USERNAME = "admin"
PASSWORD = "adminpw123"


def first_base():
    for base in HA_ENDPOINTS:
        try:
            urllib.request.urlopen(base + "/api/", timeout=3)
            return base
        except urllib.error.HTTPError:
            return base
        except Exception:
            continue
    return None


def can_login(base):
    data = urllib.parse.urlencode(
        {
            "grant_type": "password",
            "username": USERNAME,
            "password": PASSWORD,
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
        raise SystemExit("Home Assistant not reachable for login")
    if not can_login(base):
        raise SystemExit("Home Assistant login failed with seeded credentials")


if __name__ == "__main__":
    main()
