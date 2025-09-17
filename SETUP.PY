"""Utility to write the unit configuration to the Pico via serial.

Prerequisites:
- Pico flashed with the firmware from `FIRMWARE.md`.
- Python package `pyserial` (install with `pip install pyserial`).
"""

import serial
import json
import sys
import time

PORT = "COM3" if sys.platform.startswith("win") else "/dev/ttyUSB0"
BAUD = 115200

def main():
    if len(sys.argv) != 4:
        print("Usage: python SETUP.PY <friendly_name> <lat> <lon>")
        return
    name, lat, lon = sys.argv[1:]
    cfg = {"name": name, "lat": float(lat), "lon": float(lon)}
    payload = json.dumps(cfg).encode("utf-8")

    print(f"Sending config to Pico on {PORT} …")
    with serial.Serial(PORT, BAUD, timeout=5) as ser:
        # Wait for REPL prompt
        while not ser.read(1):
            pass
        # Send reset and load config
        ser.write(b"import os\nimport ujson\n\n# Write config file\nwith open('config.json','w') as f:\n    f.write('" + payload.decode("utf-8") + "')\n\n" )
        ser.flush()
        time.sleep(1)
    print("Configuration written successfully.")


if __name__ == "__main__":
    main()

