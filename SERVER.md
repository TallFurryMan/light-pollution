# Home Assistant + LoRa‑to‑MQTT Server Setup
All instructions below assume you run the server on a **Raspberry Pi 4** with **Raspberry Pi OS (64‑bit)**.

## 1. Install Docker
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER
````
Log out and back in for the group change to take effect.

## 2. Create a docker‑compose.yml
Place the following file in the repository’s root or keep it in `src/` if you prefer. The example below simply shows the file for reference.

**File path:** `src/docker-compose.yml`
```yaml
{{< highlight yaml >}}
version: "3.8"
services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: ha
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./config:/config
  mqtt:
    image: eclipse-mosquitto:2.0
    container_name: mosquitto
    restart: unless-stopped
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
  lora_gateway:
    image: ghcr.io/lorawan/lora-gateway-docker:latest
    container_name: lora_gateway
    restart: unless-stopped
    environment:
      - MQTT_URL=tcp://mosquitto:1883
      - MQTT_USER=homeassistant
      - MQTT_PASSWORD=secret
    volumes:
      - ./lora:/etc/lora
```

## 3. Mosquitto configuration (`mosquitto.conf`)
```
listener 1883
allow_anonymous true
```

## 4. LoRa gateway config (`lora/lora_config.json`)
```json
{
  "serialPort": "/dev/ttyS0",   // adjust for the LoRa Hat
  "node": {
    "id": "pico",
    "type": "node"
  }
}
```

## 5. Running the stack
```bash
docker-compose up -d
````
Verify by checking `docker ps` and ensuring the three containers are running.

## 6. Home Assistant configuration
Add the MQTT integration via _Configuration → Integrations → MQTT_.
* URL: `mqtt://localhost`

### Map integration
Add the `Map` card in the Lovelace UI.
Add an `Entity` as `sensor.last_measurement_pico` (replace *pico* with each unit name).

## 7. Device side – what the Pico sends
The Pico publishes the JSON payload to the topic `lightpol/+/data` where the `+` is the unit name.
Example payload:
```json
{"name":"unit‑east","lat":43.586,"lon":1.226,"lux":120,"ts":1690000000}
```
The `lora_gateway` container forwards the raw LoRa frame to the MQTT broker, so the payload is available for Home Assistant.

*Enjoy your village‑wide light pollution monitoring!* 
