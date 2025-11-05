"""Constants for Termo Bucuresti."""
DOMAIN = "termo_bucuresti"

CONF_STRADA = "strada"
CONF_PUNCT_TERMIC = "punct_termic"
CONF_SECTOR = "sector"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_UPDATE_INTERVAL = 15

PUNCTE_TERMICE = {
    "toate": "Toate punctele termice",
    "centru": "Centru",
    "vest": "Vest",
    "sud": "Sud",
    "nord": "Nord",
    "est": "Est"
}

SECTORI = {
    "toate": "Toate sectoarele",
    "sector1": "Sector 1",
    "sector2": "Sector 2", 
    "sector3": "Sector 3",
    "sector4": "Sector 4",
    "sector5": "Sector 5",
    "sector6": "Sector 6"
}

URL_CMTEB = "https://www.cmteb.ro/functionare_sistem_termoficare.php"
