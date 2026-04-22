---
lang: fr
layout: single
title: "Enseignants"
permalink: /fr/teachers
translation_reference: teachers
nav_order: 3
nav_label: "Enseignants"
---

# Guide enseignant

## Kit de référence pour l’atelier

- Nœud actuel du dépôt : Raspberry Pi Pico + radio SX1262 868 MHz + capteur TSL2591 + kit pré-flashé.
- Capteur de lumière visé : TSL2591X en I²C.
- Alimentation visée : batterie LiPo 3,7 V + chargeur solaire CN3065.
- Passerelle visée : Raspberry Pi 4/5 ou LattePanda v1 + HAT SX1303 868 MHz.

## Avant la séance

1. Monter ou préparer les kits.
2. Vérifier qu’un kit publie bien une mesure de test.
3. Pré-configurer le nom et la position avec `SETUP.PY`.
4. Préparer une carte des lieux d’observation autour de l’établissement.
5. Décider combien de groupes comparent des zones sombres, éclairées, mixtes.
6. Valider le chemin passerelle Raspberry Pi + HAT SX1303 avant l’arrivée des élèves.

## Provisionner un kit pré-flashé

Exemple :

```bash
python3 SETUP.PY college-cour-01 48.2167 -1.6986 --port /dev/ttyACM0 \
  --join-eui 70B3D57ED005A11A --dev-eui 0004A30B001C0530 \
  --app-key 00112233445566778899AABBCCDDEEFF
```

Ce script écrit `config.json` sur le nœud et stocke :

- le nom du kit
- la latitude et la longitude
- le profil matériel du nœud
- le protocole radio utilisé
- le type de capteur
- le type de chargeur
- l’intervalle de mesure
- les identifiants LoRaWAN OTAA du kit

Utiliser `--dry-run` pour vérifier le contenu avant écriture.

## Pendant la séance

1. Distribuer les kits et rappeler les règles de sécurité.
2. Associer chaque groupe à un lieu précis.
3. Laisser les élèves installer puis observer la carte.
4. Demander une hypothèse avant d’annoncer les résultats des autres groupes.
5. Faire un retour collectif sur les effets de la lumière nocturne.

## Après la séance

- Exporter quelques mesures marquantes.
- Comparer les lieux les plus lumineux et les plus sombres.
- Discuter des compromis entre sécurité, confort et sobriété lumineuse.

## Point important sur la prochaine variante Pi Zero 2W

<div class="lp-note">
  <p>Le HAT SX1262 pour Raspberry Pi et le Pi Zero 2W constituent une piste intéressante, mais ce chemin n’est pas encore implémenté dans le dépôt.</p>
  <p>Il faut encore prévoir une adaptation logicielle propre à cette variante et une alimentation 5 V régulée : la carte CN3065 charge une LiPo, elle ne suffit pas seule pour alimenter un Pi Zero 2W.</p>
</div>

## Préparer la passerelle

- Installer le HAT SX1303 868 MHz sur la machine hôte.
- Démarrer la pile Docker du dépôt.
- Vérifier l’accès à Home Assistant, ChirpStack et InfluxDB.
- Confirmer que le projet utilise bien la bande EU868.

## Valider la passerelle avant la séance

- Démarrer la pile Docker du dépôt.
- Vérifier que `chirpstack-gateway-bridge` écoute déjà sur l’UDP `1700`.
- Lancer le packet forwarder SX1303 sur l’hôte Raspberry Pi.
- Déclarer l’EUI de la passerelle dans ChirpStack et attendre qu’elle apparaisse.
- Tester ensuite seulement le join d’un nœud et un uplink réel.

Le détail de la mise en service réelle est dans le [guide passerelle]({{ site.baseurl }}{% link fr/GATEWAY.md %}).
