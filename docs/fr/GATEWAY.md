---
lang: fr
layout: single
title: "Passerelle"
permalink: /fr/gateway
translation_reference: gateway
nav_order: 5
nav_label: "Passerelle"
---

# Validation de la passerelle Raspberry Pi

Cette page comble un manque important du dépôt : la pile Docker contient déjà ChirpStack et `chirpstack-gateway-bridge`, mais elle ne pilote **pas** directement le concentrateur SX1303.

Pour un Raspberry Pi 400 avec un HAT Waveshare SX1303 868 MHz, le chemin supporté aujourd’hui est :

1. la machine Raspberry Pi exécute le packet forwarder SX1303
2. le packet forwarder envoie le trafic Semtech UDP vers `127.0.0.1:1700`
3. `chirpstack-gateway-bridge` convertit ce trafic vers MQTT pour ChirpStack
4. ChirpStack accepte ensuite les joins et les uplinks des nœuds de la classe

## Avant toute mise sous tension

- Brancher l’antenne LoRa avant de démarrer le concentrateur.
- Garder le projet en `EU868` de bout en bout.
- Activer le SPI sur le Raspberry Pi.
- Démarrer d’abord la pile du dépôt pour que l’UDP `1700` soit déjà disponible.

La commande de pile reste :

```bash
docker compose -f src/docker-compose.yml up -d
```

## Ce qui tourne où

La séparation actuelle est volontaire :

- `src/docker-compose.yml` exécute ChirpStack, Mosquitto, Home Assistant, InfluxDB et `chirpstack-gateway-bridge`
- la machine Raspberry Pi exécute le forwarder SX1302 / SX1303, car ce processus a besoin d’un accès direct au SPI, au reset GPIO et au concentrateur

Si la pile Docker est active mais que le packet forwarder n’est pas lancé sur l’hôte, le tableau de bord peut encore afficher les capteurs factices MQTT, mais le vrai HAT LoRaWAN ne participe pas encore.

## Préparer la machine Raspberry Pi

### 1. Activer le SPI

Sous Raspberry Pi OS :

```bash
sudo raspi-config
```

Activer `Interface Options` -> `SPI`, puis redémarrer si demandé.

### 2. Compiler le packet forwarder

Deux sources pratiques conviennent pour ce HAT :

- le wiki Waveshare SX1302 / SX1303 et son paquet de démonstration
- l’implémentation de référence `sx1302_hal` de Semtech

Références :

- wiki Waveshare : https://www.waveshare.com/wiki/SX1302_LoRaWAN_Gateway_HAT
- HAL Semtech : https://github.com/Lora-net/sx1302_hal

Flux de compilation typique de Semtech sous Raspberry Pi OS :

```bash
sudo apt update
sudo apt install -y git build-essential
git clone https://github.com/Lora-net/sx1302_hal.git
cd sx1302_hal
sed -i "s/^TARGET_USR *=.*/TARGET_USR = ${USER}/" target.cfg
make clean all
```

Notes :

- Semtech demande de modifier `target.cfg` avant les opérations d’installation. Remplacer `TARGET_USR` dès maintenant est sans danger et évite le cas fréquent où l’utilisateur réel n’est plus `pi` sur les images récentes de Raspberry Pi OS.
- Sous Raspberry Pi OS Trixie, le `tools/reset_lgw.sh` fourni par Semtech n’est plus un bon défaut car il utilise encore l’interface GPIO obsolète `/sys/class/gpio`.

### 2.b Remplacer le helper de reset sous Raspberry Pi OS Bookworm / Trixie

Le dépôt fournit un helper de reset spécifique Raspberry Pi dans `src/gateway/semtech-udp/reset_lgw.sh`.

Le copier à la place du helper Semtech avant de lancer `chip_id` ou `lora_pkt_fwd` :

```bash
export WORKSHOP_REPO="$HOME/light-pollution"
cp "$WORKSHOP_REPO/src/gateway/semtech-udp/reset_lgw.sh" util_chip_id/
cp "$WORKSHOP_REPO/src/gateway/semtech-udp/reset_lgw.sh" packet_forwarder/
chmod +x util_chip_id/reset_lgw.sh packet_forwarder/reset_lgw.sh
```

Pourquoi :

- le helper Semtech actuel attend encore `/sys/class/gpio`
- Raspberry Pi OS s’éloigne de cette interface sysfs sur les noyaux récents
- le script de remplacement du dépôt utilise `pinctrl`, qui correspond au chemin natif Raspberry Pi OS pour ce cas

### 3. Récupérer l’EUI de la passerelle

L’identifiant de passerelle utilisé par ChirpStack vient de l’outil du concentrateur :

```bash
cd util_chip_id
./chip_id
```

Conserver cet EUI. Il faudra le reprendre à l’identique lors de la création de la passerelle dans ChirpStack.

## Configurer le forwarder pour ce dépôt

Conserver les paramètres radio EU868 propres à la carte dans l’exemple Waveshare ou Semtech correspondant à une passerelle SX1250 / SX1303. Ajouter ensuite une petite surcharge locale pour l’adresse du serveur.

Un exemple est fourni dans `src/gateway/semtech-udp/local_conf.json.example`.

Surcharge minimale :

```json
{
  "gateway_conf": {
    "gateway_ID": "AA555A0000000000",
    "server_address": "127.0.0.1",
    "serv_port_up": 1700,
    "serv_port_down": 1700
  }
}
```

Les points importants :

- `gateway_ID` doit correspondre à la sortie de `chip_id`
- `server_address` doit être `127.0.0.1` si la pile tourne sur le même Raspberry Pi
- `serv_port_up` et `serv_port_down` doivent tous deux viser `1700`
- la région radio doit rester cohérente avec `EU868`

## Valider le côté pile avant de toucher à un nœud

### 1. Vérifier que le bridge est lancé

```bash
docker compose -f src/docker-compose.yml ps
docker logs gateway_bridge --tail 50
```

Il faut que `gateway_bridge` soit actif avant de lancer le forwarder.

### 2. Créer la passerelle dans ChirpStack

Ouvrir `http://localhost:8087`, puis :

1. créer ou ouvrir un tenant
2. ajouter une passerelle
3. utiliser exactement le `gateway_ID` retourné par `chip_id`
4. garder la région sur `EU868`

### 3. Lancer le packet forwarder

Exemple :

```bash
cd packet_forwarder
./lora_pkt_fwd -c local_conf.json
```

### 4. Observer les premiers signes de succès

La progression attendue est :

1. le packet forwarder démarre sans erreur d’initialisation du concentrateur
2. `gateway_bridge` reçoit du trafic Semtech UDP
3. ChirpStack affiche la passerelle comme vue récemment
4. seulement ensuite il devient pertinent d’allumer un nœud Pico et de tester le join OTAA

## Valider un vrai nœud de classe

Une fois la passerelle visible dans ChirpStack :

1. provisionner le nœud Pico avec `SETUP.PY`
2. alimenter d’abord le nœud près de la passerelle
3. vérifier les événements du device dans ChirpStack pour le join OTAA
4. vérifier l’uplink applicatif
5. déplacer ensuite le nœud vers la salle ou le point d’observation réel

Si la passerelle est saine mais que le nœud ne rejoint toujours pas le réseau, les suspects suivants sont les identifiants LoRaWAN ou une incohérence de région, pas la pile Docker elle-même.

## Dépannage

### Le packet forwarder ne parvient pas à initialiser le concentrateur

Vérifier :

- le SPI est activé
- le script de reset est présent à côté du binaire
- sous Raspberry Pi OS Bookworm / Trixie, ce script doit être la version du dépôt, pas le script Semtech basé sur sysfs
- le HAT est bien enfiché
- l’antenne est branchée
- la configuration utilisée correspond bien à une passerelle SX1250 en EU868

Si des erreurs mentionnent `/sys/class/gpio`, le problème n’est généralement pas un paquet manquant. Cela signifie surtout que l’ancien helper de reset s’appuie sur une interface GPIO que les noyaux Raspberry Pi récents n’exposent plus de la même manière.

### Le packet forwarder tourne mais ChirpStack ne voit jamais la passerelle

Vérifier :

- `server_address` pointe vers `127.0.0.1`
- les deux ports UDP sont bien `1700`
- `gateway_bridge` est réellement lancé dans Docker
- aucun filtrage local ne bloque l’UDP

### ChirpStack voit la passerelle mais le nœud ne rejoint pas

Vérifier :

- la passerelle et le nœud sont tous deux en `EU868`
- les identifiants OTAA du nœud correspondent à ChirpStack
- le nœud est proche de la passerelle pour la première validation

### Home Assistant fonctionne mais seuls les capteurs factices apparaissent

Cela signifie que la partie MQTT et tableau de bord est vivante, mais que le vrai chemin SX1303 n’est pas encore lancé ou pas encore correctement configuré.

## Chemin de mise à jour pour un Raspberry Pi hôte

Il n’existe pas encore de vraie procédure de migration, mais le modèle de mise à jour doit déjà être explicite.

### État Docker

Les volumes nommés actuels sont :

- `ha-config`
- `chirpstack-pgdata`
- `influx-data`

Lors d’une mise à jour normale, il faut les conserver :

```bash
docker compose -f src/docker-compose.yml down
docker compose -f src/docker-compose.yml up -d
```

Utiliser `down -v` uniquement pour une remise à zéro complète, en acceptant la perte du tableau de bord, de la base et de l’état Home Assistant pré-semé.

### État passerelle

La configuration du forwarder SX1303 n’est pas stockée dans les volumes Docker. Il faut la traiter comme une configuration d’hôte :

- conserver une copie de `local_conf.json`
- noter l’EUI de la passerelle déclarée dans ChirpStack
- après mise à jour du dépôt, comparer la configuration locale avec l’exemple du dépôt avant de relancer le forwarder

C’est le chemin de mise à jour pratique aujourd’hui : conserver les volumes Docker, conserver la configuration de passerelle sur l’hôte, puis revalider la passerelle avant la séance suivante.
