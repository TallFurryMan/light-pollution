---
# Light‑Pollution Monitor – What Kids Need to Know

## Overview
This guide is written so that a 12‑14 year old can follow the build,
the code, and the cloud side step by step.

### What it does
* Reads light levels every 15 min.
* Adds a name and GPS coordinates you give it.
* Sends the data through a long‑range radio to the school’s computer.
* Home Assistant pulls the data and shows the results on a map.

### Quick steps for the class
1. **Assemble** – follow the wiring diagram in *`docs/ASSEMBLY.md`*.
2. **Upload firmware** – copy `src/firmware/firmware.py` and `src/firmware/lorawan.py` to the Pico.
3. **Give it a name & place** – run `python SETUP.PY <unit‑name> <lat> <lon>` on the laptop.
4. **Deploy** – attach it to a tree or pole.  You can use the 4‑cell Li‑Po
   battery, or optionally power it with a small solar panel.  The
   solar panel’s 5 V output goes into the charger module (MCP73871 or
   TP4056), which then feeds the Li‑Po battery and the Pico.
5. **Check Home Assistant** – look at the map card.
6. **Talk about the numbers** – compare dark spots vs bright spots.
7. **Write a short report** – what did you learn about light pollution?

---
### The Code – what you *don't* need to touch
`src/firmware/firmware.py` is a tiny MicroPython script that:
* Loads the device name, latitude and longitude from `config.json`.
* Reads the light sensor on GP2 every 15 min.
* Builds a JSON payload and sends it via the LoRa helper.

---
### Why Python and MicroPython?
MicroPython runs on the Pico, is cheap and easy to learn. The syntax
looks a lot like normal Python, so students who have started with high‑level
languages can pick it up quickly.

---
**Happy measuring, future data scientists!**
