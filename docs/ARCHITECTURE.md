---
# System Architecture

## 1. Overview

**Architecture Diagram**

<svg width="400" height="150" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="40" width="100" height="70" stroke="black" fill="white"/>
  <text x="70" y="55" font-size="12" text-anchor="middle">Device</text>
  <text x="70" y="75" font-size="10" text-anchor="middle">Pico</text>
  <rect x="150" y="40" width="100" height="70" stroke="black" fill="white"/>
  <text x="200" y="55" font-size="12" text-anchor="middle">Gateway</text>
  <text x="200" y="75" font-size="10" text-anchor="middle">Raspberry Pi 4</text>
  <rect x="280" y="40" width="100" height="70" stroke="black" fill="white"/>
  <text x="330" y="55" font-size="12" text-anchor="middle">Cloud</text>
  <text x="330" y="75" font-size="10" text-anchor="middle">Home Assistant</text>
  <line x1="120" y1="75" x2="140" y2="75" stroke="black" marker-end="url(#arrow)"/>
  <line x1="250" y1="75" x2="270" y2="75" stroke="black" marker-end="url(#arrow)"/>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="black"/>
    </marker>
  </defs>
  <text x="130" y="65" font-size="10" text-anchor="middle">LoRa</text>
  <text x="260" y="65" font-size="10" text-anchor="middle">MQTT</text>
</svg>

The project is split into three major layers:
| Layer | Components | Communication | Purpose |
|-------|------------|---------------|---------|
| **Device** | Raspberry Pi Pico, LoRa RFM95/SX1278, Light sensor (TEMT6000, TSL2591, BH1750), 4‑cell Li‑Po battery | LoRa | Local data acquisition & power‑efficient transmission |
| **Gateway** | Raspberry Pi 4 with **LoRa‑to‑MQTT** container and Mosquitto broker | LoRa ➜ MQTT | Bridge between sensor and cloud |
| **Cloud** | Home Assistant container | MQTT | Store, process and visualize data |

## 2. Device Flow
1. Pico boots → reads GPS name/coordinates from NVM.
2. Every **15 min** an ADC reading is taken.
3. Payload format: `{"name":"unit‑1","lat":43.58,"lon":1.23,"lux":120,"ts":1690000000}`.
4. Payload is transmitted via LoRa.
5. At the gateway, a tiny script (or a container) parses payload, forwards to the MQTT broker.

## 3. Gateway & Server
- **LoRa‑to‑MQTT bridge** – Runs as a Docker container (see `SERVER.md`). It listens on the LoRa interface (e.g. `/dev/spidev0.0`) and forwards raw payloads as JSON over MQTT.
- **Home Assistant** – Subscribes to topic `lightpol/+/data`, stores the latest reading in a sensor and shows an `entity_picture` on the map.

## 4. Data Model
```json
{
  "name": "string",
  "lat": 45.8,
  "lon": 2.30,
  "lux": 123,
  "ts": 1690000000
}
```

All values are transmitted as a compact Base64 string to save bandwidth.

## 5. Security & Reliability
- LoRa uses **8‑bit CRC** by default; the bridge verifies it before forwarding.
- The device stores **last‑known good configuration** in flash; if the LoRa link is lost the device keeps sending until it receives acknowledgement.
