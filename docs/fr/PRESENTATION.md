---
lang: fr
layout: single
title: "Présentation"
---
# Projet de suivi de la pollution lumineuse

## Vue d’ensemble
* **But** – Réseau de capteurs autonomes qui mesurent la lumière nocturne, envoient les données à Home Assistant et les affichent sur une carte.
* **Public** – Collégiens (12‑14 ans) en équipe.
* **Pourquoi** – La pollution lumineuse nuit aux écosystèmes, au sommeil, et cache les étoiles. Mesurer permet d’apprendre la donnée, les réseaux et l’environnement.

## Livrables
1) Kit matériel (Pico + capteur + LoRa + batterie)  
2) Guide d’assemblage  
3) Firmware MicroPython (`src/firmware`)  
4) Pile Docker (HA + Mosquitto + passerelle LoRa-MQTT + InfluxDB)  
5) Docs claires pour enseignants et élèves.

## Déroulé en classe
1. Former des équipes, assembler, flasher le firmware.  
2. Configurer nom/localisation avec `SETUP.PY`.  
3. Déployer dehors.  
4. Consulter la carte HA + historique InfluxDB.  
5. Discuter des résultats et des pistes pour réduire la lumière.
