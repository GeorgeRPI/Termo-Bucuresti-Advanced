"""Binary sensors for Termo Bucuresti."""
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util
from .const import DOMAIN, CONF_STRADA, URL_CMTEB

import asyncio
import logging
import re
from typing import Dict, List, Any

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    binary_sensors = [
        TermoAlertApaCaldaSensor(entry),
        TermoAlertCalduraSensor(entry),
        TermoAlertGeneralSensor(entry),
    ]
    
    async_add_entities(binary_sensors, True)

class TermoBaseBinarySensor(BinarySensorEntity):
    """Base binary sensor class."""
    
    def __init__(self, entry: ConfigEntry):
        self._entry = entry
        self._session = None
        self._last_update = None
        self._attr_available = True
        self._interruption_data = {}

    async def async_update(self):
        """Update binary sensor."""
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
                    await self._update_binary_state()
                    self._last_update = dt_util.now()
                else:
                    self._attr_available = False
                    
        except Exception as e:
            _LOGGER.error("Eroare la actualizare binary sensor: %s", e)
            self._attr_available = False

    async def _parse_interruption_data(self, html: str) -> Dict[str, Any]:
        """Parse interruption data for binary sensors."""
        strada_cautata = self._entry.data[CONF_STRADA].lower()
        interruptions = []
        
        # Caută secțiuni relevante în HTML
        sections = re.split(r'</?div|</?tr|</?p|</?li', html)
        
        for section in sections:
            section_lower = section.lower()
            
            if strada_cautata in section_lower:
                # Verifică dacă este o întrerupere
                is_interruption = any(keyword in section_lower for keyword in [
                    'întrerupere', 'avarie', 'defect', 'repara', 'intervenție',
                    'apă caldă', 'căldură', 'serviciu termic'
                ])
                
                if is_interruption:
                    interruption = {
                        'strada': self._entry.data[CONF_STRADA],
                        'serviciu': self._extract_service_type(section),
                        'cauza': self._extract_cause(section),
                        'data_estimata': self._extract_estimated_date(section),
                        'ora_estimata': self._extract_estimated_time(section),
                        'detectat_la': dt_util.now().isoformat()
                    }
                    interruptions.append(interruption)
        
        return {
            'interruptions': interruptions,
            'total_gasite': len(interruptions)
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
            r'datorită[\s]*([^\.\n]+)'
        ]
        
        for pattern in cause_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        
        return "Nespecificat"

    def _extract_estimated_date(self, text: str) -> str:
        """Extract estimated date from text."""
        date_pattern = r'(\d{1,2}[\.\/]\d{1,2}[\.\/]\d{4})'
        match = re.search(date_pattern, text)
        return match.group(1) if match else "Nespecificat"

    def _extract_estimated_time(self, text: str) -> str:
        """Extract estimated time from text."""
        time_pattern = r'(\d{1,2}:\d{2})'
        match = re.search(time_pattern, text)
        return match.group(1) if match else "Nespecificat"

    def _clean_text(self, text: str) -> str:
        """Clean HTML tags from text."""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    async def _update_binary_state(self):
        """Update binary sensor state - to be implemented by child classes."""
        pass

class TermoAlertApaCaldaSensor(TermoBaseBinarySensor):
    """Binary sensor for hot water alerts."""
    
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry)
        self._attr_name = f"Termo Alertă Apă Caldă - {entry.data[CONF_STRADA]}"
        self._attr_unique_id = f"termo_alert_apa_calda_{entry.entry_id}"
        self._attr_icon = "mdi:water-alert"
        self._attr_device_class = "problem"
        self._attr_is_on = False

    async def _update_binary_state(self):
        """Update hot water alert state."""
        interruptions = self._interruption_data.get('interruptions', [])
        apa_calda_interruptions = [
            i for i in interruptions 
            if i['serviciu'] in ['Apă caldă', 'Serviciu termic']
        ]
        
        self._attr_is_on = len(apa_calda_interruptions) > 0
        
        if self._attr_is_on:
            latest = apa_calda_interruptions[0]
            self._attr_extra_state_attributes = {
                'cauza': latest['cauza'],
                'data_estimata': latest['data_estimata'],
                'ora_estimata': latest['ora_estimata'],
                'numar_alerta': len(apa_calda_interruptions),
                'ultima_detectare': latest['detectat_la']
            }
            self._attr_icon = "mdi:water-alert"
        else:
            self._attr_extra_state_attributes = {
                'ultima_verificare': self._last_update.isoformat() if self._last_update else None
            }
            self._attr_icon = "mdi:water-check"

class TermoAlertCalduraSensor(TermoBaseBinarySensor):
    """Binary sensor for heating alerts."""
    
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry)
        self._attr_name = f"Termo Alertă Căldură - {entry.data[CONF_STRADA]}"
        self._attr_unique_id = f"termo_alert_caldura_{entry.entry_id}"
        self._attr_icon = "mdi:radiator-alert"
        self._attr_device_class = "problem"
        self._attr_is_on = False

    async def _update_binary_state(self):
        """Update heating alert state."""
        interruptions = self._interruption_data.get('interruptions', [])
        caldura_interruptions = [
            i for i in interruptions 
            if i['serviciu'] in ['Căldură', 'Serviciu termic']
        ]
        
        self._attr_is_on = len(caldura_interruptions) > 0
        
        if self._attr_is_on:
            latest = caldura_interruptions[0]
            self._attr_extra_state_attributes = {
                'cauza': latest['cauza'],
                'data_estimata': latest['data_estimata'],
                'ora_estimata': latest['ora_estimata'],
                'numar_alerta': len(caldura_interruptions),
                'ultima_detectare': latest['detectat_la']
            }
            self._attr_icon = "mdi:radiator-alert"
        else:
            self._attr_extra_state_attributes = {
                'ultima_verificare': self._last_update.isoformat() if self._last_update else None
            }
            self._attr_icon = "mdi:radiator"

class TermoAlertGeneralSensor(TermoBaseBinarySensor):
    """Binary sensor for general alerts."""
    
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry)
        self._attr_name = f"Termo Alertă Generală - {entry.data[CONF_STRADA]}"
        self._attr_unique_id = f"termo_alert_general_{entry.entry_id}"
        self._attr_icon = "mdi:alert-circle"
        self._attr_device_class = "problem"
        self._attr_is_on = False

    async def _update_binary_state(self):
        """Update general alert state."""
        interruptions = self._interruption_data.get('interruptions', [])
        
        self._attr_is_on = len(interruptions) > 0
        
        if self._attr_is_on:
            latest = interruptions[0]
            self._attr_extra_state_attributes = {
                'serviciu_afectat': latest['serviciu'],
                'cauza': latest['cauza'],
                'data_estimata': latest['data_estimata'],
                'ora_estimata': latest['ora_estimata'],
                'total_intreruperi': len(interruptions),
                'ultima_detectare': latest['detectat_la']
            }
            self._attr_icon = "mdi:alert-circle-outline"
        else:
            self._attr_extra_state_attributes = {
                'total_intreruperi': 0,
                'ultima_verificare': self._last_update.isoformat() if self._last_update else None
            }
            self._attr_icon = "mdi:check-circle-outline"
