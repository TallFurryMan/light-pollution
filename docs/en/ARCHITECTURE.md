---
lang: en
layout: single
title: "Architecture"
permalink: /en/architecture
translation_reference: architecture
nav_order: 6
nav_label: "Architecture"
---

# Project Architecture

## Classroom view

![Classroom overview](../images/classroom-flow.svg){: .lp-diagram }

The core flow is simple:

1. A sensor node measures light.
2. Radio sends the measurement to the gateway.
3. The gateway forwards data into the software stack.
4. Home Assistant shows the map and InfluxDB keeps the history.

## Real technical stack

![Software stack](../images/software-stack.svg){: .lp-diagram }

The Docker stack in this repository contains:

- ChirpStack for the radio network layer.
- Mosquitto for MQTT transport.
- Home Assistant for the classroom dashboard.
- InfluxDB for long-term history.

## Useful classroom payload

```json
{
  "name": "school-yard-01",
  "latitude": 48.2167,
  "longitude": -1.6986,
  "lux": 123,
  "ts": 1690000000,
  "charger_type": "CN3065",
  "charger_status": "unknown"
}
```

## Design choices after the review

- One default radio region: EU868.
- One main light sensor: TSL2591X.
- One simple student workflow: pre-flashed kits.
- One recommended gateway path: host machine plus SX1303 868 MHz hat.

## Known boundary

<div class="lp-note">
  <p>The repository has been cleaned up around the current Pico-based node path. The Pi Zero 2W plus SX1262 hat variant is documented as a future hardware option, but it is not yet delivered as a ready-to-run node implementation.</p>
  <p>Full protocol alignment between the node firmware and the ChirpStack/LoRaWAN server path is still the next technical milestone.</p>
</div>
