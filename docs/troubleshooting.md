
## 📄 **11. docs/troubleshooting.md**
```markdown
# Depanare Termo Bucuresti Advanced

## Probleme Comune

### ❌ Integrarea nu apare în HACS

**Soluții:**
1. Verifică că repository-ul este public
2. Asigură-te că structura fișierelor este corectă
3. Verifică conținutul fișierului `hacs.json`

### ❌ Senzorii nu se actualizează

**Cauze posibile:**
- Conexiune internet indisponibilă
- Site-ul CMTEB este indisponibil
- Numele străzii este scris incorect

**Soluții:**
1. Verifică conectivitatea la internet
2. Accesează manual site-ul CMTEB
3. Verifică ortografia numelui străzii

### ❌ Nu se detectează întreruperi

**Cauze posibile:**
- Structura site-ului CMTEB s-a schimbat
- Numele străzii nu apare în formularul corect
- Întreruperile nu sunt încă afișate

**Soluții:**
1. Verifică manual pe site-ul CMTEB
2. Încearcă variante diferite ale numelui străzii
3. Activează modul debug pentru logs detaliate

## Configurare Logging

Pentru depanare detaliată, adaugă în `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.termo_bucuresti: debug
