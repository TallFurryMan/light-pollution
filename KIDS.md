# Light‑Pollution Monitor – What Kids Need to Know
This guide is written so that a 12‑14 year old can follow the build, the code, and the cloud side step by step.

## Overview
We’re building a tiny weather‑station‑style device that tells us how bright the night sky is in different parts of the village.

### What it does
* Reads light levels every 15 min.
* Adds a name and GPS coordinates you give it.
* Sends the data through a long‑range radio to the school’s computer.
* Home Assistant pulls the data and shows the results on a map.

### Quick steps for the class
1. **Assemble** – follow the wiring diagram in *ASSEMBLY.md*.
2. **Upload firmware** – copy `src/firmware/firmware.py` and `src/firmware/lorawan.py` to the Pico.
3. **Give it a name & place** – run `python SETUP.PY <name> <lat> <lon>` on the laptop.
4. **Deploy** – attach it to a tree or pole, plug in the battery.
5. **Check Home Assistant** – look at the map card.
6. **Talk about the numbers** – compare dark spots vs bright spots.
7. **Write a short report** – what did you learn about light pollution?

### The Code – what you *don't* need to touch
`src/firmware/firmware.py` is a tiny MicroPython script that:
* Loads the device name, latitude and longitude from `config.json`.
* Reads the light sensor on GP2 every 15 min.
* Builds a JSON payload and sends it via the LoRa helper.

Below you’ll find a **Tech Deep Dive** section with extra details that might interest the curious.

---
## Tech Deep Dive

### LoRa communication
The RFM95 module is controlled over SPI. It has a *write* command, a *read* command and an IRQ pin (DIO0). The helper `lorawan.LoRa.send()` writes the packet to the radio, requests transmission and waits until DIO0 goes high before returning. Teens only need to know that `send()` finishes when the packet leaves the module.

### ADC conversion to Lux
The TEMT6000 gives an analog voltage. The Pico’s 16‑bit ADC returns a value between 0 and 65535. The code scales this to a lux figure with:
```
lux = raw * (3.3 / 65535) * 1000
```
The factor *1000* is a simple linear conversion – good enough for relative brightness comparisons.

### JSON payload on the radio
Example payload:
```
{ "name": "East‑Tree", "lat": 43.586, "lon": 1.226, "lux": 120, "ts": 1690000000 }
```
All fields are strings or numbers. The timestamp (`int(time.time())`) tells Home Assistant how fresh the data is.

### Home Assistant side
The LoRa‑to‑MQTT container publishes frames to the topic `lightpol/+/data`. In Home Assistant a *Map* card can display the last measurement time and light level for each unit. No extra coding is needed on the server – just use the Docker stack defined in `SERVER.md`.

### Why Python and MicroPython?
MicroPython runs on the Pico, is cheap and easy to learn. The syntax looks a lot like normal Python, so students who have started with high‑level languages can pick it up quickly.

---
**Happy measuring, future data scientists!**

*** End of guide ***
