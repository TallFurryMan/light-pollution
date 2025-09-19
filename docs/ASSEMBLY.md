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

## 3.1 RFM95 - 433MHz/945MHz LoRa module
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

## 3.2 SX1278 – 868 MHz LoRa module
If you are using an **SX1278** instead of the RFM95, the wiring is nearly the same but requires different control pins. Follow the diagram below and update the firmware configuration accordingly.

```markdown
![SX1278 LoRa board](https://cdn.shopify.com/s/files/1/0208/5938/files/LoRaSX1278.jpg?width=600)
```

**Connection table**
```
Pico (3.3 V)
│   ──> 3.3 V regulator
│
├─ VCC            ──> 3.3 V
├─ GND            ──> GND
├─ SPI0 SCK       ──> GP13
├─ SPI0 MOSI      ──> GP15
├─ SPI0 MISO      ──> GP14
├─ NSS (CS)       ──> GP17
├─ DIO0 (IRQ)     ──> GP16
└─ RESET           ──> GP18
```

* **Keep the SPI traces short** – the SX1278 runs at 3 MHz and is sensitive to long wires on the MOSI/MISO lines.
* **Decouple** the VCC pin with a 100 nF capacitor across VCC‑GND near the module.

### Firmware configuration
The firmware reads the `lora_chip` key in `config.json` to pick the correct chip. Add

```json
{ "lora_chip": "SX1278", … }
```

to the configuration file. The updated firmware will automatically use the 868 MHz frequency and register defaults for the SX1278.

## 4. Power supply
1. Connect the **Li‑Po charger** to the battery. Use a 4‑cell pack (4.2 V). The charger will output 3.3 V.
2. Feed the 3.3 V output to the regulator input. Tie the regulator GND to the common rail.
3. Verify with a multimeter: **3.3 V** at the regulator output.

## 5. Optional solar power
The kit can be powered from a small solar panel through one of two charger chips.

### 5.1 Choose a charger chip
* **MCP73871** – I²C status interface, suitable for USB‑to‑LiPo charging.
* **TP4056** – Simple linear charger, no status lines.

### 5.2 Solar panel wiring
1. Connect the panel’s positive lead to the charger’s **VIN** input.
2. Connect the negative lead to the charger’s **GND**.
3. The charger outputs a regulated 4.2 V ready for the battery.
4. The output of the charger then feeds the 3.3 V regulator the same way the
   PCB charger does.  Keep cables short and use a 100 nF capacitor across
   the charger output.
5. If you use the MCP73871, you can monitor its status via I²C.

### 5.3 Assembly tip
The solar panel can be mounted on the top of the enclosure.  If the panel
receives light, the charger will automatically begin charging the battery
without needing any extra wiring from the Pico.  The Pico has no dedicated
solar‐input pins, it only cares about the regulated 3.3 V rail.

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
