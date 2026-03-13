# Light Pollution Workshop

[French workshop docs](https://tallfurryman.github.io/light-pollution/fr/) | [English technical docs](https://tallfurryman.github.io/light-pollution/en/) | [GitHub Pages workflow](https://github.com/tallfurryman/light-pollution/actions/workflows/gh-pages.yml)

[![Stack Tests](https://github.com/tallfurryman/light-pollution/actions/workflows/stack-tests.yml/badge.svg)](https://github.com/tallfurryman/light-pollution/actions/workflows/stack-tests.yml)
[![Latest Release](https://img.shields.io/github/v/release/tallfurryman/light-pollution?include_prereleases&label=latest%20release)](https://github.com/tallfurryman/light-pollution/releases)
[![Docs](https://github.com/tallfurryman/light-pollution/actions/workflows/gh-pages.yml/badge.svg)](https://github.com/tallfurryman/light-pollution/actions/workflows/gh-pages.yml)

This repository supports a classroom activity for French middle-school students around light pollution, environmental sensing, and map-based interpretation of data.

## Current scope

- Current implemented node path: Raspberry Pi Pico + SX1262 + TSL2591, prepared as a pre-flashed classroom kit.
- Current server stack target: ChirpStack, Mosquitto MQTT, Home Assistant, InfluxDB, Redis, Postgres, and a gateway bridge.
- Current protocol status: the Pico reference firmware now joins ChirpStack over LoRaWAN OTAA and sends classroom measurements as encrypted application payloads.
- Current boundary: the Pi Zero 2W node variant remains a future hardware path and still needs its own power and software adaptation.
- Current documentation target: a clearer GitHub Pages site with separate student and teacher paths.

## Main files

| File | Purpose |
|------|---------|
| `src/docker-compose.yml` | Classroom stack with ChirpStack, MQTT, Home Assistant, and InfluxDB. |
| `src/configuration.yaml` | Home Assistant configuration, including the InfluxDB 2.x exporter settings. |
| `src/firmware/firmware.py` | MicroPython node firmware for the current Pico-based reference path. |
| `src/firmware/lorawan.py` | SX1262 radio driver plus the node-side LoRaWAN Class A implementation used by the Pico firmware. |
| `SETUP.PY` | Teacher provisioning tool for pre-flashed nodes. |
| `docs/` | GitHub Pages content in French and English. |

## Running the stack

```bash
docker compose -f src/docker-compose.yml up -d
```

Main endpoints:

- Home Assistant: `http://localhost:8123`
- InfluxDB: `http://localhost:8086`
- ChirpStack UI: `http://localhost:8087`
- MQTT broker: `tcp://localhost:1883`

## Provisioning a classroom node

```bash
python3 SETUP.PY school-yard-01 48.2167 -1.6986 --port /dev/ttyACM0 \
  --join-eui 70B3D57ED005A11A --dev-eui 0004A30B001C0530 \
  --app-key 00112233445566778899AABBCCDDEEFF
```

Use `--dry-run` first if you want to inspect the generated `config.json` payload without writing it over serial. Pass `--protocol raw` only if you explicitly want to bypass the built-in LoRaWAN OTAA path.

## Tests

Unit tests:

```bash
python3 -m unittest tests.test_crypto_utils tests.test_firmware tests.test_lorawan tests.test_project_config tests.test_setup_script
```

Stack-dependent tests:

```bash
docker compose -f src/docker-compose.yml up -d
docker compose -f src/docker-compose.yml run --rm test_runner sh -c "pip install -q -r tests/requirements.txt && python -m unittest discover -s tests"
```
