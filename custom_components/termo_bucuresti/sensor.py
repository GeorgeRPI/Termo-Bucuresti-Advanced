"""Sensor platform pentru CMTEB."""
import logging
import asyncio
from datetime import timedelta
from bs4 import BeautifulSoup
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_STREET, CONF_PUNCT_TERMIC, BASE_URL, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setare senzori din config entry."""
    street = config_entry.data[CONF_STREET]
    punct_termic = config_entry.data[CONF_PUNCT_TERMIC]
    
    api = CMTEBData(hass, street, punct_termic)
    
    sensors = [
        CMTEBStatusSensor(api, street, punct_termic, "stare_apa_calda", "Stare Apă Caldă"),
        CMTEBStatusSensor(api, street, punct_termic, "stare_caldura", "Stare Căldură"),
        CMTEBSensor(api, street, punct_termic, "cauza", "Cauză Intervenție"),
        CMTEBSensor(api, street, punct_termic, "descriere", "Descriere Intervenție"),
        CMTEBSensor(api, street, punct_termic, "data_estimare", "Dată Estimare Reparație")
    ]
    
    async_add_entities(sensors, update_before_add=True)

class CMTEBData:
    """Clasă pentru obținerea datelor de la CMTEB."""
    
    def __init__(self, hass, street, punct_termic):
        """Initialize."""
        self.hass = hass
        self.street = street
        self.punct_termic = punct_termic
        self.data = {}

    @Throttle(timedelta(seconds=SCAN_INTERVAL))
    async def async_update(self):
        """Actualizare date de la CMTEB."""
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(BASE_URL, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    await self._parse_html(html)
                else:
                    _LOGGER.error("Eroare la conectarea la CMTEB: %s", response.status)
        except Exception as e:
            _LOGGER.error("Eroare la actualizarea datelor CMTEB: %s", e)

    async def _parse_html(self, html):
        """Parsare HTML pentru extragerea datelor."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Inițializare date
        self.data = {
            "stare_apa_calda": "Necunoscut",
            "stare_caldura": "Necunoscut", 
            "cauza": "N/A",
            "descriere": "N/A",
            "data_estimare": "N/A"
        }
        
        try:
            # Căutare toate tabelele sau div-urile care conțin informații
            tables = soup.find_all('table')
            divs = soup.find_all('div', class_=True)
            
            # Combină toate elementele potențial relevante
            elements_to_check = tables + divs
            
            for element in elements_to_check:
                element_text = element.get_text().lower()
                
                # Verifică dacă elementul conține referințe la strada noastră
                if self.street.lower() in element_text or self.punct_termic.lower() in element_text:
                    _LOGGER.debug("Am găsit element relevant pentru %s", self.street)
                    
                    # Încearcă să extragi informații din tabele
                    if element.name == 'table':
                        rows = element.find_all('tr')
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                header = cells[0].get_text().strip().lower()
                                value = cells[1].get_text().strip()
                                
                                # Mapare date bazată pe conținut
                                if any(word in header for word in ['apă caldă', 'apa calda', 'apa', 'calda']):
                                    self.data["stare_apa_calda"] = self._parse_status(value)
                                elif any(word in header for word in ['căldură', 'caldura', 'caldura', 'încălzire']):
                                    self.data["stare_caldura"] = self._parse_status(value)
                                elif any(word in header for word in ['cauză', 'cauza', 'motiv', 'cauze']):
                                    self.data["cauza"] = value
                                elif any(word in header for word in ['descriere', 'detalii', 'explicație']):
                                    self.data["descriere"] = value
                                elif any(word in header for word in ['data', 'estimare', 'programare', 'reparatie']):
                                    self.data["data_estimare"] = value
                    
                    # Încearcă să extragi informații din div-uri
                    else:
                        # Caută text structurat în div-uri
                        div_text = element.get_text()
                        lines = div_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if ':' in line:
                                parts = line.split(':', 1)
                                if len(parts) == 2:
                                    header = parts[0].strip().lower()
                                    value = parts[1].strip()
                                    
                                    if any(word in header for word in ['apă caldă', 'apa calda']):
                                        self.data["stare_apa_calda"] = self._parse_status(value)
                                    elif any(word in header for word in ['căldură', 'caldura']):
                                        self.data["stare_caldura"] = self._parse_status(value)
                                    elif any(word in header for word in ['cauză', 'cauza']):
                                        self.data["cauza"] = value
                                    elif any(word in header for word in ['descriere']):
                                        self.data["descriere"] = value
                                    elif any(word in header for word in ['data', 'estimare']):
                                        self.data["data_estimare"] = value
                                
        except Exception as e:
            _LOGGER.error("Eroare la parsarea HTML-ului: %s", e)

    def _parse_status(self, text):
        """Parsează textul pentru a determina starea."""
        if not text:
            return "Necunoscut"
            
        text_lower = text.lower()
        if any(word in text_lower for word in ['oprit', 'stop', 'întrerupt', 'intrerupt', 'suspendat', 'avarie']):
            return "Oprită"
        elif any(word in text_lower for word in ['funcțiune', 'funcţiune', 'funcțiune', 'activ', 'normal', 'funcționează']):
            return "Funcționează"
        else:
            return text

class CMTEBSensor(SensorEntity):
    """Reprezentare senzor generic CMTEB."""
    
    def __init__(self, api, street, punct_termic, sensor_type, sensor_name):
        """Initialize."""
        self._api = api
        self._street = street
        self._punct_termic = punct_termic
        self._sensor_type = sensor_type
        self._attr_name = f"CMTEB {sensor_name} {street}"
        self._attr_unique_id = f"cmteb_{sensor_type}_{street}_{punct_termic}"
        self._state = None

    @property
    def state(self):
        """Returnare stare."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Atribute suplimentare."""
        return {
            "strada": self._street,
            "punct_termic": self._punct_termic,
            "tip_senzor": self._sensor_type
        }

    async def async_update(self):
        """Actualizare senzor."""
        await self._api.async_update()
        self._state = self._api.data.get(self._sensor_type, "Necunoscut")

class CMTEBStatusSensor(CMTEBSensor):
    """Senzor specializat pentru stări (apă caldă/căldură)."""
    
    @property
    def icon(self):
        """Iconiță bazată pe stare."""
        if self._state == "Oprită":
            return "mdi:alert-octagram"
        elif self._state == "Funcționează":
            return "mdi:check-circle"
        else:
            return "mdi:help-circle"
