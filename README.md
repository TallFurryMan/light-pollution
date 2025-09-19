Light‑Pollution Monitor Project
===============================

The **Light‑Pollution Monitor** is a hands‑on learning kit that turns a
Raspberry Pi Pico into a tiny data‑collection node.  Students assemble the
hardware, write or copy the firmware, give each unit a name and location and
watch the data appear on a Home Assistant map.

This repository contains:

* **Presentation** – overview and success criteria (`docs/PRESENTATION.md`).
* **Architecture** – system architecture diagram and data flow (`docs/ARCHITECTURE.md`).
* **Kids** – classroom‑ready guide (`docs/KIDS.md`).
* **Assembly** – detailed wiring and build instructions (`docs/ASSEMBLY.md`).
* **Hardware** – bill of materials and layout guidance (`docs/HARDWARE.md`).
* **Firmware** – MicroPython source (`src/firmware/`).

## Quick start
```bash
# 1. Flash the firmware onto a Pico
rshell -p /dev/ttyUSB0 -e "mkdir firmware && cp src/firmware/*.py firmware/"
# 2. Configure the unit
python SETUP.PY unit‑1 43.58 1.23
# 3. Attach the hardware and power it on.
```

## Documentation
All Markdown documentation lives in the **docs** directory.  For a
full‑page view you can run the lightweight web server below.

```bash
python serve_docs.py
```

Open `http://localhost:8000` in a browser.
