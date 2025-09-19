# SX1278 LoRa Module – Assembly & Setup
![LoRa SX1278 board](https://cdn.shopify.com/s/files/1/0208/5938/files/LoRaSX1278.jpg?width=600)
![LoRa SX1278 board](https://cdn.shopify.com/s/files/1/0208/5938/files/LoRaSX1278.jpg?width=600)

This guide shows how to wire and configure the SX1278 LoRa breakout so
that it works with the Light‑Pollution Monitor firmware.  The SX1278
provides 868 MHz operation with a similar register set to the RFM95.

## Wiring diagram
```
Pico (3.3 V)
│   ──> 3.3 V regulator
│
├─ RFM95/SX1278 VCC  ──> 3.3 V
├─ GND            ──> GND
├─ SPI0 SCK        ──> GP13
├─ SPI0 MOSI       ──> GP15
├─ SPI0 MISO       ──> GP14
├─ NSS (CS)        ──> GP17
├─ DIO0 (IRQ)      ──> GP16
└─ RESET           ──> GP18
```

> **Tip:**  Keep the SPI traces as short as possible; the SX1278 is a
> 3‑MHz device and is sensitive to long wires on the MOSI/MISO
> lines.

## Configuration in firmware
The `config.json` file on the Pico has a new key, `lora_chip`, that
selects the chip at runtime:

```json
{ "lora_chip": "SX1278", … }
```

The firmware auto‑detects this value and initialises the LoRa helper
with the correct frequency (868 MHz) and register defaults.

## Software change
The firmware was updated to accept the `lora_chip` setting and pass
the value to the `LoRa` class.  No other code changes are required.

## Testing the connection
1. Flash the updated firmware to the Pico.
2. Power the SX1278 breakout and connect it as per the diagram.
3. Observe Home Assistant – a new MQTT topic
   `lightpol/<unit‑name>/data` should appear.
4. If data does not appear, run `python SETUP.PY <name> <lat> <lon>`
   again to ensure the configuration file has been written correctly.

---

Happy measuring! 🎉
