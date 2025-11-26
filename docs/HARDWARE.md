# Hardware Design – Light‑Pollution Monitor (Pico + LoRa)

## 1. Bill of Materials (BOM)
| Part | Qty | Notes |
|------|-----|-------|
| Raspberry Pi Pico | 1 | Main microcontroller |
| RFM95W LoRa breakout (433 MHz or 915 MHz) | 1 | 8‑bit SPI interface, 4‑pin header |
| SX1278 LoRa breakout (868 MHz) | 1 | 8‑bit SPI interface, 4‑pin header |
| Waveshare SX1262 868 MHz Pico HAT | 1 | Preferred Pico LoRa HAT (SX1262) |
| TEMT6000 light sensor (photodiode) | 1 | Analog output, low‑cost |
| TSL2591 high‑sensitivity I²C lux meter | 1 | Digital, low‑light performance |
| BH1750 digital lux sensor | 1 | Digital, simple I²C interface |
| 2.5 V to 3.3 V regulator (e.g. AMS1117‑3.3) | 1 | Power sensor and sensor pin |
| 4‑cell Li‑Po battery + charger module (MCP73831) | 1 | 4.2 V full charge |
| Battery charger MCP73871 (USB‑to‑LiPo) | 1 | I²C status, 4‑cell Li‑Po 4.2 V | 
| TP4056 Li‑Po charger | 1 | Simple linear charger, 4.2 V output |
| Small solar panel 5 V 1 W | 1 | Adafruit 5 V 1W solar panel |
| Small solar panel 5 V 2.4 W | 1 | Adafruit 5 V 2.4 W solar panel |
| 10 µF and 100 nF capacitors | 2 | Decoupling |
| 3.3 V level‑shifter (BSS138) | 2 | For LoRa pins if not 3.3 V only |
| Breadboard + jumper wires | 1 | For prototyping |
| Enclosure (3‑D printed) | 1 | Waterproof, small footprint |
| Optional: 3‑pin connector for future GPS module |

### Gateway Hardware (Home Assistant / Raspberry Pi)
Use a LoRa concentrator that runs the Semtech packet forwarder; suggested options:
- **Waveshare SX1303 LoRaWAN HAT for Raspberry Pi** – SX1303 concentrator, SPI; supported by Semtech UDP forwarder/ChirpStack.
- **RAK7271 / RAK7371 (SX1302/SX1303 USB stick)** – EU868/US915; known‑good with `sx1302_hal`.
- **Seeed WM1302 on USB carrier** – SX1302, EU868/US915 variants.
- **iC880A-SPI on USB/SPI bridge** – legacy SX1301 but widely supported.

These connect to the Home Assistant Raspberry Pi and feed ChirpStack or the gateway bridge in the compose stack. Pico sensor units should use the SX1262 HAT (or an ESP-based SX1262 module for a future variant) and do not translate LoRa to RS485/CAN.

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
* **Breadboard first** – Build the circuit on a breadboard to test every
  connection.
* **Keep SPI traces short** – LoRa modules are sensitive to long wires.
* **Ground‑plane** – Use the back of the enclosure or a copper sheet to
  ensure a common ground.
* **Use DIP‑switch or header** – For the LoRa NSS pin, so you can change it without soldering.
