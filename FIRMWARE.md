# Firmware – MicroPython for the Light‑Pollution Monitor
The firmware runs on a Raspberry Pi Pico and uses the following components:
* **ADC** on **GP2** to read from the TEMT6000.
* **LoRa RFM95** over **SPI0** (MOSI GP15, MISO GP14, SCK GP13, NSS GP18, DIO0 GP18, RESET GP10).
* **config.json** stored in the Pico’s internal flash (updated with `SETUP.PY`).

## 1. File structure
```
- src/firmware/
   |-- firmware.py   # Main loop that you will copy to the Pico
   |-- lorawan.py    # LoRa helper
   |-- config.json   # Unit configuration (template below)
```
Copy the two Python files to the Pico’s filesystem and keep `config.json` on the Pi to edit with `SETUP.PY`.

## 2. `config.json` template
```json
{
  "name": "unit‑example",
  "lat": 43.58,
  "lon": 123.45,
  "poll_interval": 900  # optional, seconds between measurements
}
```
Run `python SETUP.PY <name> <lat> <lon>` to generate a real configuration file that the device will read on boot.
