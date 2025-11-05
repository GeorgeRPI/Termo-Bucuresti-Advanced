# Configurare Termo Bucuresti Advanced

## Configurare Inițială

### Prin Interfața Web

1. Navighează la **Setări** → **Dispozitive și servicii**
2. Click pe butonul **"+ Adaugă integrare"**
3. Caută **"Termo Bucuresti Advanced"**
4. Completează formularul de configurare:

### Câmpuri de Configurare

| Câmp | Descriere | Valori Acceptate |
|------|-----------|------------------|
| **Stradă** | Numele străzii de monitorizat | Orice nume de stradă valid din București |
| **Punct termic** | Punctul termic pentru filtrare | Toate, Centru, Vest, Sud, Nord, Est |
| **Sector** | Sectorul pentru filtrare | Toate sectoarele, Sector 1-6 |
| **Interval actualizare** | Frecvența verificărilor | 5-120 minute |

### Exemplu Configurație

```yaml
strada: "Bulevardul Unirii"
punct_termic: "centru"
sector: "sector3"
update_interval: 15
