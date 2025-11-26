---
# Light‑Pollution Monitor – What Kids Need to Know

## Overview
Written for 12‑14 year olds to follow the build, code, and cloud steps.

### What it does
* Reads light every 15 min.
* Adds a name and GPS coordinates.
* Sends data by long‑range radio to the school’s computer.
* Home Assistant shows the results on a map.

### Quick steps
1. **Assemble** – see `docs/ASSEMBLY.md`.
2. **Upload firmware** – copy `src/firmware/firmware.py` and `lorawan.py` to the Pico.
3. **Name & place** – run `python SETUP.PY <name> <lat> <lon>`.
4. **Deploy** – mount outside; power with Li‑Po or small solar + charger.
5. **Check Home Assistant** – view the map card.
6. **Discuss** – compare dark vs bright spots.
7. **Report** – write what you learned.

### Code (no need to edit)
`src/firmware/firmware.py`:
* Loads name/GPS from `config.json`.
* Reads light every 15 min.
* Sends JSON via LoRa.

### Why MicroPython?
* Lightweight, low cost, easy to read.
* Very close to “regular” Python.
