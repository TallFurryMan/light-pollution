---
---
lang: en
layout: single
title: "Step-by-Step Assembly"
---
# Step‑by‑Step Assembly

## 1. Prep the breadboard
1. Insert **Raspberry Pi Pico**.
2. GND to ground rail, 3.3 V to positive rail.

## 2. Light sensor wiring
Pick the sensor you need.

### TEMT6000 (analog)
- OUT → **GP2** (ADC0), VCC 3.3 V, GND.
- Add 10 µF cap between VCC/GND near the sensor.

### TSL2591 (I²C)
- SCL → **GP5**, SDA → **GP4**, VCC 3.3 V, GND.
- Address 0x29 by default.

### BH1750 (I²C)
- SCL → **GP5**, SDA → **GP4**, VCC 3.3 V, GND.
- Address 0x23 by default.

## 3. LoRa module
- SPI0: SCK GP13, MOSI GP15, MISO GP14.
- CS/NSS: GP18 (default).
- DIO0 IRQ: GP18 (or per module).
- RESET: GP10 optional.
- Decouple VCC with 100 nF near the module.

## 4. Power
- Li‑Po + charger (MCP73871/TP4056), regulator 3.3 V to Pico/sensors.
- Verify 3.3 V before connecting.
