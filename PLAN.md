# Next Steps

- Ensure Home Assistant starts clean with test-time onboarding (Melesse, FR) and pre-created admin.
- Wire MQTT discovery device trackers/sensors near Melesse so HA map shows test devices.
- Add service-level tests (MQTT discovery presence, Influx health) without full end-to-end coupling.
- Keep stack and CI green via `test_runner` in compose and GitHub Actions.
