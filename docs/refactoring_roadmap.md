# 🗺️ REFACTORING ROADMAP

## ✅ VALMIS
### 1. config_manager.py (400 riviä)
- **Status**: VALMIS 🎉
- **Tulos**: 400 → 205 riviä (49% vähennys)
- **Rakenne**: 6 modulaarista komponenttia
- **Testit**: Kaikki läpäisty

## 🔄 SEURAAVAT

### 2. quorum_manager.py (413 riviä)
- **Sijainti**: `src/managers/quorum_manager.py`
- **Koko**: 413 riviä
- **Arvio**: Keskivaikea
- **Mahdollinen jako**:
  - `quorum/` - Konsensuslogiikka
  - `voting/` - Äänestyslogiikka  
  - `network/` - Verkkokommunikaatio

### 3. manage_questions.py (491 riviä)
- **Sijainti**: `src/cli/manage_questions.py` 
- **Koko**: 491 riviä
- **Arvio**: Helppo
- **Mahdollinen jako**:
  - `commands/` - CLI-komennot
  - `validators/` - Kysymysten validointi
  - `import_export/` - Tuonti/vienti

### 4. sync_coordinator.py (429 riviä)
- **Sijainti**: `src/cli/sync_coordinator.py`
- **Koko**: 429 riviä
- **Arvio**: Vaikea
- **Mahdollinen jako**:
  - `coordination/` - Synkronointilogiikka
  - `conflict/` - Konfliktien ratkaisu
  - `recovery/` - Palautuslogiikka

## 📈 TILASTOT

### Refaktoroitu:
- **Yhteensä**: 400 riviä
- **Säästö**: 195 riviä (49%)
- **Aika**: Noin 2 tuntia

### Jäljellä:
- **Yhteensä**: ~1669 riviä (4 tiedostoa)
- **Arvioitu säästö**: 800+ riviä
- **Arvioitu aika**: 8-10 tuntia

## 🎯 STRATEGIA

### Priorisointi:
1. **Suurin vaikutus**: quorum_manager.py (tärkeä core-moduuli)
2. **Helpoin**: manage_questions.py (nopea voitto)
3. **Vaikein**: sync_coordinator.py (monimutkainen logiikka)

### Lähestymistapa:
- Testaa aina ennen refaktorointia
- Säilytä legacy-compatibility
- Dokumentoi jokainen vaihe
- Commitoi pieniin osiin

## ✅ LISÄTTY: manage_questions.py (491 riviä)
- **Status**: VALMIS 🎉
- **Tulos**: 491 → 127 riviä (74% vähennys)
- **Rakenne**: 9 modulaarista komponenttia
- **Testit**: Perustoiminnot testattu
- **Aika**: Noin 3 tuntia

## 📈 PÄIVITETYT TILASTOT

### Refaktoroitu:
- **Yhteensä**: 891 riviä (2 tiedostoa)
- **Säästö**: 464 riviä (52%)
- **Aika**: Noin 5 tuntia

### Jäljellä:
- **Yhteensä**: ~1178 riviä (3 tiedostoa)
- **Arvioitu säästö**: 600+ riviä
- **Arvioitu aika**: 6-8 tuntia
