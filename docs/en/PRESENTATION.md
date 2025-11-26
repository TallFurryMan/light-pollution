---
# Light‑Pollution Monitoring Project

## Overview
* **Goal** – Build a network of small, autonomous *Light‑Pollution Monitors* that collect night‑time lux data, upload to Home Assistant, and show results on a map.
* **Audience** – 12‑14 year old students working in teams.
* **Why it matters** – Light pollution harms ecosystems, disturbs sleep, and hides the stars. Measuring it teaches data, networking, and environmental stewardship.

## Project Deliverables
1. **Hardware** – Low‑cost kit: Pico, light sensor, LoRa radio, battery.
2. **Assembly guide** – Step‑by‑step with minimal tools.
3. **Firmware** – MicroPython (`src/firmware`): read sensor, add name/GPS, send via LoRa.
4. **Server setup** – Docker stack: Home Assistant, Mosquitto, LoRa‑MQTT bridge, InfluxDB.
5. **Documentation** – Clear, friendly guides for kids and teachers.

## Classroom Workflow
1. Form teams of 3‑4.
2. Assemble following `docs/ASSEMBLY.md`.
3. Flash firmware (Micropython + rshell/REPL).
4. Set name/location with `SETUP.PY`.
5. Deploy outdoors (tree/roof) with Li‑Po power.
6. View data on HA map / InfluxDB history.
7. Discuss patterns and ways to reduce light pollution.

## Success Criteria
- One reading every 15 minutes.
- HA map shows name, last reading, and timestamp.
- Students can explain the data flow from sensor to cloud.
