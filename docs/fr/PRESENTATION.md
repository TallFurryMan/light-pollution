---
lang: fr
layout: single
title: "Accueil"
permalink: /fr/
translation_reference: presentation
nav_order: 1
nav_label: "Accueil"
---

# Atelier pollution lumineuse

<div class="lp-hero">
  <div>
    <p class="lp-eyebrow">Collège 5e à 3e</p>
    <h2>Mesurer la nuit, lire une carte, discuter de l’impact de l’éclairage sur le vivant et sur le ciel.</h2>
    <p>Le projet s’appuie sur des kits pré-flashés pour que les élèves passent du temps sur l’observation, la comparaison des lieux et l’interprétation des données, pas sur le dépannage logiciel.</p>
    <div class="lp-actions">
      <a class="lp-button" href="{{ site.baseurl }}{% link fr/KIDS.md %}">Parcours élèves</a>
      <a class="lp-button lp-button--secondary" href="{{ site.baseurl }}{% link fr/TEACHERS.md %}">Préparer l’atelier</a>
    </div>
  </div>
  <div class="lp-panel">
    <h3>Ce que l’on apprend</h3>
    <p>Données environnementales, réseau radio, cartographie, énergie autonome et esprit critique face aux mesures.</p>
    <h3>Ce que les élèves manipulent</h3>
    <p>Un nœud capteur, une carte Home Assistant, des mesures de lux, puis un court compte rendu.</p>
  </div>
</div>

![Carte Home Assistant des capteurs](../images/ha-map.png)

## Démarrer vite

<div class="lp-grid">
  <div class="lp-card">
    <h3>Élèves</h3>
    <p>Suivre l’activité en classe, poser le capteur, relever les résultats et comparer les zones.</p>
    <p><a href="{{ site.baseurl }}{% link fr/KIDS.md %}">Ouvrir le parcours élèves</a></p>
  </div>
  <div class="lp-card">
    <h3>Enseignants</h3>
    <p>Préparer la passerelle, nommer les kits, configurer les coordonnées et organiser la séance.</p>
    <p><a href="{{ site.baseurl }}{% link fr/TEACHERS.md %}">Ouvrir le guide enseignant</a></p>
  </div>
  <div class="lp-card">
    <h3>Matériel</h3>
    <p>Voir le kit de référence actuel, les pièces achetées pour la prochaine activité et les contraintes d’alimentation.</p>
    <p><a href="{{ site.baseurl }}{% link fr/HARDWARE.md %}">Voir le matériel</a></p>
  </div>
  <div class="lp-card">
    <h3>Architecture</h3>
    <p>Comprendre la chaîne radio, ChirpStack, MQTT, Home Assistant et InfluxDB.</p>
    <p><a href="{{ site.baseurl }}{% link fr/ARCHITECTURE.md %}">Voir l’architecture</a></p>
  </div>
</div>

## Position actuelle du dépôt

<div class="lp-note">
  <p><strong>Chemin implémenté aujourd’hui :</strong> nœud capteur basé sur un Raspberry Pi Pico avec radio SX1262 en 868 MHz, capteur TSL2591 et kit pré-configuré.</p>
  <p><strong>Chemin protocolaire implémenté aujourd’hui :</strong> le firmware Pico rejoint maintenant ChirpStack en LoRaWAN OTAA et envoie les mesures chiffrées comme charges utiles applicatives.</p>
  <p><strong>Chemin matériel suivant :</strong> passerelle Raspberry Pi 4/5 ou LattePanda v1 avec HAT SX1303 868 MHz, et expérimentation d’un nœud Pi Zero 2W avec une alimentation 5 V adaptée.</p>
</div>

## Livrables utiles

- Documentation bilingue pour l’atelier et le support technique.
- Pile serveur Docker avec ChirpStack, Mosquitto, Home Assistant et InfluxDB.
- Firmware MicroPython pour les kits pré-flashés actuels.
- Guide de montage et diagrammes pour préparer une séance plus lisible que la sortie GitHub Pages d’origine.
