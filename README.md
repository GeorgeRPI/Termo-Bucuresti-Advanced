# Termo Bucuresti Advanced pentru Home Assistant

![Version](https://img.shields.io/badge/version-v1.0.0-blue)
![hacs](https://img.shields.io/badge/HACS-Custom-orange.svg)

Monitorizare avansată a întreruperilor la apă caldă și căldură de la CMTEB București.

##  🌟 Caracteristici

- ✅ 🔍 Monitorizare în timp real a întreruperilor
- ✅ 🔍 Detalii complete: cauză, descriere, dată estimată pentru reparare
- ✅ Filtrare după stradă și punct termic
- ✅ Notificări automate
- ✅ Statistici și istoric

## 🚀 Instalare

1. Adaugă în HACS (cele trei puncte din dreapta sus/Repozitorii non-standard): `https://github.com/GeorgeRPI/termo_bucuresti_advanced`
2. Instalează integrarea
3. Restartează Home Assistant
4. Configurează din interfața web


## 🔍 Card - Dashboard:
type: vertical-stack
cards:
  - type: glance
    entities:
      - entity: sensor.termo_status_strada
        name: Stare generală
      - entity: sensor.termo_apa_calda_strada
        name: Apă caldă
      - entity: sensor.termo_caldura_strada
        name: Căldură
  - type: entities
    entities:
      - entity: sensor.termo_cauza_strada
        name: Cauză
      - entity: sensor.termo_data_estima_strada
        name: Estimare reparare
  - type: history-graph
    entities:
      - sensor.termo_apa_calda_strada
      - sensor.termo_caldura_strada
    hours_to_show: 24

## ✨ Exemple de utilizare

### 🔔 Automatizare pentru Întrerupere termică
  - alias: "Notificare întrerupere termică"
    trigger:
      - platform: state
      - entity_id: binary_sensor.termo_alerta_generala_strada
    to: "on"
  - action:
      - service: notify.mobile_app_telefon
    data:
      - title: "⚠️ Întrerupere servicii termice"
    message: >-
      S-a detectat o întrerupere la {{ state_attr('binary_sensor.termo_alerta_generala_strada', 'serviciu_afectat') }}.
      Cauză: {{ state_attr('binary_sensor.termo_alerta_generala_strada', 'cauza') }}
      Estimare reparare: {{ state_attr('binary_sensor.termo_alerta_generala_strada', 'data_estimata') }} {{ state_attr('binary_sensor.termo_alerta_generala_strada',          'ora_estimata') }}
