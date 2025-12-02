---
lang: en
layout: single
title: "Kids"
permalink: /en/kids
translation_reference: kids
---
## What it does
* Reads light every 15 min.
* Adds a name and GPS coordinates.
* Sends data by long‑range radio to the school’s computer.
* Home Assistant shows the results on a map.

## Quick steps
1. **Assemble** – follow [Assembly]({{ site.baseurl }}{% link en/ASSEMBLY.md %}).
2. **Upload firmware** – copy `src/firmware/firmware.py` and `src/firmware/lorawan.py` to the Pico.
3. **Name & place** – run `python SETUP.PY <name> <lat> <lon>`.
4. **Deploy** – mount outside; power with Li‑Po or small solar + charger (MCP73871 or TP4056).
5. **Check Home Assistant** – view the map card.
6. **Discuss** – compare dark vs bright spots.
7. **Report** – write what you learned.

## Code (no need to edit)
`src/firmware/firmware.py` (MicroPython):
* Loads name/latitude/longitude from `config.json`.
* Reads the light sensor every 15 min.
* Sends a JSON payload via LoRa.

## Why MicroPython?
* Lightweight, low cost, easy to read.
* Very close to “regular” Python.
