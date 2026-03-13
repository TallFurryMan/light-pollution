---
lang: en
layout: single
title: "Teachers"
permalink: /en/teachers
translation_reference: teachers
nav_order: 3
nav_label: "Teachers"
---

# Teacher Guide

## Reference workshop kit

- Current repo node: Raspberry Pi Pico + SX1262 868 MHz radio + TSL2591 sensor + pre-flashed firmware.
- Light sensor target: TSL2591X over I2C.
- Power target: CN3065 solar charger + 3.7 V LiPo.
- Gateway target: Raspberry Pi 4/5 or LattePanda v1 + SX1303 868 MHz gateway hat.

## Before class

1. Assemble or prepare the kits.
2. Confirm that one kit publishes a test measurement.
3. Pre-configure name and coordinates with `SETUP.PY`.
4. Prepare a map of observation locations around the school.
5. Decide which groups compare dark, bright, and mixed locations.

## Provision a pre-flashed kit

```bash
python3 SETUP.PY school-yard-01 48.2167 -1.6986 --port /dev/ttyACM0
```

The script writes `config.json` to the node and stores:

- the kit name
- latitude and longitude
- the board profile
- the sensor type
- the charger type
- the measurement interval

Use `--dry-run` to inspect the payload before writing it.

## During class

1. Hand out the kits and explain safety rules.
2. Assign each group a precise observation point.
3. Let students place the node and watch the map.
4. Ask for a hypothesis before comparing group results.
5. End with a discussion about lighting choices and their impact.

## Important note about the next Pi Zero 2W variant

<div class="lp-note">
  <p>The SX1262 HAT plus a Pi Zero 2W is a good future direction, but that node path is not yet implemented in this repository.</p>
  <p>It also still needs both a node-side software path aligned with ChirpStack/LoRaWAN and regulated 5 V power. A CN3065 board and a single LiPo cell are not enough on their own for a Pi Zero 2W node.</p>
</div>
