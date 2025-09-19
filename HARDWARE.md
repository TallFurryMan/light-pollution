# Hardware Design – Light‑Pollution Monitor (Pico + LoRa)
## 1. Bill of Materials (BOM)
| Part | Qty | Notes |
|------|-----|-------|
| Raspberry Pi Pico | 1 | Main microcontroller |
| RFM95W LoRa breakout (433 MHz or 915 MHz) | 1 | 8‑bit SPI interface, 4‑pin header |
| SX1278 LoRa breakout (868 MHz) | 1 | 8‑bit SPI interface, 4‑pin header |
| TEMT6000 light sensor (photodiode) | 1 | Analog output, low‑cost |
| TSL2591 high‑sensitivity I²C lux meter | 1 | Digital, low‑light performance |
| BH1750 digital lux sensor | 1 | Digital, simple I²C interface |
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
   **For TEMT6000**
   GP2 (ADC0) ──> OUT
  **For I²C sensors (TSL2591, BH1750)**
  GP5 (I2C SCL) ──> SCL
  GP4 (I2C SDA) ──> SDA
  GP15 (SPI0 MOSI) ──> MOSI
  GP14 (SPI0 MISO) ──> MISO
  GP13 (SPI0 SCK) ──> SCK
  GP18 (GPIO) ──> NSS (DIO0 for IRQ)
  Optional: GP10 (GPIO) ──> RESET
```

**Additional lines for SX1278**
The SX1278 uses the same SPI signals (SCK, MOSI, MISO), but the GPIO
assignment is slightly different: the NSS pin is on GP17, DIO0 on GP16
and the RESET pin on GP18.  When using SX1278, replace the RFM95 wiring
below with:
```
GP17 (NSS) ──> NSS
GP16 (DIO0) ──> DIO0
GP18 (RESET) ──> RESET
```
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
