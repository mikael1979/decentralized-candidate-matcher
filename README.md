```markdown
# Hajautettu Vaalikone - Decentralized Candidate Matcher

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![IPFS](https://img.shields.io/badge/IPFS-Kubo%200.38.2-orange?logo=ipfs)](https://github.com/ipfs/kubo#install)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()

Hajautettu, yhteisöohjattu vaalikonejärjestelmä, joka käyttää ELO-luokitusjärjestelmää kysymysten priorisointiin ja automoderaatioon. Järjestelmä on suunniteltu tukemaan useita samanaikaisia vaaleja hajautetusti ilman keskitettyä hallintapalvelinta.

## 📋 Sisällysluettelo

- [Pääominaisuudet](#-pääominaisuudet)
- [Vaatimukset](#-vaatimukset)
- [Pika-aloitus](#🚀-pika-aloitus)
- [Käyttöopas](#📖-käyttöopas)
- [Config-järjestelmä](#⚙️-config-järjestelmä)
- [Analytics & Raportointi](#📊-analytics--raportointi)
- [IPFS-integrointi](#🌐-ipfs-integrointi)
- [Tietoturva](#🔒-tietoturva)
- [Vianetsintä](#🐛-vianetsintä)
- [Projektin Rakenne](#📁-projektin-rakente)
- [Tulevat Ominaisuudet](#🔮-tulevat-ominaisuudet)
- [Kehitykseen Osallistuminen](#🤝-kehitykseen-osallistuminen)
- [Lisenssi](#📄-lisenssi)

## 🎯 Pääominaisuudet

- **Hajautettu Arkkitehtuuri** – Ei single point of failure  
- **Config-järjestelmä** – Template-pohjainen konfiguraatio  
- **ELO-luokitusjärjestelmä** – Kysymysten laadun automaattinen arviointi  
- **PKI-turvajärjestelmä** – Ehdokkaiden ja puolueiden varmennus  
- **IPFS-integrointi** – Hajautettu datajako ja tallennus  
- **Reaaliaikainen analytics** – Vaalitilastot ja analyysit  
- **HTML-profiilit** – Automaattiset profiilisivut IPFS:ään  
- **Remove/Update toiminnot** – Täydellinen data-hallinta  

## 🛠️ Vaatimukses

- **Python 3.8** tai uudempi
- **IPFS Kubo 0.38.2** tai uudempi
- **2GB** vapaata muistia
- **1GB** levytilaa
- **Internet-yhteys** (IPFS-synkronointia varten)

## 🚀 Pika-aloitus

### 1. Asennus ja Alustus

```bash
# Kloonaa repositorio
git clone https://github.com/mikael1979/decentralized-candidate-matcher.git
cd decentralized-candidate-matcher

# Asenna riippuvuudet
pip install -r requirements.txt

# Alusta järjestelmä (tehdään vain kerran)
python src/cli/install.py --first-install --election-id "Olympos2024" --node-type coordinator
```

### 2. Peruskäyttö

```bash
# Config-järjestelmä muistaa vaalin automaattisesti!

# Lisää kysymys
python src/cli/manage_questions.py --add --question-fi "Pitäisikö salamavaltaa rajoittaa?" --category "Hallinto"

# Lisää ehdokas
python src/cli/manage_candidates.py --add --name-fi "Zeus" --party "Olympos"

# Lisää vastaus
python src/cli/manage_answers.py add --candidate-id zeus_001 --question-id q_hallinto_01 --answer 3 --confidence 4

# Käynnistä äänestys
python src/cli/voting_engine.py --start

# Näytä analytiikka
python src/cli/analytics.py wrapper
```

## 📖 Käyttöopas

### Vaalien Järjestäjille

```bash
# Alusta vaali
python src/cli/install.py --first-install --election-id "Olympos2024"

# Listaa kysymykset
python src/cli/manage_questions.py --list

# Vertaile kysymyksiä ELO-perusteella
python src/cli/compare_questions.py --auto 10

# Tarkista järjestelmän tila
python src/cli/analytics.py wrapper
```

### Puolueille & Ehdokkaille

```bash
# Rekisteröi ehdokas
python src/cli/manage_candidates.py --add --name-fi "Athena" --party "Olympos"

# Lisää vastauksia
python src/cli/manage_answers.py add --candidate-id athena_002 --question-id q_sota_01 --answer 5 --confidence 5

# Päivitä profiili
python src/cli/manage_candidates.py --update athena_002 --name-fi "Athena Parhenos"
```

### Äänestäjille

```bash
# Osallistu äänestykseen
python src/cli/voting_engine.py --start

# Katso tulokset
python src/cli/voting_engine.py --results session_olympos_20241201_120000

# Selaa analytiikkaa
python src/cli/analytics.py wrapper
```

### Data-hallinta

```bash
# Päivitä kysymys
python src/cli/manage_questions.py --update q_hallinto_01 --question-fi "Pitäisikö ukkoseniskuoikeuksia rajoittaa?"

# Poista ehdokas
python src/cli/manage_candidates.py --remove ares_003

# Poista vastaus
python src/cli/manage_answers.py remove --candidate-id zeus_001 --question-id q_hallinto_01
```

## ⚙️ Config-järjestelmä

Järjestelmä käyttää template-pohjaista config-järjestelmää:

```json
{
  "metadata": {
    "election_id": "Olympos2024",
    "created": "2024-01-15T10:30:00Z",
    "version": "1.0.0",
    "config_hash": "olympos_config_001",
    "template_hash": "base_template_v1"
  },
  "election_config": {
    "answer_scale": {"min": -5, "max": 5, "step": 1},
    "confidence_scale": {"min": 1, "max": 5, "step": 1},
    "max_questions": 50,
    "max_candidates": 12,
    "languages": ["fi", "en", "sv", "gr"]  # gr = muinaiskreikka
  }
}
```

## 📊 Analytics & Raportointi

```bash
python src/cli/analytics.py wrapper
```

**Raportti sisältää:**
- ✅ Järjestelmän tila (healthy / needs_attention)
- 📈 Data-tilastot (kysymykset, ehdokkaat, vastaukset)
- 🏆 Kysymysten ELO-jakauma
- 🔧 Konkreettiset suositukset puutteiden korjaamiseksi
- 📋 Terveysindikaattorit

## 🌐 IPFS-integrointi

```bash
# Config julkaistaan automaattisesti asennuksessa
python src/cli/install.py --first-install --election-id "Olympos2024"

# Julkaise kaikki profiilit IPFS:ään
python src/cli/generate_profiles.py publish-all-to-ipfs

# Synkronoi data IPFS-verkkoon
python src/cli/ipfs_sync.py --status
```

## 🔒 Tietoturva

- **Data Validointi** - Kaikki vastaukset validoitu (−5…+5, varmuus 1…5)
- **Eheysvarmistus** - Data-eheys varmistettu `system_chain.json`:llä
- **Hash-fingerprint** - Configin muutosten seuranta
- **CID-tarkistus** - IPFS-pohjainen eheystarkistus
- **PKI-todennus** - Ehdokkaiden ja puolueiden varmennus

## 🐛 Vianetsintä

### Yleisimmät ongelmat

**Config ei lataa:**
```bash
rm config/active_election.json
python src/cli/install.py --first-install --election-id "Asgard2024"
```

**IPFS-yhteysongelma:**
```bash
# Käynnistä IPFS-daemon
ipfs daemon

# Tarkista yhteys
python src/cli/ipfs_sync.py --status
```

**Data-eheysongelma:**
```bash
# Tarkista data-eheys
python src/cli/validate_data.py --full-check

# Korjaa system_chain
python src/cli/validate_data.py --repair
```

## 📁 Projektin Rakenne

```
src/
├── cli/                    # Komentorivityökalut
│   ├── install.py              # Järjestelmän asennus + config
│   ├── voting_engine.py        # Vaalikoneen ydin
│   ├── analytics.py            # Analytics & raportointi
│   ├── manage_questions.py     # Kysymysten hallinta (add/remove/update)
│   ├── manage_candidates.py    # Ehdokkaiden hallinta (add/remove/update)  
│   ├── manage_answers.py       # Vastausten hallinta (add/remove/update)
│   ├── manage_parties.py       # Puolueiden hallinta
│   ├── compare_questions.py    # ELO-vertailu
│   ├── elo_admin.py            # ELO-hallinta
│   ├── ipfs_sync.py            # IPFS-synkronointi
│   ├── generate_profiles.py    # HTML-profiilit
│   └── validate_data.py        # Data-validointi
├── core/                    # Ydintoiminnallisuudet
│   ├── config_manager.py       # Config-hallinta
│   ├── ipfs_client.py          # IPFS-integrointi
│   ├── file_utils.py           # Tiedostotyökalut
│   ├── data_validator.py       # Data-validointi
│   └── ipfs/                   # Modulaarinen IPFS
│       ├── archive_manager.py   # Arkistointi
│       ├── delta_manager.py     # Muutosten seuranta
│       └── sync_orchestrator.py # Synkronointi
└── templates/               # Templatet
    └── config.base.json        # Config template
```

## 🔮 Tulevat Ominaisuudet

- [ ] **Multinode-hajautus** - Hajautettu arkkitehtuuri useille nodeille
- [ ] **Moderni React-web-käyttöliittymä** - Graafinen käyttöliittymä
- [ ] **Reaaliaikainen tulospalvelu** - Live-tulokset
- [ ] **Mobiilisovellus** - Äänestys mobiililaitteilla
- [ ] **Blockchain-integrointi** - Lisäeheystakuu (valinnainen)
- [ ] **Käännöstoiminnot** - Laajempi kielituki (mukaan lukien muinaiskreikka)
- [ ] **API-rajapinta** - Kolmannen osapuolen integraatiot

## 🤝 Kehitykseen Osallistuminen

1. **Forkkaa** repositorio
2. **Luo feature-haara**: 
   ```bash
   git checkout -b feature/oma-ominaisuus
   ```
3. **Tee muutokset** ja testaa
4. **Commitoi** muutokset:
   ```bash
   git commit -am 'Lisää uusi ominaisuus: kuvaus'
   ```
5. **Pushaa** haara:
   ```bash
   git push origin feature/oma-ominaisuus
   ```
6. **Avaa Pull Request**

### Testaus

```bash
# Suorita perustestit
python tests/test_config_manager.py

# Täydellinen testirundi
python src/cli/install.py --first-install --election-id "Testivaalit2024" --node-type coordinator
python src/cli/manage_questions.py --add --question-fi "Testikysymys"
python src/cli/manage_candidates.py --add --name-fi "Testiehdokas"
python src/cli/analytics.py wrapper
python src/cli/voting_engine.py --start
```

## 📄 Lisenssi

Apache License 2.0 - Katso [LICENSE](LICENSE) tiedosto lisätietoja varten.

---

<div align="center">

## 🎉 TUOTANTOVALMIS!

**Demokratia koodiksi – Hajautettu vaalikone käyttövalmiina**

*"Yksinkertaisemmat komennot, tehokkaampi demokratia"*

**🏛️ Olympos-vaalit 2024 - Järjestelmä käynnissä!**

</div>
```
