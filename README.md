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
- Current gateway boundary: the Docker stack exposes `chirpstack-gateway-bridge`, but the SX1303 concentrator still needs a host-side packet forwarder on the Raspberry Pi.

## Main files

| File | Purpose |
|------|---------|
| `src/docker-compose.yml` | Classroom stack with ChirpStack, MQTT, Home Assistant, and InfluxDB. |
| `src/configuration.yaml` | Home Assistant configuration, including the InfluxDB 2.x exporter settings. |
| `src/firmware/firmware.py` | MicroPython node firmware for the current Pico-based reference path. |
| `src/firmware/lorawan.py` | SX1262 radio driver plus the node-side LoRaWAN Class A implementation used by the Pico firmware. |
| `src/gateway/semtech-udp/local_conf.json.example` | Minimal Semtech UDP forwarder overlay for a Raspberry Pi host running the SX1303 hat. |
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

## Validating a real SX1303 gateway

The compose stack does not drive the SX1303 concentrator directly. On a Raspberry Pi host, the current supported path is:

1. Run this repository stack with `docker compose -f src/docker-compose.yml up -d`.
2. Run a Semtech UDP packet forwarder on the Raspberry Pi host for the SX1303 hat.
3. Point that forwarder to `127.0.0.1:1700`, where `chirpstack-gateway-bridge` is already listening.
4. Register the resulting gateway EUI in ChirpStack and confirm that the gateway becomes visible before testing a node.

Use the dedicated guides for the exact validation checklist:

- French: `https://tallfurryman.github.io/light-pollution/fr/gateway/`
- English: `https://tallfurryman.github.io/light-pollution/en/gateway/`

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

## Upgrade notes

There is no application-level migration procedure yet. The current stack is expected to restart cleanly on top of the existing Docker named volumes:

- `ha-config`
- `chirpstack-pgdata`
- `influx-data`

Use `docker compose -f src/docker-compose.yml down` if you want to update images or code while preserving state. Use `docker compose -f src/docker-compose.yml down -v` only when you intentionally want a fresh classroom demo state, because that removes the named volumes and causes Home Assistant to be reseeded from `src/config-seed`.

The SX1303 gateway configuration is outside Docker today. Upgrading the stack does not migrate the host-side packet forwarder for you, so keep a copy of its configuration on the Raspberry Pi and re-check it against the repository guide after each update.
