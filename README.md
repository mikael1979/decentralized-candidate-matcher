```markdown
# Hajautettu Vaalikone - Decentralized Candidate Matcher

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![IPFS Compatible](https://img.shields.io/badge/IPFS-Kubo%200.38.2-green.svg)](https://docs.ipfs.tech/)

Hajautettu, yhteisöohjattu vaalikonejärjestelmä, joka käyttää ELO-luokitusjärjestelmää kysymysten priorisointiin ja automoderaatioon. Järjestelmä on suunniteltu tukemaan useita samanaikaisia vaaleja hajautetusti ilman keskitettyä hallintapalvelinta.

## Pääominaisuudet

- **Hajautettu Arkkitehtuuri** – Ei single point of failure  
- **Config-järjestelmä** – Template-pohjainen konfiguraatio  
- **ELO-luokitusjärjestelmä** – Kysymysten laadun automaattinen arviointi  
- **PKI-turvajärjestelmä** – Ehdokkaiden ja puolueiden varmennus  
- **IPFS-integrointi** – Hajautettu datajako ja tallennus  
- **Reaaliaikainen analytics** – Vaalitilastot ja analyysit  
- **HTML-profiilit** – Automaattiset profiilisivut IPFS:ään  
- **Remove/Update toiminnot** – Täydellinen data-hallinta  

## TUOTANTOVALMIS!

Järjestelmä on nyt täysin tuotantovalmis ja sisältää:
- **Config-järjestelmä** – Template-pohjainen konfiguraatio  
- **Vaalikoneen ydin** – Täysin toimiva voting engine  
- **Analytics & raportointi** – Kattava tilasto- ja terveysraportointi  
- **Data-hallinta** – CRUD-toiminnot kaikille data-tyypeille  
- **IPFS-tuki** – Configin ja profiilien julkaisu  

## Projektin Rakenne

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
│   ├── config_manager.py       # Config-hallinta (UUSI)
│   ├── ipfs_client.py          # IPFS-integrointi
│   ├── file_utils.py           # Tiedostotyökalut
│   ├── data_validator.py       # Data-validointi
│   └── ipfs/                   # Modulaarinen IPFS
│       ├── archive_manager.py   # Arkistointi
│       ├── delta_manager.py     # Muutosten seuranta
│       └── sync_orchestrator.py # Synkronointi
└── templates/               # Templatet
    └── config.base.json        # Config template (UUSI)
```

## Config-järjestelmä (UUSI!)

Järjestelmä käyttää nyt template-pohjaista config-järjestelmää:

```json
{
  "metadata": {
    "election_id": "Jumaltenvaalit2026",
    "config_hash": "abc123...",
    "template_hash": "def456..."
  },
  "election_config": {
    "answer_scale": {"min": -5, "max": 5},
    "confidence_scale": {"min": 1, "max": 5},
    "max_questions": 50,
    "max_candidates": 200
  }
}
```

## Pika-aloitus

### 1. Asennus ja Config

```bash
git clone https://github.com/mikael1979/decentralized-candidate-matcher.git
cd decentralized-candidate-matcher
pip install -r requirements.txt

# Alusta järjestelmä ja luo config (tehdään vain kerran)
python src/cli/install.py --first-install --election-id Jumaltenvaalit2026 --node-type coordinator
```

### 2. Peruskäyttö (EI enää --election -parametria!)

```bash
# Config-järjestelmä muistaa vaalin automaattisesti!

python src/cli/manage_questions.py --add --question-fi "Pitäisikö hiilidioksidipäästöjä vähentää?" --category "Ympäristö"
python src/cli/manage_candidates.py --add --name-fi "Matti Meikäläinen" --party "Vihreä liitto"
python src/cli/manage_answers.py add --candidate-id cand_abc123 --question-id q_xyz789 --answer 3 --confidence 4

python src/cli/voting_engine.py --start
python src/cli/analytics.py wrapper
```

### 3. Data-hallinta (Uudet remove/update-toiminnot!)

```bash
python src/cli/manage_questions.py --update q_abc123 --question-fi "Päivitetty kysymys"
python src/cli/manage_candidates.py --update cand_xyz --name-fi "Uusi nimi"
python src/cli/manage_answers.py remove --candidate-id cand_abc123 --question-id q_xyz789
python src/cli/manage_questions.py --remove q_abc123
```

## Käyttötapaukset

### Vaalien järjestäjille
```bash
python src/cli/install.py --first-install --election-id Jumaltenvaalit2026
python src/cli/manage_questions.py --list
python src/cli/compare_questions.py --auto 10
python src/cli/analytics.py wrapper
```

### Puolueille & ehdokkaille
```bash
python src/cli/manage_candidates.py --add --name-fi "Ehdokas Nimi" --party "Oma Puolue"
python src/cli/manage_answers.py add --candidate-id cand_123 --question-id q_456 --answer 5 --confidence 5
```

### Äänestäjille
```bash
python src/cli/voting_engine.py --start
python src/cli/voting_engine.py --results session_20251120_120000
python src/cli/analytics.py wrapper
```

## Analytics & Terveysraportti

```bash
python src/cli/analytics.py wrapper
```

Sisältää:
- Järjestelmän tilan (healthy / needs_attention)
- Data-tilastot
- Kysymysten ELO-jakauma
- Konkreettiset suositukset puutteiden korjaamiseksi

## IPFS-integrointi

```bash
# Config julkaistaan automaattisesti asennuksessa
python src/cli/install.py --first-install --election-id Jumaltenvaalit2026

# Julkaise kaikki profiilit IPFS:ään
python src/cli/generate_profiles.py publish-all-to-ipfs
```

## Testaus

```bash
python tests/test_config_manager.py

# Tai täydellinen pikatestirundi
python src/cli/install.py --first-install --election-id Jumaltenvaalit2026 --node-type coordinator
python src/cli/manage_questions.py --add --question-fi "Testikysymys"
python src/cli/manage_candidates.py --add --name-fi "Testiehdokas"
python src/cli/analytics.py wrapper
python src/cli/voting_engine.py --start
```

## Tietoturva & Eheys

- Kaikki vastaukset validoitu (−5…+5, varmuus 1…5)
- Data-eheys varmistettu `system_chain.json`:llä
- Configin hash-fingerprint
- IPFS CID-pohjainen eheystarkistus

## Tulevat Ominaisuudet

- [ ] Moninode-hajautus
- [ ] Moderni React-web-käyttöliittymä
- [ ] Reaaliaikainen tulospalvelu
- [ ] Mobiilisovellus
- [ ] Blockchain-integrointi (valinnainen)

## Osallistu Kehitykseen

1. Forkkaa repo
2. Luo feature-haara (`git checkout -b feature/oma-ominaisuus`)
3. Commitoi (`git commit -am 'Kuvaus muutoksesta'`)
4. Pushaa & avaa Pull Request

## Lisenssi

Apache License 2.0 – katso [LICENSE](LICENSE)

---

<div align="center">

**Demokratia koodiksi – Config-järjestelmä valmis, tuotanto käynnissä!**

*"Yksinkertaisemmat komennot, tehokkaampi demokratia"*

</div>
```


