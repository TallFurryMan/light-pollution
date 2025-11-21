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
   The InfluxDB container will expose port `8086` for the HA integration.
4. In the HA UI, go to **Configuration → Integrations** and add
   an *InfluxDB* integration pointing at `http://influxdb:8086`.
5. All incoming sensor data will be written to the `homeassistant`
   bucket.

The configuration file is designed to work out‑of‑the‑box with the
included `src/configuration.yaml`.

### Accessing Home Assistant

After the stack is up, open `http://localhost:8123` in your browser (or
the host IP if running on another machine). The initial Home Assistant
onboarding will prompt for a user; complete that and then add the
InfluxDB integration pointing at `http://influxdb:8086`. Mosquitto is
exposed on `tcp://localhost:1883` for local testing and ChirpStack’s UI
is available on `http://localhost:8087`.
