---
lang: fr
layout: single
title: "Elèves"
permalink: /fr/kids
translation_reference: kids
---
## À quoi ça sert ?
* Mesurer la lumière ambiante toutes les 15 minutes.
* Ajouter le nom du capteur et ses coordonnées GPS.
* Envoyer les données par radio longue portée vers l’ordinateur de la classe.
* Home Assistant affiche les mesures sur une carte.

## Étapes rapides en classe
1. **Assembler** – suivre le schéma de câblage dans `docs/ASSEMBLY.md`.
2. **Charger le firmware** – copier `src/firmware/firmware.py` et `src/firmware/lorawan.py` sur le Pico.
3. **Nommer et localiser** – exécuter `python SETUP.PY <nom> <lat> <lon>` depuis l’ordinateur.
4. **Déployer** – fixer le capteur dehors; alimentation batterie Li‑Po ou petit panneau solaire via MCP73871 ou TP4056.
5. **Vérifier dans Home Assistant** – regarder la carte.
6. **Analyser les chiffres** – comparer zones sombres et zones éclairées.
7. **Rédiger un court bilan** – ce que vous apprenez sur la pollution lumineuse.

## Ce qu’il y a dans le code
`src/firmware/firmware.py` (MicroPython) :
* Lit nom/latitude/longitude depuis `config.json`.
* Mesure le capteur de lumière toutes les 15 minutes.
* Forme un message JSON et l’envoie via LoRa.

## Pourquoi MicroPython ?
* Léger, économique et lisible pour des débutants.
* Proche du Python “classique”, donc facile à prendre en main.
