---
lang: fr
layout: single
title: "Architecture du système"
---
# Architecture du système

## 1. Vue d’ensemble

**Diagramme**

Le projet comporte trois couches :
| Couche | Composants | Liaison | Rôle |
|-------|------------|---------|------|
| **Capteur** | Raspberry Pi Pico, LoRa SX127x/SX1262, capteur de lumière (TEMT6000, TSL2591, BH1750), batterie Li‑Po | LoRa | Mesure locale et émission à faible consommation |
| **Passerelle** | Raspberry Pi avec conteneurs **LoRa‑to‑MQTT** et Mosquitto | LoRa ➜ MQTT | Pont entre capteur et serveur |
| **Serveur** | Conteneur Home Assistant (+ InfluxDB) | MQTT | Stockage, traitement et visualisation |

## 2. Chaîne côté capteur
1. Le Pico lit le nom et les coordonnées depuis `config.json`.
2. Toutes les **15 minutes**, un relevé de lux est effectué.
3. Format : `{"name":"unit‑1","latitude":48.2167,"longitude":-1.6986,"lux":120,"ts":1690000000}`.
4. Le message est envoyé via LoRa.

## 3. Passerelle & serveur
- **Passerelle LoRa‑MQTT** : écoute le module LoRa et publie les messages JSON sur Mosquitto.
- **Home Assistant** : souscrit aux topics MQTT, crée les entités via la découverte, et affiche les capteurs sur la carte.
- **InfluxDB** : reçoit l’historique complet via l’intégration `influxdb2`.

## 4. Modèle de données
```json
{
  "name": "string",
  "latitude": 48.2167,
  "longitude": -1.6986,
  "lux": 123,
  "ts": 1690000000
}
```

## 5. Fiabilité
- Trames LoRa vérifiées par CRC.
- La configuration minimale est conservée en flash pour redémarrer sans intervention.
