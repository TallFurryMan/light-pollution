# System Architecture
## 1. Overview
The project is split into three major layers:
| Layer | Components | Communication | Purpose |
|-------|------------|---------------|---------|
| **Device** | *Raspberry Pi Pico*, *LoRa RFM95*, *Light sensor* (TEMT6000, TSL2591 or BH1750), 4‑cell Li‑Po battery | LoRa | Local data acquisition & power‑efficient transmission |
   Firmware source: `src/firmware/*.py`
| **Gateway** | Raspberry Pi 4 with **LoRa gateway Hat** (or RFM95 in a *“LoRa‑to‑MQTT”* container) and **Docker** homeassistant | LoRa ➜ MQTT | Bridge between sensor and cloud |
| **Cloud** | Home Assistant container running on the same Raspberry‑Pi 4, exposed via `mqtt://` endpoint | MQTT | Store, process and visualize data |
## 2. Device Flow
1. Pico boots → reads GPS name/coordinates from NVM.
2. Every **15 min** an ADC reading is taken.
3. Payload format: `{"name":"unit‑1","lat":43.58,"lon":1.23,"lux":120,"ts":1690000000}`.
4. Payload is signed (optional) and transmitted via LoRa.
5. At the gateway, a tiny script (or a container) parses payload, forwards to the MQTT broker.
## 3. Gateway & Server
- **LoRa‑to‑MQTT bridge** – Runs as a Docker container (see `SERVER.md`). It listens on the LoRa interface (e.g. `/dev/spidev0.0`) and forwards raw payloads as JSON over MQTT.
- **Home Assistant** – Subscribes to topic `lightpol/+/data`, stores the latest reading in a sensor and shows an `entity_picture` on the map.
## 4. Data Model
```json
{
  "name": "string",   // friendly unit name
  "lat":   45.8,       // latitude
  "lon":   2.30,       // longitude
  "lux":  123,         // illuminance in lux
  "ts":   1690000000   // Unix timestamp
}
```
All values are transmitted as a compact Base64 string to save bandwidth.
## 5. Security & Reliability
- LoRa uses **8‑bit CRC** by default; the bridge verifies it before forwarding.
- The device stores **last‑known good configuration** in flash; if the LoRa link is lost the device keeps sending until it receives acknowledgement.
---
**Key takeaway** – The kids work on the *device* layer; the gateway and Home Assistant configuration are pre‑built and only require a quick copy/paste.
