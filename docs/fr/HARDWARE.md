---
# Matériel

## Liste de pièces (BOM)
- Raspberry Pi Pico
- Module LoRa (SX127x ou HAT SX1262 pour Pico)
- Capteur de lumière (TEMT6000 ou TSL2591 ou BH1750)
- Batterie Li‑Po + chargeur (MCP73871 ou TP4056)
- Régulateur 3.3 V, condensateurs de découplage
- Câbles Dupont / breadboard, boîtier

## Passerelle Raspberry Pi
- Concentrateur LoRa (HAT SX1303 Waveshare ou clé USB SX1302/1303).
- Mosquitto + ChirpStack + Home Assistant + InfluxDB (docker‑compose fourni).

## Conseils
- Traces SPI courtes pour le module LoRa.
- Masse commune et découplage proche des capteurs et du module radio.
- Prévoir un connecteur pour changer de capteur ou de module LoRa facilement.
