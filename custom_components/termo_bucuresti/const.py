"""Constants for Termo Bucuresti Advanced."""
from homeassistant.const import Platform

DOMAIN = "termo_bucuresti"
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

# Chei de configurare
CONF_STRADA = "strada"
CONF_PUNCT_TERMIC = "punct_termic"
CONF_SECTOR = "sector"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_NOTIFICARI = "notificari"
CONF_DEBUG_MODE = "debug_mode"

# Valori implicite
DEFAULT_UPDATE_INTERVAL = 15
DEFAULT_NOTIFICARI = True
DEFAULT_DEBUG_MODE = False

# Puncte termice
PUNCTE_TERMICE = {
    "toate": "Toate punctele termice",
    "centru": "Centru",
    "vest": "Vest",
    "sud": "Sud",
    "nord": "Nord",
    "est": "Est"
}

# Sectoare
SECTORI = {
    "toate": "Toate sectoarele",
    "sector1": "Sector 1",
    "sector2": "Sector 2",
    "sector3": "Sector 3",
    "sector4": "Sector 4",
    "sector5": "Sector 5",
    "sector6": "Sector 6"
}

# URL-uri
URL_CMTEB = "https://www.cmteb.ro/functionare_sistem_termoficare.php"
URL_BASE = "https://www.cmteb.ro"

# Atribute
ATTR_CAUZA = "cauza"
ATTR_DESCRIERE = "descriere"
ATTR_DATA_ESTIMATA = "data_estimata"
ATTR_ORA_ESTIMATA = "ora_estimata"
ATTR_SERVICIU = "serviciu"
ATTR_STRADA = "strada"
ATTR_PUNCT_TERMIC = "punct_termic"
ATTR_SECTOR = "sector"
ATTR_ULTIMA_ACTUALIZARE = "ultima_actualizare"
ATTR_NUMAR_INTRERUPERI = "numar_intreruperi"

# Tipuri de servicii
SERVICIU_APA_CALDA = "apă caldă"
SERVICIU_CALDURA = "căldură"
SERVICIU_TERMIC = "serviciu termic"

# Stări
STARE_NORMAL = "Normal"
STARE_INTRERUPT = "Întrerupt"
STARE_NECUNOSCUT = "Necunoscut"

# Severitate
SEVERITATE_SCAZUTA = "scăzută"
SEVERITATE_MEDIE = "medie"
SEVERITATE_RIDICATA = "ridicată"
