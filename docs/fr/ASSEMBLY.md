---
lang: fr
layout: single
title: "Guide de montage"
---
# Guide de montage pas à pas

## 1. Préparer la breadboard
1. Insérer le **Raspberry Pi Pico**.
2. Relier **GND** au rail de masse, **3.3 V** au rail positif.

## 2. Câblage des capteurs de lumière
Choisir selon la sensibilité voulue.

### 2.1 TEMT6000 (analogique)
- OUT → **GP2** (ADC0), VCC 3.3 V, GND commun.
- Condensateur 10 µF entre VCC et GND conseillé.

### 2.2 TSL2591 (I²C)
- SCL → **GP5**, SDA → **GP4**, VCC 3.3 V, GND commun.
- Adresse par défaut 0x29.

### 2.3 BH1750 (I²C)
- SCL → **GP5**, SDA → **GP4**, VCC 3.3 V, GND commun.
- Adresse par défaut 0x23.

## 3. Module LoRa
- SPI0 : SCK GP13, MOSI GP15, MISO GP14.
- CS/NSS : GP18 (par défaut).
- DIO0 (IRQ) : GP18 ou autre selon module.
- RESET : GP10 (optionnel).
- Découplage 100 nF près du module.

## 4. Alimentation
- Batterie Li‑Po 4.2 V + chargeur (MCP73871 ou TP4056).
- Régulateur 3.3 V vers rails du Pico et des capteurs.
- Vérifier 3.3 V au multimètre.
