---
# Projet de suivi de la pollution lumineuse

## Présentation
* **Objectif** – Construire un réseau de petits capteurs autonomes qui mesurent la lumière nocturne, envoient les données vers Home Assistant et les affichent sur une carte.
* **Public** – Collégiens (12‑14 ans), travail en petits groupes.
* **Enjeu** – La pollution lumineuse perturbe la faune, le sommeil humain et l’observation du ciel. Mesurer, c’est comprendre la donnée, les réseaux et l’environnement.

## Livrables
1. **Kit matériel** – Pico, capteur de lumière, radio LoRa, batterie.
2. **Guide d’assemblage** – Pas à pas avec peu d’outillage.
3. **Firmware** – MicroPython (dossier `src/firmware`) : lecture du capteur, nom/coordonnées, envoi LoRa.
4. **Serveur** – Pile Docker avec Home Assistant, Mosquitto, passerelle LoRa‑MQTT, InfluxDB.
5. **Documentation** – Explications simples pour élèves et enseignants.

## Déroulé en classe
1. Former des équipes de 3‑4.
2. Assembler selon `docs/ASSEMBLY.md`.
3. Charger le firmware (Micropython + rshell ou REPL).
4. Configurer nom/localisation avec `SETUP.PY`.
5. Déployer dehors (arbre/toit), alimenter en Li‑Po.
6. Observer la carte Home Assistant et l’historique InfluxDB.
7. Discuter : comparer les lieux, proposer des pistes de réduction de lumière.

## Critères de réussite
- Un relevé toutes les 15 minutes.
- Carte HA montrant nom, dernière mesure et horodatage.
- Les élèves peuvent décrire le chemin de la donnée du capteur au cloud.
