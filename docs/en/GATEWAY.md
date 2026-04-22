---
lang: en
layout: single
title: "Gateway"
permalink: /en/gateway
translation_reference: gateway
nav_order: 5
nav_label: "Gateway"
---

# Raspberry Pi gateway validation

This page closes an important gap in the repository: the Docker stack already contains ChirpStack and `chirpstack-gateway-bridge`, but it does **not** control the SX1303 concentrator directly.

For a Raspberry Pi 400 with a Waveshare SX1303 868 MHz hat, the current supported path is:

1. the Raspberry Pi host runs the SX1303 packet forwarder
2. the packet forwarder sends Semtech UDP traffic to `127.0.0.1:1700`
3. `chirpstack-gateway-bridge` converts that traffic into MQTT for ChirpStack
4. ChirpStack accepts joins and uplinks from the classroom nodes

## Before powering anything

- Attach the LoRa antenna before starting the concentrator.
- Keep the project on `EU868` from end to end.
- Enable SPI on the Raspberry Pi.
- Start the repository stack first so UDP `1700` is already available.

The stack command remains:

```bash
docker compose -f src/docker-compose.yml up -d
```

## What runs where

The current deployment split is intentional:

- `src/docker-compose.yml` runs ChirpStack, Mosquitto, Home Assistant, InfluxDB, and `chirpstack-gateway-bridge`.
- The Raspberry Pi host runs the SX1302 / SX1303 forwarder because that process needs direct access to SPI, GPIO reset handling, and the concentrator itself.

If the Docker stack is up but the packet forwarder is not running on the host, the classroom dashboard can still show the MQTT mock devices, but the real LoRaWAN hat is not participating yet.

## Prepare the Raspberry Pi host

### 1. Enable SPI

On Raspberry Pi OS:

```bash
sudo raspi-config
```

Enable `Interface Options` -> `SPI`, then reboot if requested.

### 2. Build the packet forwarder

Two practical sources are reasonable for this hat:

- Waveshare's SX1302 / SX1303 gateway HAT wiki and demo package
- Semtech's `sx1302_hal` reference implementation

Repository:

- Waveshare wiki: https://www.waveshare.com/wiki/SX1302_LoRaWAN_Gateway_HAT
- Semtech HAL: https://github.com/Lora-net/sx1302_hal

Typical Semtech build flow on Raspberry Pi OS:

```bash
sudo apt update
sudo apt install -y git build-essential
git clone https://github.com/Lora-net/sx1302_hal.git
cd sx1302_hal
sed -i "s/^TARGET_USR *=.*/TARGET_USR = ${USER}/" target.cfg
make clean all
```

Notes:

- Upstream Semtech asks you to edit `target.cfg` before install operations. Replacing `TARGET_USR` early is harmless and avoids the common `pi` username mismatch on newer Raspberry Pi OS images.
- On Raspberry Pi OS Trixie, the stock `tools/reset_lgw.sh` is no longer a safe default because it still uses the obsolete `/sys/class/gpio` interface.

### 2.b Replace the reset helper on Raspberry Pi OS Bookworm / Trixie

The repository ships a Raspberry Pi specific reset helper at `src/gateway/semtech-udp/reset_lgw.sh`.

Copy it over the Semtech helper before running `chip_id` or `lora_pkt_fwd`:

```bash
export WORKSHOP_REPO="$HOME/light-pollution"
cp "$WORKSHOP_REPO/src/gateway/semtech-udp/reset_lgw.sh" util_chip_id/
cp "$WORKSHOP_REPO/src/gateway/semtech-udp/reset_lgw.sh" packet_forwarder/
chmod +x util_chip_id/reset_lgw.sh packet_forwarder/reset_lgw.sh
```

Why this matters:

- Semtech's current helper still expects `/sys/class/gpio`.
- Raspberry Pi OS moved away from the old sysfs GPIO interface on recent kernels.
- The replacement script in this repository uses `pinctrl`, which is the Raspberry Pi OS-native path for this use case.

### 3. Retrieve the gateway EUI

The gateway ID used by ChirpStack comes from the concentrator tooling:

```bash
cd util_chip_id
./chip_id
```

Keep that EUI. You will need it unchanged when creating the gateway in ChirpStack.

## Configure the forwarder for this repository

Keep the board-specific EU868 radio settings from the Waveshare or Semtech example that matches the SX1250-based SX1303 board. Then add a small local override for the server endpoint.

An example file is provided at `src/gateway/semtech-udp/local_conf.json.example`.

Minimal override:

```json
{
  "gateway_conf": {
    "gateway_ID": "AA555A0000000000",
    "server_address": "127.0.0.1",
    "serv_port_up": 1700,
    "serv_port_down": 1700
  }
}
```

What matters here:

- `gateway_ID` must match the `chip_id` output.
- `server_address` should be `127.0.0.1` when the stack runs on the same Raspberry Pi.
- `serv_port_up` and `serv_port_down` must both target `1700`.
- The radio region must stay aligned with `EU868`.

## Validate the stack side before touching a node

### 1. Confirm the bridge is running

```bash
docker compose -f src/docker-compose.yml ps
docker logs gateway_bridge --tail 50
```

You want `gateway_bridge` running before you start the forwarder.

### 2. Create the gateway in ChirpStack

Open `http://localhost:8087`, then:

1. create or open a tenant
2. add a gateway
3. use the exact `gateway_ID` reported by `chip_id`
4. keep the region on `EU868`

### 3. Start the packet forwarder

Example:

```bash
cd packet_forwarder
./lora_pkt_fwd -c local_conf.json
```

### 4. Check the first success signals

The expected progression is:

1. the packet forwarder starts without concentrator init errors
2. `gateway_bridge` begins receiving Semtech UDP traffic
3. ChirpStack shows the gateway as recently seen
4. only then does it make sense to power a Pico node and test OTAA joins

## Validate a real classroom node

Once the gateway is visible in ChirpStack:

1. provision the Pico node with `SETUP.PY`
2. power the node near the gateway first
3. check ChirpStack device events for the OTAA join
4. check the application uplink payload
5. then move the node to the actual classroom or outdoor test point

If the gateway is healthy but the node still does not join, the next suspects are the LoRaWAN credentials or a region mismatch, not the Docker stack itself.

## Troubleshooting

### The packet forwarder fails to initialize the concentrator

Check:

- SPI is enabled
- the reset script is present next to the binary
- on Raspberry Pi OS Bookworm / Trixie, that reset script should be the repository version, not the stock Semtech sysfs script
- the hat is seated correctly
- the antenna is connected
- you are using a configuration intended for an SX1250-based EU868 gateway

If you see errors mentioning `/sys/class/gpio`, the problem is usually not a missing package. It means the old reset helper is using a GPIO interface that recent Raspberry Pi kernels no longer expose in the same way.

### The packet forwarder runs but ChirpStack never sees the gateway

Check:

- `server_address` points to `127.0.0.1`
- both UDP ports are set to `1700`
- `gateway_bridge` is actually running in Docker
- no firewall rule is blocking local UDP traffic

### ChirpStack sees the gateway but the node does not join

Check:

- the gateway and node are both on `EU868`
- the node OTAA credentials match what is configured in ChirpStack
- the node is close to the gateway for the first validation

### Home Assistant works, but only the mock devices appear

That means the MQTT and dashboard side is alive, but the real SX1303 gateway path is still missing or misconfigured.

## Upgrade path for a Raspberry Pi host

There is no real migration procedure yet, but the update model should already be explicit.

### Docker state

The current named volumes are:

- `ha-config`
- `chirpstack-pgdata`
- `influx-data`

In normal updates, keep them:

```bash
docker compose -f src/docker-compose.yml down
docker compose -f src/docker-compose.yml up -d
```

Use `down -v` only if you want a full reset and accept losing the current dashboard, database, and seeded Home Assistant state.

### Gateway state

The SX1303 forwarder config is not stored in Docker volumes. Treat it as host configuration:

- keep a copy of your `local_conf.json`
- keep a note of the gateway EUI used in ChirpStack
- after pulling repository changes, compare your host config with the repository example before restarting the forwarder

That is the practical upgrade path today: preserve Docker volumes, preserve the host-side gateway config, and revalidate the gateway before the next class.
