## Server‑Side Setup

The repository includes a `docker-compose.yml` that runs Home Assistant,
Mosquitto MQTT, the LoRa gateway and an **InfluxDB** instance.  The
InfluxDB service stores every measurement that Home Assistant pushes
via the `influxdb2` integration, so you get unlimited‑sized history
instead of the 24‑hour retention Home Assistant uses by default.

### File layout

| File | Purpose |
|------|---------|
| `src/docker-compose.yml` | Pulls the four services.
| `src/configuration.yaml` | Minimal Home Assistant config with InfluxDB integration.
| `src/config` | Folder mapping for Home Assistant's data.  Add your custom
  config files here.

### What you need to do

1. Copy or create the `config` directory next to the compose file.
2. Add any custom Home Assistant integration config you want.
3. Start the stack: `docker compose -f src/docker-compose.yml up -d`.
   InfluxDB exposes port `8086` and is pre-wired in `src/configuration.yaml`
   via the `influxdb2` integration (no UI configuration needed).
4. Open Home Assistant at `http://localhost:8123` and complete the
   onboarding. The InfluxDB integration will be active automatically,
   writing to the `homeassistant` bucket on `influxdb:8086`.

The configuration file is designed to work out‑of‑the‑box with the
included `src/configuration.yaml`.

### Accessing Home Assistant

After the stack is up, open `http://localhost:8123` in your browser (or
the host IP if running on another machine). The initial Home Assistant
onboarding will prompt for a user; complete that and then add the
InfluxDB integration pointing at `http://influxdb:8086`. Mosquitto is
exposed on `tcp://localhost:1883` for local testing and ChirpStack’s UI
is available on `http://localhost:8087`.

### Running tests inside the stack

An optional `test_runner` container (Python 3.10) is included. To run
the tests against the live stack:

```bash
docker compose -f src/docker-compose.yml up -d
docker compose -f src/docker-compose.yml run --rm test_runner python -m unittest discover -s tests
```

The repository is mounted at `/workspace` inside the test container so
artifacts and results are available on the host.
