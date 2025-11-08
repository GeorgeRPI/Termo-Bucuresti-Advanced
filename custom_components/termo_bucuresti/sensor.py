"""Sensors for Termo Bucuresti."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util
from .const import DOMAIN, CONF_STRADA, URL_CMTEB

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    sensors = [
        TermoApaCaldaSensor(entry),
        TermoCalduraSensor(entry),
        TermoStatusGeneralSensor(entry),
        TermoCauzaSensor(entry),
        TermoDataEstimataSensor(entry),
    ]
    
    async_add_entities(sensors, True)

class TermoBaseSensor(SensorEntity):
    """Base sensor class with advanced parsing."""
    
    def __init__(self, entry: ConfigEntry):
        self._entry = entry
        self._session = None
        self._last_update = None
        self._attr_available = True
        self._interruption_data = {}

    async def async_update(self):
        """Update sensor with advanced parsing."""
        try:
            if not self._session:
                self._session = async_get_clientsession(self.hass)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self._session.get(URL_CMTEB, headers=headers, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    self._interruption_data = await self._parse_interruption_data(html)
                    await self._update_sensor_state()
                    self._last_update = dt_util.now()
                else:
                    self._attr_available = False
                    
        except Exception as e:
            _LOGGER.error("Eroare la actualizare: %s", e)
            self._attr_available = False

    async def _parse_interruption_data(self, html: str) -> Dict[str, Any]:
        """Parse interruption data from CMTEB website with advanced detection."""
        strada_cautata = self._entry.data[CONF_STRADA].lower()
        interruptions = []
        
        # Modele pentru diferite tipuri de întreruperi
        patterns = {
            'zona': r'(?:zona|sector|cartier|strada)[\s\S]{1,100}?' + re.escape(strada_cautata),
            'serviciu': r'(?:apă caldă|căldură|încălzire|serviciu termic)',
            'cauza': r'(?:cauză|motiv|datorită)[:\s]*([^\.]+)',
            'data_estimata': r'(?:estimat|programat|până)[\s\S]{1,50}?\d{1,2}[\.\/]\d{1,2}[\.\/]\d{4}',
            'ora_estimata': r'(?:ora|la)[\s]*(\d{1,2}:\d{2})'
        }
        
        # Împărțiți HTML-ul în secțiuni care ar putea conține informații despre întreruperi
        sections = re.split(r'</?div|</?tr|</?p|</?li', html)
        
        for section in sections:
            section_lower = section.lower()
            
            # Verificați dacă secțiunea conține numele străzii și cuvintele cheie pentru servicii
            if (strada_cautata in section_lower and 
                any(keyword in section_lower for keyword in ['apă', 'caldă', 'căldură', 'termic'])):
                
                interruption = {
                    'strada': self._entry.data[CONF_STRADA],
                    'serviciu': self._extract_service_type(section),
                    'cauza': self._extract_cause(section),
                    'descriere': self._clean_text(section)[:200],
                    'data_estimata': self._extract_estimated_date(section),
                    'ora_estimata': self._extract_estimated_time(section),
                    'detectat_la': dt_util.now().isoformat()
                }
                
                interruptions.append(interruption)
        
        return {
            'interruptions': interruptions,
            'total_gasite': len(interruptions),
            'ultima_actualizare': dt_util.now().isoformat()
        }

    def _extract_service_type(self, text: str) -> str:
        """Extract service type from text."""
        text_lower = text.lower()
        if 'apă caldă' in text_lower:
            return "Apă caldă"
        elif 'căldură' in text_lower or 'încălzire' in text_lower:
            return "Căldură"
        return "Serviciu termic"

    def _extract_cause(self, text: str) -> str:
        """Extract cause from text."""
        cause_patterns = [
            r'(?:cauză|motiv)[:\s]*([^\.\n]+)',
            r'datorită[\s]*([^\.\n]+)',
            r'pentru[\s]*([^\.\n]+)'
        ]
        
        for pattern in cause_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        
        return "Nespecificat"

    def _extract_estimated_date(self, text: str) -> str:
        """Extract estimated date from text."""
        date_patterns = [
            r'(\d{1,2}[\.\/]\d{1,2}[\.\/]\d{4})',
            r'(\d{1,2}\s+[a-zA-Z]+\s+\d{4})',
            r'până[\s\S]{1,30}?(\d{1,2}[\.\/]\d{1,2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "Nespecificat"

    def _extract_estimated_time(self, text: str) -> str:
        """Extract estimated time from text."""
        time_pattern = r'(\d{1,2}:\d{2})'
        match = re.search(time_pattern, text)
        return match.group(1) if match else "Nespecificat"

    def _clean_text(self, text: str) -> str:
        """Clean HTML tags and extra spaces from text."""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    async def _update_sensor_state(self):
        """Update sensor state based on parsed data."""
        # De implementat by child classes
        pass

class TermoApaCaldaSensor(TermoBaseSensor):
    """Sensor for hot water interruptions."""
    
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry)
        self._attr_name = f"Termo Apă Caldă - {entry.data[CONF_STRADA]}"
        self._attr_unique_id = f"termo_apa_calda_{entry.entry_id}"
        self._attr_icon = "mdi:water-thermometer"
        self._attr_native_value = "Necunoscut"

    async def _update_sensor_state(self):
        """Update hot water sensor state."""
        interruptions = self._interruption_data.get('interruptions', [])
        apa_calda_interruptions = [
            i for i in interruptions 
            if i['serviciu'] in ['Apă caldă', 'Serviciu termic']
        ]
        
        if apa_calda_interruptions:
            self._attr_native_value = "Întrerupt"
            latest = apa_calda_interruptions[0]
            self._attr_extra_state_attributes = {
                'cauza': latest['cauza'],
                'descriere': latest['descriere'],
                'data_estimata': latest['data_estimata'],
                'ora_estimata': latest['ora_estimata'],
                'detectat_la': latest['detectat_la'],
                'numar_intreruperi': len(apa_calda_interruptions)
            }
        else:
            self._attr_native_value = "Normal"
            self._attr_extra_state_attributes = {
                'ultima_verificare': self._last_update.isoformat() if self._last_update else None
            }

class TermoCalduraSensor(TermoBaseSensor):
    """Sensor for heating interruptions."""
    
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry)
        self._attr_name = f"Termo Căldură - {entry.data[CONF_STRADA]}"
        self._attr_unique_id = f"termo_caldura_{entry.entry_id}"
        self._attr_icon = "mdi:radiator"
        self._attr_native_value = "Necunoscut"

    async def _update_sensor_state(self):
        """Update heating sensor state."""
        interruptions = self._interruption_data.get('interruptions', [])
        caldura_interruptions = [
            i for i in interruptions 
            if i['serviciu'] in ['Căldură', 'Serviciu termic']
        ]
        
        if caldura_interruptions:
            self._attr_native_value = "Întrerupt"
            latest = caldura_interruptions[0]
            self._attr_extra_state_attributes = {
                'cauza': latest['cauza'],
                'descriere': latest['descriere'],
                'data_estimata': latest['data_estimata'],
                'ora_estimata': latest['ora_estimata'],
                'detectat_la': latest['detectat_la'],
                'numar_intreruperi': len(caldura_interruptions)
            }
        else:
            self._attr_native_value = "Normal"
            self._attr_extra_state_attributes = {
                'ultima_verificare': self._last_update.isoformat() if self._last_update else None
            }

class TermoStatusGeneralSensor(TermoBaseSensor):
    """General status sensor."""
    
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry)
        self._attr_name = f"Termo Status - {entry.data[CONF_STRADA]}"
        self._attr_unique_id = f"termo_status_{entry.entry_id}"
        self._attr_icon = "mdi:home-analytics"
        self._attr_native_value = "Necunoscut"

    async def _update_sensor_state(self):
        """Update general status sensor."""
        interruptions = self._interruption_data.get('interruptions', [])
        
        if interruptions:
            self._attr_native_value = "Întreruperi active"
            self._attr_icon = "mdi:alert-circle-outline"
        else:
            self._attr_native_value = "Normal"
            self._attr_icon = "mdi:check-circle-outline"
        
        self._attr_extra_state_attributes = {
            'total_intreruperi': len(interruptions),
            'ultima_actualizare': self._last_update.isoformat() if self._last_update else None,
            'strada': self._entry.data[CONF_STRADA]
        }

class TermoCauzaSensor(TermoBaseSensor):
    """Sensor for interruption cause."""
    
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry)
        self._attr_name = f"Termo Cauză - {entry.data[CONF_STRADA]}"
        self._attr_unique_id = f"termo_cauza_{entry.entry_id}"
        self._attr_icon = "mdi:alert-circle"
        self._attr_native_value = "Nicio întrerupere"

    async def _update_sensor_state(self):
        """Update cause sensor."""
        interruptions = self._interruption_data.get('interruptions', [])
        
        if interruptions:
            latest = interruptions[0]
            self._attr_native_value = latest['cauza']
            self._attr_extra_state_attributes = {
                'descriere_completa': latest['descriere'],
                'serviciu_afectat': latest['serviciu'],
                'data_estimata': latest['data_estimata'],
                'ora_estimata': latest['ora_estimata']
            }
        else:
            self._attr_native_value = "Nicio întrerupere"
            self._attr_extra_state_attributes = {}

class TermoDataEstimataSensor(TermoBaseSensor):
    """Sensor for estimated restoration time."""
    
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry)
        self._attr_name = f"Termo Data Estimată - {entry.data[CONF_STRADA]}"
        self._attr_unique_id = f"termo_data_estimata_{entry.entry_id}"
        self._attr_icon = "mdi:clock-alert"
        self._attr_native_value = "Nespecificat"

    async def _update_sensor_state(self):
        """Update estimated time sensor."""
        interruptions = self._interruption_data.get('interruptions', [])
        
        if interruptions:
            latest = interruptions[0]
            data_ora = f"{latest['data_estimata']} {latest['ora_estimata']}".strip()
            self._attr_native_value = data_ora if data_ora != "Nespecificat" else "În curs"
            self._attr_extra_state_attributes = {
                'serviciu': latest['serviciu'],
                'cauza': latest['cauza']
            }
        else:
            self._attr_native_value = "Nespecificat"
            self._attr_extra_state_attributes = {}
