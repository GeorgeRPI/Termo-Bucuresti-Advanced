# 🏠 Compania Municipală Termoenergetica București - Integrare pentru HomeAssistant

![Version](https://img.shields.io/badge/version-v2.0.1-blue)
![hacs](https://img.shields.io/badge/HACS-Custom-orange.svg)

Monitorizare avansată a întreruperilor la apă caldă și căldură de la CMTEB București.

#  🌟 Caracteristici

- ✅ 🔍 Monitorizare în timp real a întreruperilor
- ✅ 🔍 Detalii complete: cauză, descriere, dată estimată pentru reparare
- ✅ Filtrare după stradă și punct termic
- ✅ Notificări automate
- ✅ Statistici și istoric

# 🚀 Instalare

1. Adaugă în HACS (cele trei puncte din dreapta sus/Repozitorii non-standard): `https://github.com/GeorgeRPI/termo_bucuresti_advanced`
2. Instalează integrarea: Termo Bucuresti Advanced
3. Restartează Home Assistant
4. Configurează din interfața web


# 🔍 Card - Dashboard:
## Card stare curentă
type: glance
  - entities:
    - entity: sensor.termo_status_strada
    - entity: sensor.termo_apa_strada
    - entity: sensor.termo_caldura_strada

## Card statistici
  - type: statistic
    - entity: sensor.termo_statistici_strada
    - chart_type: line

## Card istoric
type: history-graph
  - entities:
    - sensor.termo_apa_strada
    - sensor.termo_caldura_strada
    - hours_to_show: 24

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
    message: >- S-a detectat o întrerupere la {{ state_attr('binary_sensor.termo_alerta_generala_strada', 'serviciu_afectat') }}.
      - Cauză: {{ state_attr('binary_sensor.termo_alerta_generala_strada', 'cauza') }}
      - Estimare reparare: {{ state_attr('binary_sensor.termo_alerta_generala_strada', 'data_estimata') }} {{ state_attr('binary_sensor.termo_alerta_generala_strada',          'ora_estimata') }}
