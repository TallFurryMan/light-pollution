# Project Plan

## Firmware and Radio
- Correct SX127x register map and transmission sequence in `lorawan.py`.
- Move firmware loop into a `main()` with dependency injection for sensor/charger/LoRa.
- Harden `config.json` handling (defaults, bad files) and make poll interval configurable.

## Testing
- Add `pytest` harness with fakes for `machine` primitives to test sensor math and payloads.
- Unit-test charger status mapping, LoRa register writes, and payload content/encoding.
- Mock `serial.Serial` to test `SETUP.PY` arguments, port detection, and script writing.

## Home Assistant Stack
- Replace host networking with a bridge network; expose 8123/1883/8086 explicitly.
- Provide a working `mosquitto.conf` and ensure `src/config/` bootstrap for Home Assistant.
- Validate images exist (Docker Hub/GHCR) and run stack via Colima on macOS.

## Classroom Flows
- 5ème: guided pairs build with pre-flashed Pico, serial/LED sanity checks, simple deploy.
- 3ème: let students tweak HA dashboards, InfluxDB views, and poll intervals/device names.
