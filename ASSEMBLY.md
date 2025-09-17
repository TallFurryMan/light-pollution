# Step‑by‑Step Assembly Guide
This guide walks you through building a **Light‑Pollution Monitor** from the parts list. All you need is a soldering iron and a small multimeter.

## 1. Prepare the breadboard
1. Insert the **Raspberry Pi Pico** into the breadboard, aligning the headers with the rails.
2. Connect **GND** of Pico to the common ground rail.
3. Hook the **3.3 V** of Pico to the positive rail.

## 2. Light sensor wiring
1. Place the **TEMT6000** close to a **C‑shaped** board so you can see the light.
2. Connect:
   * **VCC** → 3.3 V rail.
   * **GND** → GND rail.
   * **OUT** → **GP2** (ADC0) on Pico.
3. Add a 10 µF capacitor between VCC and GND close to the sensor for stability.

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

