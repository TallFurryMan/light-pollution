---
lang: en
layout: single
title: "Home"
permalink: /en/
translation_reference: presentation
nav_order: 1
nav_label: "Home"
---

# Light Pollution Workshop

<div class="lp-hero">
  <div>
    <p class="lp-eyebrow">Ages 12 to 14</p>
    <h2>Measure the night, read a map, and discuss how lighting affects living things and the visibility of the sky.</h2>
    <p>The workshop relies on pre-flashed kits so students spend their time observing, comparing locations, and explaining results instead of fighting setup problems.</p>
    <div class="lp-actions">
      <a class="lp-button" href="{{ site.baseurl }}{% link en/KIDS.md %}">Student path</a>
      <a class="lp-button lp-button--secondary" href="{{ site.baseurl }}{% link en/TEACHERS.md %}">Teacher guide</a>
    </div>
  </div>
  <div class="lp-panel">
    <h3>What students learn</h3>
    <p>Environmental sensing, radio networking, map reading, autonomous power, and critical thinking around measurements.</p>
    <h3>What they handle</h3>
    <p>A sensor node, a map in Home Assistant, lux values, and a short written conclusion.</p>
  </div>
</div>

![Home Assistant map view](../images/ha-map.png)

## Quick entry points

<div class="lp-grid">
  <div class="lp-card">
    <h3>Students</h3>
    <p>Run the classroom activity, place the node, read the map, and compare bright and dark locations.</p>
    <p><a href="{{ site.baseurl }}{% link en/KIDS.md %}">Open the student path</a></p>
  </div>
  <div class="lp-card">
    <h3>Teachers</h3>
    <p>Prepare the gateway, provision the kits, and structure the classroom flow.</p>
    <p><a href="{{ site.baseurl }}{% link en/TEACHERS.md %}">Open the teacher guide</a></p>
  </div>
  <div class="lp-card">
    <h3>Hardware</h3>
    <p>See the current supported kit, the newly purchased parts, and the power constraints for the next hardware variant.</p>
    <p><a href="{{ site.baseurl }}{% link en/HARDWARE.md %}">View hardware</a></p>
  </div>
  <div class="lp-card">
    <h3>Architecture</h3>
    <p>Understand the current radio, ChirpStack, MQTT, Home Assistant, and InfluxDB flow.</p>
    <p><a href="{{ site.baseurl }}{% link en/ARCHITECTURE.md %}">View architecture</a></p>
  </div>
</div>

## Current repository status

<div class="lp-note">
  <p><strong>Implemented path today:</strong> a Pico-based pre-flashed node with an SX1262 radio in EU868 and a TSL2591 sensor.</p>
  <p><strong>Next hardware path:</strong> a Raspberry Pi host with the SX1303 868 MHz gateway hat, plus an experimental Pi Zero 2W node variant. Full protocol alignment with the ChirpStack server path is still the next technical milestone, along with proper 5 V power regulation for the Pi Zero 2W variant.</p>
</div>
