---
lang: en
layout: single
title: "Architecture"
permalink: /en/architecture
translation_reference: architecture
---
## 1. Overview
The project has three layers:

| Layer | Components | Communication | Purpose |
|-------|------------|---------------|---------|
| **Device** | Raspberry Pi Pico, LoRa SX127x/SX1262, light sensor (TEMT6000, TSL2591, BH1750), Li‑Po battery | LoRa | Local sensing and low‑power TX |
| **Gateway** | Raspberry Pi with LoRa‑MQTT bridge + Mosquitto | LoRa ➜ MQTT | Bridge between sensor and server |
| **Server** | Home Assistant (+ InfluxDB) | MQTT | Store, process, visualize |

## 2. Device Flow
1. Pico reads name/GPS from `config.json`.
2. Every 15 minutes: read lux.
3. Payload: `{"name":"unit-1","latitude":48.2167,"longitude":-1.6986,"lux":120,"ts":1690000000}`.
4. Send via LoRa.

## 3. Gateway & Server
- LoRa‑MQTT bridge publishes JSON to Mosquitto.
- Home Assistant subscribes, creates entities via discovery, shows on map.
- InfluxDB stores full history.

## 4. Data Model
```json
{
  "name": "string",
  "latitude": 48.2167,
  "longitude": -1.6986,
  "lux": 123,
  "ts": 1690000000
}
```

## 5. Reliability
- LoRa frames with CRC; gateway verifies before forwarding.
- Minimal config cached so the node can restart autonomously.
