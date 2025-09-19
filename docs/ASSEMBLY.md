---
# Step‑by‑Step Assembly Guide
This guide walks you through building a **Light‑Pollution Monitor** from the parts list. All you need is a soldering iron and a small multimeter.

## 1. Prepare the breadboard
1. Insert the **Raspberry Pi Pico** into the breadboard, aligning the headers with the rails.
2. Connect **GND** of Pico to the common ground rail.
3. Hook the **3.3 V** of Pico to the positive rail.

## 2. Light sensor wiring
The firmware now supports three different light sensors.  Pick the one that
best matches your low‑light requirement and power budget.  All sensors are
powered from the 3.3 V rail and share the same ground rail.  The Pico must
be able to read the output using a suitable pin.

### 2.1 TEMT6000 – cheap analog photodiode
* **Description**: Single‑channel photodiode with linear output proportional
  to light intensity.  Works best in the 100–100 000 lux range.
* **Connection**:
  * **VCC** → 3.3 V rail
  * **GND** → GND rail
  * **OUT** → **GP2** (ADC0) on Pico
* **Notes**: Place a 10 µF electrolytic capacitor between VCC and GND near
  the sensor for stability.

```markdown
![TEMT6000](https://cdn.shopify.com/s/files/1/0208/5938/files/TEMT6000.jpg?width=600)
```

### 2.2 TSL2591 – high‑sensitivity I²C lux meter
* **Description**: Digital lux meter with programmable gain and integration
  time.  Good for low‑light environments and provides a lux value directly.
* **Connection**:
  * **VCC** → 3.3 V rail
  * **GND** → GND rail
  * **SCL** → **GP5** (I²C SCL)
  * **SDA** → **GP4** (I²C SDA)
  * **ADDR** → leave pull‑ups high (default address 0x29)
* **Notes**: I²C uses the Pico’s dedicated I²C bus; no extra pins are
  required.

```markdown
![TSL2591](https://cdn-shop.adafruit.com/1200x1200/2835-01.jpg)
```

### 2.3 BH1750 – digital lux sensor
* **Description**: I²C digital lux sensor that outputs a 16‑bit lux value.
* **Connection**:
  * **VCC** → 3.3 V rail
  * **GND** → GND rail
  * **SCL** → **GP5** (I²C SCL)
  * **SDA** → **GP4** (I²C SDA)
  * **ADDR** → leave pull‑ups high (default address 0x23)
* **Notes**: Use the same I²C lines as the TSL2591 – just change the
  address in the firmware or add a level‑shifter if needed.

```markdown
![BH1750](https://cdn-shop.adafruit.com/1200x1200/2837-01.jpg)
```

---
**Optional** – When assembling on a small breadboard, use a dedicated
header row for each sensor so that you can simply plug the sensor in and
cut the leads later.  Keep the header pins in a separate row to avoid
crosstalk and reduce the chance of soldering the main board.

## 3. LoRa module wiring
1. Put the **RFM95** on the board. It has a 6‑pin pitch; use the jumper wires.
2. Wire as follows:
   * **VCC** → 3.3 V rail.
   * **GND** → GND rail.
   * **NSS** → **GP18** (use this as the CS line). If you want to change later, use a header.
   * **SCK** → **GP13**.
   * **MISO** → **GP14**.
   * **MOSI** → **GP15**.
   * **RESET** → **GP10** (optional, can be tied to 3.3 V if unused).
   * **DIO0** → **GP18** (shared with NSS) – used for IRQ.
3. Add a decoupling capacitor (100 nF) across VCC‑GND near the LoRa.

## 4. Power supply
1. Connect the **Li‑Po charger** to the battery. Use a 4‑cell pack (4.2 V). The charger will output 3.3 V.
2. Feed the 3.3 V output to the regulator input. Tie the regulator GND to the common rail.
3. Verify with a multimeter: **3.3 V** at the regulator output.

## 5. Enclosure
1. Drill a hole for the **LoRa antenna** – a simple wire or the antenna built‑in to the breakout.
2. Mount the board so that GP2 (light sensor) is as exposed as possible; shield the rest.
3. Seal gaps with epoxy or silicone to protect against rain.

## 6. Final checks
* Power on the Raspberry Pi Pico with a USB‑to‑serial adapter; the REPL should start.
* Open the REPL and type `import sys; print(sys.version)` to confirm MicroPython is working.
* Verify ADC reading:
  ```python
  from machine import ADC, Pin
  adc = ADC(Pin(2))
  print(adc.read_u16())
  ```
* Test LoRa transmission locally with the sample script (see `FIRMWARE.md`).

Congratulations – the hardware is ready for code!
