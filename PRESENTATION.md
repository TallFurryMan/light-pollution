# Light‑Pollution Monitoring Project
## Overview
* **Goal** – Build a network of small, autonomous *Light‑Pollution Monitors* that collect night‑time lux data across a village, upload the data to a Home Assistant server, and present the results on a map.
* **Audience** – 12‑14 year old students in France’s 3ème, working in class groups.
* **Why it matters** – Light pollution harms ecosystems, disturbs human sleep, and reduces our view of the stars. By measuring it, we learn about data collection, networking, and environmental stewardship.
## Project Deliverables
1. **Hardware** – A simple, low‑cost kit based on a Raspberry Pi Pico, a light sensor, a LoRa radio, and a battery.
2. **Assembly guide** – Step‑by‑step instructions that can be followed with minimal tools.
3. **Firmware** – MicroPython code that reads the sensor, adds a friendly name and GPS coordinates, and sends the data via LoRa.
   The code lives in the `src/firmware` directory:
   * `firmware.py` – main loop.
   * `lorawan.py` – helper for the LoRa module.
4. **Server setup** – A Docker‑based Home Assistant stack with an MQTT broker and LoRa‑to‑MQTT gateway.
5. **Documentation** – All the above in Markdown with clear, friendly explanations for kids.
## Classroom Workflow
1. **Group formation** – Students split into teams of 3‑4.
2. **Hardware assembly** – Follow `ASSEMBLY.md`.
3. **Firmware upload** – Use `micropython` and `rshell` or the built‑in REPL.
4. **Configure name/location** – Run the supplied `SETUP.PY` script on a laptop.
5. **Deploy** – Attach each unit to a tree or rooftop, power with a 4‑cell Li‑Po.
6. **Data collection** – Observe weekly data in Home Assistant’s map UI.
7. **Discussion** – Analyze patterns, compare locations, and propose mitigation ideas.
## Success Criteria
- Each unit reports at least once every 15 minutes.
- Data is displayed on a Home Assistant map with unit name, last‑seen timestamp, and last sensor reading.
- Students can explain the data flow from sensor to cloud.
**All done!**
