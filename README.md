
# 🏛️ Hajautettu Vaalikonejärjestelmä

**Modulaarinen, hajautettu vaalikonejärjestelmä** joka yhdistää ELO-luokituksen, IPFS-synkronoinnin ja hajautetun puoluevahvistuksen.

## ✨ Ominaisuudet

### ✅ Toteutetut
- 🎯 **ELO-luokitusjärjestelmä** - Kysymysten priorisointi yhteisön vertailuilla
- 👑 **Ehdokkaiden hallinta** - Ehdokkaiden perustiedot ja puolueiden linkitys  
- 🏛️ **Hajautettu puoluerekisteri** - 3 noden kvoorumi vahvistukseen
- 📊 **Tilastot ja raportointi** - ELO-rankingit ja puoluetilastot
- 🔄 **Modulaarinen rakenne** - Helppo laajennettavuus
- 🌐 **IPFS-integrointi** - Hajautettu datajako (Kubo 0.38.2 yhteensopiva)
- 📝 **Ehdokkaiden vastausten hallinta** - Vastaukset ja perustelut (-5 - +5 asteikolla)
- 🔐 **PKI-turvajärjestelmä** - Ehdokkaiden identiteetin varmennus
- 🎨 **HTML-profiilien generointi** - IPFS-julkaisut puolueille ja ehdokkaille
- 📈 **Analytics ja raportointi** - Vaalitilastot ja analyysit
- 🔧 **Data validointi** - JSON-skeemat ja eheystarkistukset

### 🔨 Kehityksessä
- 🖥️ **Moninode-järjestelmä** - Hajautettu arkkitehtuuri
- 🎰 **Vaalikoneen ydinmoottori** - Varsinainen vaalikone
- 🔄 **Verkkosynkronointi** - Useiden nodien välinen datajako

### ⏳ Suunnitellut
- 🌐 **Web-käyttöliittymä** - Moderni React-sovellus
- 📱 **Mobiili-sovellus** - Natiivit sovellukset
- 🔐 **Blockchain-integrointi** - Edistyneet turvatoimet

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
# Asenna testivaali master-nodena
python src/cli/install.py --election-id Jumaltenvaalit2026 --first-install

# Tai asenna worker-nodena
python src/nodes/worker/election_installer.py --election Jumaltenvaalit2026
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

### 4. Hallinnoi Ehdokkaita ja Puolueita
```bash
# Lisää ehdokas
python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --add \
  --name "Zeus" --party "Olympolaiset"

# Ehdotta uusi puolue
python src/cli/manage_parties.py propose --election Jumaltenvaalit2026 \
  --name-fi "Olympolaiset" --name-en "Olympians"

# Vahvista puolue (tarvitaan 3 nodea)
python src/cli/enhanced_party_verification.py --election Jumaltenvaalit2026 \
  --party-id party_001 --verify

# Liitä ehdokas puolueeseen
python src/cli/link_candidate_to_party.py --election Jumaltenvaalit2026 \
  --candidate-id cand_1 --party-id party_001
```

### 5. Hallinnoi Vastauksia
```bash
# Lisää ehdokkaan vastaus
python src/cli/manage_answers.py --election Jumaltenvaalit2026 \
  --candidate-id cand_1 --question-id q_1 --answer 3 \
  --explanation-fi "Olen melko samaa mieltä" --confidence 4

# Tarkista vastaukset
python src/cli/manage_answers.py --election Jumaltenvaalit2026 --list
```

### 6. IPFS ja Profiilit
```bash
# Synkronoi data IPFS:ään
python src/cli/ipfs_sync.py sync --election Jumaltenvaalit2026

# Generoi HTML-profiilit
python src/cli/generate_profiles.py publish-all-to-ipfs --election Jumaltenvaalit2026

# Tarkista profiilien tila
python src/cli/generate_profiles.py status --election Jumaltenvaalit2026
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
│   │   ├── manage_answers.py       # Vastausten hallinta
│   │   ├── compare_questions.py    # ELO-vertailu
│   │   ├── elo_admin.py           # ELO-hallinta
│   │   ├── ipfs_sync.py           # IPFS-synkronointi
│   │   ├── analytics.py           # Analytics
│   │   ├── generate_profiles.py   # HTML-profiilit
│   │   ├── validate_data.py       # Data validointi
│   │   ├── candidate_credentials.py # PKI-turva
│   │   └── enhanced_party_verification.py
│   ├── core/               # Ydinkirjasto
│   │   ├── ipfs_client.py         # IPFS-integrointi
│   │   ├── file_utils.py          # Tiedostotoiminnot
│   │   ├── config_manager.py      # Konfiguraatio
│   │   └── election_validator.py  # Vaalivalidaatio
│   ├── managers/           # Järjestelmän hallinta
│   │   ├── question_manager.py    # Kysymysten elinkaari
│   │   ├── elo_manager.py         # ELO-laskenta
│   │   ├── crypto_manager.py      # Kryptografia
│   │   ├── ipfs_manager.py        # IPFS-hallinta
│   │   ├── analytics_manager.py   # Analytics
│   │   └── quorum_manager.py      # Kvoorumiäänestys
│   ├── nodes/              # Hajautettu arkkitehtuuri
│   │   ├── node_manager.py        # Solmujen hallinta
│   │   ├── network_sync.py        # Verkkosynkronointi
│   │   ├── quorum_voting.py       # Hajautettu äänestys
│   │   └── worker/election_installer.py
│   └── templates/          # HTML-generointi
│       ├── html_generator.py      # HTML-template-järjestelmä
│       └── base_template.css      # CSS-tyylit
├── base_templates/         # JSON-pohjat
├── data/                  # Data-tiedostot
│   ├── runtime/           # Käyttödata
│   ├── nodes/             # Node-data
│   └── backup/            # Varmuuskopiot
├── scripts/               # Apuskriptit
├── tests/                 # Testit
└── config/                # Konfiguraatiot
```

### Data-malli
```json
// questions.json - Kysymykset + ELO-luokitukset
{
  "questions": [
    {
      "local_id": "q_1",
      "content": {
        "category": {"fi": "hallinto", "en": "governance", "sv": "förvaltning"},
        "question": {"fi": "...", "en": "...", "sv": "..."}
      },
      "elo_rating": {
        "current_rating": 1050,
        "comparison_delta": 16,
        "vote_delta": 0
      }
    }
  ]
}

// candidate_answers.json - Ehdokkaiden vastaukset
{
  "cand_1": {
    "q_1": {
      "answer_value": 3,
      "explanation": {
        "fi": "Olen melko samaa mieltä",
        "en": "I somewhat agree",
        "sv": "Jag håller delvis med"
      },
      "confidence": 4
    }
  }
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

# ELO-tilastot ja rankingit
python src/cli/elo_admin.py leaderboard --election Jumaltenvaalit2026
python src/cli/elo_admin.py stats --election Jumaltenvaalit2026
```

## 🏛️ Hajautettu Puoluevahvistus

Puolueet vahvistetaan hajautetusti:

- **3 noden kvoorumi** vaaditaan vahvistukseen
- **Jokainen node äänestää** puolueen hyväksymisestä/hylkäämisestä
- **PKI-turvajärjestelmä** varmistaa identiteetin
- **Täysi läpinäkyvyys** - kaikki tapahtumat lokitetaan

```bash
# Seuraa puolueiden tilaa
python src/cli/manage_parties.py stats --election Jumaltenvaalit2026
python src/cli/party_stats.py --election Jumaltenvaalit2026
```

## 🌐 IPFS-integrointi

Järjestelmä käyttää IPFS:ää hajautettuun datajakoon:

- **Täysi yhteensopivuus** IPFS Kubo 0.38.2:n kanssa
- **Mock-IPFS** testausta varten
- **HTML-profiilit** saatavilla IPFS-verkossa
- **Automaattinen synkronointi** useiden nodien välillä

```bash
# IPFS-statustarkistus
python src/cli/ipfs_sync.py status --election Jumaltenvaalit2026

# Synkronoi data
python src/cli/ipfs_sync.py sync --election Jumaltenvaalit2026
```

## 🎨 HTML-profiilit

Järjestelmä generoi automaattisesti HTML-profiilit puolueille ja ehdokkaille:

- **Väriteemat** puoluekohtaiset värit
- **IPFS-julkaisu** profiilit saatavilla verkossa
- **Responsiivinen design** mobiiliystävällinen
- **Monikielisyys** suomi, englanti, ruotsi

```bash
# Generoi kaikki profiilit
python src/cli/generate_profiles.py publish-all-to-ipfs --election Jumaltenvaalit2026

# Listaa saatavilla olevat profiilit
python src/cli/generate_profiles.py status --election Jumaltenvaalit2026
```

## 🔐 Tietoturva

Järjestelmä käyttää PKI-pohjaista turvajärjestelmää:

- **Ehdokkaiden sertifikaatit** - Identiteetin varmennus
- **Digitaaliset allekirjoitukset** - Vastausten autenttisuus
- **Hajautettu vahvistus** - Estää keskitetyn vallan

```bash
# Luo ehdokkaalle sertifikaatit
python src/cli/candidate_credentials.py --election Jumaltenvaalit2026 \
  --candidate-id cand_1 --generate

# Vahvista ehdokas
python src/cli/candidate_credentials.py --election Jumaltenvaalit2026 \
  --candidate-id cand_1 --verify
```

## 🧪 Testaa Järjestelmää

```bash
# Suorita yksikkötestit
python -m pytest tests/unit/

# Suorita integraatiotestit
python -m pytest tests/integration/

# Tarkista järjestelmän tila
./scripts/system_status.sh
./scripts/party_summary.sh

# Testaa ELO-järjestelmää
./scripts/test_elo_system.sh
```

## 📈 Analytics ja Raportointi

```bash
# ELO-tilastot
python src/cli/elo_admin.py stats --election Jumaltenvaalit2026

# Puoluetilastot  
python src/cli/party_stats.py --election Jumaltenvaalit2026

# Analytics-raportit
python src/cli/analytics.py --election Jumaltenvaalit2026

# Data validointi
python src/cli/validate_data.py --election Jumaltenvaalit2026
```

## 🔮 Tulevat Ominaisuudet

### 🥇 PRIORITEETTI 1 (Seuraavaksi)
- [ ] 🖥️ **Moninode-järjestelmän viimeistely** - Hajautettu arkkitehtuuri
- [ ] 🎰 **Vaalikoneen ydinmoottori** - Varsinainen vaalikone

### 🥈 PRIORITEETTI 2 
- [ ] 🌐 **Web-käyttöliittymä** - Graafinen käyttöliittymä
- [ ] 📊 **Tulosten visualisointi** - Käyttäjäystävälliset raportit

### 🥉 PRIORITEETTI 3
- [ ] 🧪 **Laajamittainen testaus** - Skaalautuvuustestit
- [ ] 📚 **Dokumentaatio** - Käyttöohjeet ja API-dokumentaatio

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

# Testaa IPFS-yhteys
python test_ipfs.py
```

🚀 Template-editori:
🎯 Pääominaisuudet:
📄 HTML/CSS Analyysi - Analysoi olemassa olevat verkkosivut

🛡️ Turvallisuussuodatus - Poistaa JavaScriptin ja XSS-uhkat

🎨 Väriteeman tunnistus - Ehdota värejä automaattisesti

📝 JSON-template generointi - Luo JSON-templateja

👁️ Esikatselu - Testaa templateja ennen käyttöönottoa

🔧 Käyttötavat:
bash
# Komentorivikäyttö
```bash
python -m src.tools.template_editor.editor --html verkkosivu.html --css tyylit.css --preview

# Ohjelmallinen käyttö
from src.tools.template_editor.editor import TemplateEditor
editor = TemplateEditor()
result = editor.create_template_from_website("sivu.html", "tyylit.css")
```
## 🤝 Osallistu Kehitykseen

1. **Tutki koodia**: `src/` hakemisto sisältää kaiken lähdekoodin
2. **Testaa järjestelmää**: Käytä testiskriptejä `scripts/`
3. **Raportoi bugeja**: Käytä GitHub Issues -osiota
4. **Ehdä parannuksia**: Forkkaa ja tee pull request

## 📄 Lisenssi

Tämä projekti on lisensoitu **Apache License 2.0** -lisenssillä. 

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Katso [LICENSE](LICENSE) tiedosto täydellistä lisenssitekstiä varten.

---

**Jumaltenvaalit 2026 on käynnissä!** 🏛️⚡

*"Demokratia koodiksi - yhteisö luo, äänestää ja moderoi kysymyksiä hajautetusti"*
```

