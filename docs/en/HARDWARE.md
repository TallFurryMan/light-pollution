---
# Hardware

## Bill of Materials
- Raspberry Pi Pico
- LoRa module (SX127x or SX1262 Pico HAT)
- Light sensor (TEMT6000 / TSL2591 / BH1750)
- Li‑Po battery + charger (MCP73871 or TP4056)
- 3.3 V regulator, decoupling caps
- Dupont wires/breadboard, enclosure

## Gateway (Raspberry Pi)
- LoRa concentrator (Waveshare SX1303 HAT or SX1302/1303 USB stick).
- Docker stack: Mosquitto, ChirpStack, Home Assistant, InfluxDB.

## Tips
- Keep SPI traces short.
- Common ground and local decoupling for sensors and radio.
- Use headers/connectors to swap sensors or LoRa modules easily.
