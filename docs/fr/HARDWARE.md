---
lang: fr
layout: single
title: "Matériel"
permalink: /fr/hardware
translation_reference: hardware
---
## Liste de pièces (BOM)
Vous aurez à [assembler]({{ site.baseurl }}{% link fr/ASSEMBLY.md %}) les éléments suivants:
- Raspberry Pi Pico
- Module LoRa (HAT SX1262 pour Pico, ou SX127x)
- Capteur de lumière (TSL2591, ou TEMT6000 ou BH1750)
- Batterie Li‑Po + chargeur (CN3065, ou MCP73871 ou TP4056)
- Régulateur 3.3 V, condensateurs de découplage
- Câbles JST XMX 2.54mm et/ou PH 2.0mm, ou Dupont
- Boîtier

![Raspberry Pi Pico - Par Phiarc — Travail personnel, CC BY-SA 4.0, https://commons.wikimedia.org/w/index.php?curid=129649350](../images/rasp_pico.png)

![https://www.waveshare.com/sx1262-lorawan-hat.htm](../images/sx1262.png)

![https://www.cqrobot.com/index.php?route=product/product&product_id=1112](../images/tsl2591.png)

![https://www.otronic.nl/fr/500ma-mini-module-de-chargeur-solaire-lipo-lithium.html](../images/cn3065.png)

## Passerelle Raspberry Pi
- Concentrateur LoRa (HAT SX1303 Waveshare ou clé USB SX1302/1303).
- Mosquitto + ChirpStack + Home Assistant + InfluxDB (docker‑compose fourni).

![https://www.waveshare.com/wiki/SX1302_LoRaWAN_Gateway_HAT](../images/sx1303.png)

## Conseils
- Traces SPI courtes pour le module LoRa.
- Masse commune et condensateurs de découplage proche des capteurs et du module radio.
- Prévoir un connecteur pour changer de capteur ou de module LoRa facilement.
