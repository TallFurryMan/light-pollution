# Hardware Design – Light‑Pollution Monitor (Pico + LoRa)
## 1. Bill of Materials (BOM)
| Part | Qty | Notes |
|------|-----|-------|
| Raspberry Pi Pico | 1 | Main microcontroller |
| RFM95W LoRa breakout (433 MHz or 915 MHz) | 1 | 8‑bit SPI interface, 4‑pin header |
| TEMT6000 light sensor (photodiode) | 1 | Analog output, low‑cost |
| 2.5 V to 3.3 V regulator (e.g. AMS1117‑3.3) | 1 | Power sensor and sensor pin |
| 4‑cell Li‑Po battery + charger module (MCP73831) | 1 | 4.2 V full charge |
| 10 µF and 100 nF capacitors | 2 | Decoupling |
| 3.3 V level‑shifter (BSS138) | 2 | For LoRa pins if not 3.3 V only |
| Breadboard + jumper wires | 1 | For prototyping |
| Enclosure (3‑D printed) | 1 | Waterproof, small footprint |
| Optional: 3‑pin connector for future GPS module |
## 2. Wiring Diagram
```
   Pico (3.3 V) ──> 3.3 V regulator ──> RFM95 (VCC)
   GND ──> GND (common)
   GP2 (ADC0) ──> TEMT6000 OUT
   GP15 (SPI0 MOSI) ──> RFM95 MOSI
   GP14 (SPI0 MISO) ──> RFM95 MISO
   GP13 (SPI0 SCK) ──> RFM95 SCK
   GP18 (GPIO) ──> RFM95 NSS (DIO0 for IRQ)
   Optional: GP10 (GPIO) ──> RFM95 RESET
```
Make sure to tie the sensor VCC to the 3.3 V regulator, not the Pi’s 3.3 V line.
## 3. Power Consumption
| State | Current (mA) |
|-------|--------------|
| Idle | ~15 |
| LoRa TX | 40‑50 (depends on power‑amplifier) |
| Light Sensor | <1 |
---
With 15 mA idle and a 15 min measurement interval, a single **4‑cell Li‑Po** (~2500 mAh) will last roughly 4–5 months.
## 4. Assembly Tips
* **Breadboard first** – Build the circuit on a breadboard to test every connection.
* **Keep SPI traces short** – LoRa modules are sensitive to long wires.
* **Ground‑plane** – Use the back of the enclosure or a copper sheet to ensure a common ground.
* **Use DIP‑switch or header** – For the LoRa NSS pin, so you can change it without soldering.

