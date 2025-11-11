Totta! Luodaan TODO.md tiedosto joka listaa kaikki tekemättömät osat ja nykyisen tilanteen:

## 📝 TODO.md

**TODO.md**:
```markdown
# 🏛️ Hajautetun Vaalikoneen Kehitys - TODO Lista

## 📊 NYKYINEN TILA (✅ VALMIS)

### 🎯 Perusjärjestelmä
- [x] `install.py` - Järjestelmän asennus
- [x] `meta.json` - Järjestelmän metadata
- [x] `system_chain.json` - Muutoshistoria
- [x] Hakemistorakenne ja modulaarisuus

### ❓ Kysymysten Hallinta
- [x] `manage_questions.py` - Kysymysten lisäys ja hallinta
- [x] `questions.json` - Kysymysten data-rakenne
- [x] ELO-luokitusjärjestelmä
- [x] `compare_questions.py` - Kysymysten vertailu
- [x] `elo_admin.py` - ELO-tilastot ja hallinta

### 👑 Ehdokkaiden Hallinta
- [x] `manage_candidates.py` - Ehdokkaiden lisäys
- [x] `candidates.json` - Ehdokkaiden perustiedot
- [x] Ehdokkaiden perusrakenteet

### 🏛️ Puolueiden Hallinta
- [x] `manage_parties.py` - Puolueiden hajautettu hallinta
- [x] `parties.json` - Puolueiden data-rakenne
- [x] Hajautettu vahvistus (3/3 kvoorumi)
- [x] `link_candidate_to_party.py` - Ehdokkaiden linkitys

### 🧪 Testaus ja Dokumentaatio
- [x] Testiskriptit puolueille ja ELO:lle
- [x] Järjestelmän tilaraportit

---

## 🚧 TEKIJÄLLÄ (🔨 KEHItyksessä)

### 📝 Ehdokkaiden Vastausten Hallinta
- [ ] `manage_answers.py` - Ehdokkaiden vastausten hallinta
- [ ] Vastausten validointi (-5 - +5 asteikolla)
- [ ] Perustelut monikielisinä
- [ ] Luottamustasot (1-5)

### 🌐 IPFS-Synkronointi
- [ ] `ipfs_sync.py` - Hajautettu datajako
- [ ] IPFS-client integraatio
- [ ] Mock-IPFS testausta varten
- [ ] Synkronointiprotokolla

---

## 📋 SEURAAVAT VAIHEET (⏳ ODOTTAA)

### 🎯 Vaalikoneen Ydin
- [ ] `voting_engine.py` - Varsinainen vaalikone
- [ ] Käyttäjän vastausten keräys
- [ ] Yhteensopivuuslaskenta
- [ ] Tulosten järjestely

### 🖥️ Käyttöliittymät
- [ ] Web-käyttöliittymä (Flask/FastAPI)
- [ ] CLI-käyttöliittymä (rich/click)
- [ ] Tulosten visualisointi

### 🔐 Tietoturva ja Integriteetti
- [ ] `integrity_manager.py` - Fingerprint-tarkistus
- [ ] Data-validointi
- [ ] Hajautettu varmennus

### 📈 Analytics ja Raportointi
- [ ] `election_analytics.py` - Vaalitilastot
- [ ] Tulosten analysointi
- [ ] Raporttien generointi

---

## 🎯 PRIORITEETIT

### 🥇 PRIORITEETTI 1 (Seuraavaksi)
1. **`manage_answers.py`** - Ehdokkaiden vastaukset
2. **`ipfs_sync.py`** - Hajautettu datajako

### 🥈 PRIORITEETTI 2 
3. **`voting_engine.py`** - Vaalikoneen ydin
4. **Web-käyttöliittymä** - Graafinen käyttöliittymä

### 🥉 PRIORITEETTI 3
5. **Tietoturva** - Integrity management
6. **Analytics** - Tilastot ja raportit

---

## 🏗️ TEKNISET TODET

### Tiedostorakenne
```
src/cli/
├── ✅ install.py              # Järjestelmän asennus
├── ✅ manage_questions.py     # Kysymysten hallinta  
├── ✅ manage_candidates.py    # Ehdokkaiden hallinta
├── ✅ manage_parties.py       # Puolueiden hallinta
├── ✅ compare_questions.py    # ELO-vertailu
├── ✅ elo_admin.py           # ELO-hallinta
├── ✅ link_candidate_to_party.py
├── 🔨 manage_answers.py      # EHDOKKAIDEN VASTAUKSET (SEURAAVA)
├── ⏳ ipfs_sync.py           # IPFS-synkronointi
├── ⏳ voting_engine.py       # Vaalikoneen ydin
└── ⏳ integrity_manager.py   # Tietoturva
```

### Data-tiedostot
```
data/runtime/
├── ✅ meta.json              # Järjestelmän metadata
├── ✅ system_chain.json      # Muutoshistoria
├── ✅ questions.json         # Kysymykset + ELO-luokitukset
├── ✅ candidates.json        # Ehdokkaat
├── ✅ parties.json           # Puolueet
├── 🔨 candidate_answers.json # EHDOKKAIDEN VASTAUKSET (SEURAAVA)
└── ⏳ ipfs_sync.json        # IPFS-synkronointitila
```

---

## 🎉 VIIMEISIMMÄT SAavutukset

### ✅ Just Valmistuneet
- **Puolueiden hajautettu hallinta** - Kvoorumi-järjestelmä
- **ELO-luokitus täysin toimiva** - Dynaaminen priorisointi
- **Ehdokkaat liitetty puolueisiin** - Täydellinen data-malli

### 🔄 Testaus Onnistui
- 3 noden vahvistus kvoorumi
- ELO-luokitukset muuttuvat vertailujen perusteella  
- Puolueiden tilastot ja raportointi
- Kaikki ehdokkaat linkitetty puolueeseen

---

## 🚀 NOPEA KÄYNNISTYS

```bash
# 1. Asenna järjestelmä
./scripts/setup_jumaltenvaalit.sh

# 2. Hallitse kysymyksiä
python src/cli/manage_questions.py --election Jumaltenvaalit2026 --add --category "aihe" --question-fi "Kysymys?"

# 3. Hallitse ehdokkaita
python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --add --name "Ehdokas"

# 4. Hallitse puolueita
python src/cli/manage_parties.py propose --election Jumaltenvaalit2026 --name-fi "Puolue"

# 5. Testaa ELO-järjestelmää
python src/cli/compare_questions.py --election Jumaltenvaalit2026 --choice a
```

---

## 💡 IDEoITA SEURAAVIIN OSAISIIN

### Ehdokkaiden Vastausten Rakenne
```json
{
  "candidate_id": "zeus",
  "answers": [
    {
      "question_id": "q_1",
      "answer_value": 5,
      "confidence": 5,
      "explanation": {
        "fi": "Salamat kuuluvat minulle!",
        "en": "Lightning bolts belong to me!",
        "sv": "Åskviggar tillhör mig!"
      }
    }
  ]
}
```

### IPFS-Synkronointi
- Mock-IPFS kehitystä varten
- Real-IPFS tuotantoon
- Hybrid-tila siirtymäajan

*Päivitetty: $(date)*
```

## 🎯 Nyt on selkeä suunnitelma eteenpäin!

### Seuraavat Vaiheet:

1. **`manage_answers.py`** - Ehdokkaiden vastaukset
2. **`ipfs_sync.py`** - Hajautettu datajako  
3. **`voting_engine.py`** - Vaalikoneen ydin

### Haluatko että aloitetaan nyt ehdokkaiden vastausten hallinnasta?

Se on loogisin seuraava askel koska:
- Sinulla on jo kysymykset, ehdokkaat ja puolueet
- Tarvitset vastaukset ennen kuin vaalikone voi toimia
- Se täydentää nykyistä data-mallia

Shall we create `manage_answers.py`? 🎯
