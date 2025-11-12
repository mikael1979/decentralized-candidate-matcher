## 📝 Päivitetty README.md

**README.md**:
```markdown
# 🏛️ Hajautettu Vaalikonejärjestelmä

**Modulaarinen, hajautettu vaalikonejärjestelmä** joka yhdistää ELO-luokituksen, IPFS-synkronoinnin ja hajautetun puoluevahvistuksen.

## ✨ Ominaisuudet

### ✅ Toteutetut
- 🎯 **ELO-luokitusjärjestelmä** - Kysymysten priorisointi yhteisön vertailuilla
- 👑 **Ehdokkaiden hallinta** - Ehdokkaiden perustiedot ja puolueiden linkitys  
- 🏛️ **Hajautettu puoluerekisteri** - 3 noden kvoorumi vahvistukseen
- 📊 **Tilastot ja raportointi** - ELO-rankingit ja puoluetilastot
- 🔄 **Modulaarinen rakenne** - Helppo laajennettavuus

### 🔨 Kehityksessä
- 📝 Ehdokkaiden vastausten hallinta
- 🌐 IPFS-synkronointi
- 🎰 Vaalikoneen ydinmoottori

## 🚀 Nopea Aloitus

### 1. Asenna Järjestelmä
```bash
# Kloonaa ja asenna
git clone <repository-url>
cd decentralized-candidate-matcher

# Asenna riippuvuudet
./scripts/setup.sh

# Aktivoi virtuaaliympäristö
source venv/bin/activate
```

### 2. Asenna Jumaltenvaalit 2026 (Testivaali)
```bash
# Asenna testivaali
python src/cli/install.py --election-id Jumaltenvaalit2026 --first-install
```

### 3. Hallinnoi Kysymyksiä
```bash
# Lisää kysymys
python src/cli/manage_questions.py --election Jumaltenvaalit2026 --add \
  --category "hallinto" \
  --question-fi "Pitäisikö Zeusin salamaniskuoikeuksia rajoittaa?"

# Vertaile kysymyksiä (ELO-luokitus)
python src/cli/compare_questions.py --election Jumaltenvaalit2026

# Näytä ELO-tilastot
python src/cli/elo_admin.py stats --election Jumaltenvaalit2026
```

### 4. Hallinnoi Ehdokkaita
```bash
# Lisää ehdokas
python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --add \
  --name "Zeus" \
  --party "Olympolaiset"

# Listaa ehdokkaat
python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --list
```

### 5. Hallinnoi Puolueita
```bash
# Ehdotta uusi puolue
python src/cli/manage_parties.py propose --election Jumaltenvaalit2026 \
  --name-fi "Olympolaiset" \
  --name-en "Olympians" \
  --email "zeus@olympos.gr"

# Vahvista puolue (tarvitaan 3 nodea)
python src/cli/manage_parties.py verify --election Jumaltenvaalit2026 \
  --party-id party_001 --node-id node_001 --verify --reason "Hyvä puolue"

# Liitä ehdokas puolueeseen
python src/cli/link_candidate_to_party.py --election Jumaltenvaalit2026 \
  --candidate-id cand_1 --party-id party_001
```

## 🏗️ Arkkitehtuuri

### Hakemistorakenne
```
decentralized-candidate-matcher/
├── src/
│   ├── cli/                 # Komentorivityökalut
│   │   ├── install.py              # Järjestelmän asennus
│   │   ├── manage_questions.py     # Kysymysten hallinta
│   │   ├── manage_candidates.py    # Ehdokkaiden hallinta
│   │   ├── manage_parties.py       # Puolueiden hallinta
│   │   ├── compare_questions.py    # ELO-vertailu
│   │   ├── elo_admin.py           # ELO-hallinta
│   │   └── link_candidate_to_party.py
│   ├── core/               # Ydinkirjasto
│   └── managers/           # Järjestelmän hallinta
├── base_templates/         # JSON-pohjat
├── data/runtime/           # Data-tiedostot
├── scripts/               # Apuskriptit
└── tests/                 # Testit
```

### Data-malli
```json
// questions.json - Kysymykset + ELO-luokitukset
{
  "questions": [
    {
      "local_id": "q_1",
      "content": {"category": "hallinto", "question": {"fi": "...", "en": "...", "sv": "..."}},
      "elo_rating": {"current_rating": 1050, "comparison_delta": +16}
    }
  ]
}

// parties.json - Hajautettu puoluerekisteri
{
  "parties": [
    {
      "party_id": "party_001",
      "name": {"fi": "Olympolaiset", "en": "Olympians", "sv": "Olympierna"},
      "registration": {
        "verification_status": "verified",
        "verified_by": ["node_001", "node_002", "node_003"]
      },
      "candidates": ["cand_1", "cand_2"]
    }
  ]
}
```

## 🎯 ELO-Luokitusjärjestelmä

Järjestelmä käyttää ELO-luokitusjärjestelmää kysymysten priorisointiin:

- **Käyttäjät vertailevat** kahta satunnaista kysymystä
- **Voittaja saa pisteitä**, häviäjä menettää
- **Luokitukset muuttuvat** dynaamisesti yhteisön mielipiteiden mukaan
- **Korkeimmat luokitukset** valitaan aktiivisiin kysymyksiin

```bash
# Käytä ELO-järjestelmää
python src/cli/compare_questions.py --election Jumaltenvaalit2026
python src/cli/elo_admin.py leaderboard --election Jumaltenvaalit2026
```

## 🏛️ Hajautettu Puoluevahvistus

Puolueet vahvistetaan hajautetusti:

- **3 noden kvoorumi** vaaditaan vahvistukseen
- **Jokainen node äänestää** puolueen hyväksymisestä/hylkäämisestä
- **Täysi läpinäkyvyys** - kaikki tapahtumat lokitetaan
- **Estää keskitetyn vallan** puolueiden hyväksynnässä

```bash
# Seuraa puolueiden tilaa
python src/cli/manage_parties.py stats --election Jumaltenvaalit2026
python src/cli/manage_parties.py list --election Jumaltenvaalit2026 --show-pending
```

## 🧪 Testaa Järjestelmää

```bash
# Suorita kattava testi
./scripts/test_elo_system.sh
./scripts/test_party_system.sh

# Tarkista järjestelmän tila
./scripts/system_status.sh
./scripts/party_summary.sh
```

## 📈 Tilastot ja Raportointi

```bash
# ELO-tilastot
python src/cli/elo_admin.py stats --election Jumaltenvaalit2026

# Puoluetilastot  
python src/cli/manage_parties.py stats --election Jumaltenvaalit2026

# Järjestelmän yleisnäkymä
./scripts/system_status.sh
```

## 🔮 Tulevat Ominaisuudet

### Lyhyellä Aikavälillä
- [ ] 📝 Ehdokkaiden vastausten hallinta
- [ ] 🌐 IPFS-synkronointi
- [ ] 🎰 Vaalikoneen ydinmoottori

### Pitkällä Aikavälillä  
- [ ] 🔐 Tietoturva ja integrity management
- [ ] 🖥️ Web-käyttöliittymä
- [ ] 📊 Analytics ja raportointi
- [ ] 🌍 Monikielisyys ja lokalisaatio

## 🐛 Ongelmatilanteet

### Yleisimmät ongelmat
```bash
# Virtuaaliympäristö ei aktiivinen
source venv/bin/activate

# Puuttuvat riippuvuudet
pip install -r requirements.txt

# Data-tiedostot puuttuvat
python src/cli/install.py --election-id Jumaltenvaalit2026 --first-install
```

### Debuggausta
```bash
# Tarkista data-tiedostot
ls -la data/runtime/

# Tarkista järjestelmän tila
python scripts/debug_elo.py
```

## 🤝 Osallistu Kehitykseen

1. **Tutki koodia**: `src/` hakemisto sisältää kaiken lähdekoodin
2. **Testaa järjestelmää**: Käytä testiskriptejä `scripts/`
3. **Raportoi bugeja**: Käytä GitHub Issues -osiota
4. **Ehdä parannuksia**: Forkkaa ja tee pull request

## 📄 Lisenssi

Tämä projekti on kehitysvaiheessa. Kaikki tiedot testausdataa varten.

---

**Jumaltenvaalit 2026 on käynnissä!** 🏛️⚡

*"Demokratia koodiksi - yhteisö luo, äänestää ja moderoi kysymyksiä hajautetusti"*
```


