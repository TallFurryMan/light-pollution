---
lang: en
layout: single
title: "Hardware"
permalink: /en/hardware
translation_reference: hardware
---
## Bill of Materials
You’ll [assemble]({{ site.baseurl }}{% link en/ASSEMBLY.md %}) the following:
- Raspberry Pi Pico
- LoRa module (SX1262 Pico HAT, or SX127x)
- Light sensor (TSL2591, TEMT6000, or BH1750)
- Li‑Po battery + charger (CN3065, MCP73871, or TP4056)
- 3.3 V regulator, decoupling caps
- JST XMX 2.54mm and/or PH 2.0mm cables, or Dupont
- Enclosure

![Raspberry Pi Pico](../images/rasp_pico.png)

![Waveshare SX1262 HAT](../images/sx1262.png)

![TSL2591 sensor](../images/tsl2591.png)

![CN3065 solar charger](../images/cn3065.png)

## Gateway (Raspberry Pi)
- LoRa concentrator (Waveshare SX1303 HAT or SX1302/1303 USB stick).
- Mosquitto + ChirpStack + Home Assistant + InfluxDB (docker-compose provided).

![SX1303 Gateway HAT](../images/sx1303.png)

## Tips
- Keep SPI traces short for the LoRa module.
- Common ground and nearby decoupling for sensors and radio.
- Use connectors to swap sensors or LoRa modules easily.
