# Semtech UDP forwarder overlay

This directory contains a minimal endpoint override for a Raspberry Pi host that
runs the SX1303 packet forwarder next to the repository Docker stack.

Use it as a `local_conf.json` style overlay on top of the board-specific EU868
configuration supplied by Waveshare or Semtech for the SX1250 / SX1303 gateway.

What you must replace before use:

- `gateway_ID` with the output of `util_chip_id/chip_id`
- `server_address` if the forwarder does not run on the same host as the stack

The repository stack expects the forwarder to send Semtech UDP traffic to
`chirpstack-gateway-bridge` on UDP port `1700`.

For Raspberry Pi OS Bookworm / Trixie, use the `reset_lgw.sh` shipped in this
directory instead of the upstream Semtech helper. The upstream helper still
targets the obsolete sysfs GPIO interface, while this repository variant uses
`pinctrl`, which matches current Raspberry Pi OS behavior.
