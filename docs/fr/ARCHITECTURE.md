---
lang: fr
layout: single
title: "Architecture"
permalink: /fr/architecture
translation_reference: architecture
nav_order: 6
nav_label: "Architecture"
---

# Architecture du projet

## Vue pédagogique

![Vue d’ensemble de la classe](../images/classroom-flow-fr.svg){: .lp-diagram }

Le principe est simple :

1. Un nœud capteur mesure la lumière.
2. La radio envoie la mesure vers la passerelle.
3. La passerelle publie les données dans la pile logicielle.
4. Home Assistant affiche la carte et InfluxDB garde l’historique.

## Chaîne technique réelle

![Chaîne technique du dépôt](../images/software-stack-fr.svg){: .lp-diagram }

La pile Docker du dépôt comprend :

- ChirpStack pour la couche réseau radio.
- Mosquitto pour le transport MQTT.
- Home Assistant pour l’affichage et l’exploitation pédagogique.
- InfluxDB pour conserver l’historique complet.

## Modèle de données utile en classe

```json
{
  "name": "college-cour-01",
  "latitude": 48.2167,
  "longitude": -1.6986,
  "lux": 123,
  "ts": 1690000000,
  "charger_type": "CN3065",
  "charger_status": "unknown"
}
```

## Choix de référence après révision

- Une seule bande radio par défaut : EU868.
- Un seul capteur mis en avant : TSL2591X.
- Un seul chemin simple pour les élèves : kits pré-flashés.
- Une seule passerelle recommandée : machine hôte + HAT SX1303 868 MHz.

## Limite connue assumée

<div class="lp-note">
  <p>Le dépôt a été nettoyé pour être cohérent avec le kit Pico actuel. La variante Pi Zero 2W avec HAT SX1262 est documentée comme évolution matérielle, mais pas encore fournie comme implémentation de nœud prête à l’emploi.</p>
  <p>L’alignement complet entre le firmware de nœud et la chaîne ChirpStack/LoRaWAN reste la prochaine étape protocolaire du projet.</p>
</div>
