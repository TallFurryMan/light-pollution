---
lang: en
layout: single
title: "Hardware"
permalink: /en/hardware
translation_reference: hardware
nav_order: 4
nav_label: "Hardware"
---

# Reference Hardware

## Current supported profile in the repository

| Item | Practical reference | Status |
|------|---------------------|--------|
| Node controller | Raspberry Pi Pico | Current software path |
| Node radio | Waveshare Pico-LoRa-SX1262-868M | Default firmware profile |
| Light sensor | TSL2591X | Supported |
| Solar charging | CN3065 + panel + 3.7 V LiPo | Documented power chain |
| Gateway | Raspberry Pi 4/5 or LattePanda v1 + SX1303 868 MHz | Recommended target |

## Parts bought for the next activity

- SX1303 868 MHz gateway hat.
- SX1262 868 MHz radio hat.
- TSL2591X sensors.
- CN3065 solar chargers.
- Solar panels.
- 3.7 V LiPo batteries.
- Raspberry Pi Zero 2W.

## Why this matters

- The project now documents one default radio region: EU868.
- The TSL2591X is the main classroom light sensor.
- The CN3065 plus LiPo path is the intended solar charging chain for low-power nodes.
- The Pi Zero 2W variant is treated as a future hardware path, not as a claimed ready-made implementation.

## Power warning

<div class="lp-note">
  <p>A Pico-based node fits a simpler low-power chain than a Pi Zero 2W.</p>
  <p>A Pi Zero 2W needs regulated 5 V. A 3.7 V LiPo and a CN3065 charger are not enough by themselves; a boost stage or a dedicated power board is required.</p>
</div>
