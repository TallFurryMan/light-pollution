# Next Steps

- Validate the new gateway guide on the real Raspberry Pi 400:
  run through the documented SX1303 steps against the live host, note any Waveshare-specific GPIO or reset quirks, and fold those observations back into the guide.

- Decide whether to support a second gateway path:
  either keep Semtech UDP as the single documented option for clarity, or add a separate Basics Station page once there is a tested reason to support it.

- Add a lightweight host-side validation helper if needed:
  a small script could confirm that Docker is up, UDP `1700` is exposed, and the gateway bridge is logging traffic, without pretending to manage the concentrator from inside the stack.

- Start a versioned migration note once releases affect state:
  today the upgrade path is "preserve named volumes and host gateway config", but future releases may need explicit notes for Home Assistant seed data, ChirpStack database state, or gateway config changes.
