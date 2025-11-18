# 🏛️ Hajautettu Vaalikone - Decentralized Candidate Matcher

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![IPFS Compatible](https://img.shields.io/badge/IPFS-Kubo%200.38.2-green.svg)](https://docs.ipfs.tech/)

Hajautettu, yhteisöohjattu vaalikonejärjestelmä, joka käyttää ELO-luokitusjärjestelmää kysymysten priorisointiin ja automoderaatioon. Järjestelmä on suunniteltu tukemaan useita samanaikaisia vaaleja hajautetusti ilman keskitettyä hallintapalvelinta.

## 🌟 Pääominaisuudet

- **🎯 Hajautettu Arkkitehtuuri** - Ei single point of failure
- **🏅 ELO-luokitusjärjestelmä** - Kysymysten laadun automaattinen arviointi
- **🔐 PKI-turvajärjestelmä** - Ehdokkaiden ja puolueiden varmennus
- **🌐 IPFS-integrointi** - Hajautettu datajako ja tallennus
- **📊 Reaaliaikainen analytics** - Vaalitilastot ja analyysit
- **🎨 HTML-profiilit** Automaattiset profiilisivut IPFS:ään
- **👥 Moninode-tuki** Useat solmut samalle vaalille

## 🏗️ Projektin Rakenne

```
src/
├── cli/                    # Komentorivityökalut
│   ├── install.py              # Järjestelmän asennus
│   ├── manage_questions.py     # Kysymysten hallinta  
│   ├── manage_candidates.py    # Ehdokkaiden hallinta
│   ├── manage_parties.py       # Puolueiden hallinta
│   ├── manage_answers.py       # Vastausten hallinta
│   ├── compare_questions.py    # ELO-vertailu
│   ├── elo_admin.py           # ELO-hallinta
│   ├── link_candidate_to_party.py
│   ├── ipfs_sync.py           # IPFS-synkronointi
│   ├── analytics.py           # Analytics
│   ├── generate_profiles.py   # HTML-profiilit
│   ├── node_management.py     # Solmujen hallinta
│   ├── answer_validation.py   # Vastausten validointi
│   ├── answer_reports.py      # Raportointi
│   ├── party_verification.py  # Puolueiden vahvistus
│   ├── candidate_credentials.py # Ehdokkaiden tunnistus
│   └── publish_election_configs.py
├── core/                    # Ydintoiminnallisuudet
│   ├── ipfs_client.py          # IPFS-integrointi
│   ├── pki_manager.py          # PKI-turvajärjestelmä
│   ├── validators.py           # Validaattorit
│   ├── file_utils.py           # Tiedostotyökalut
│   ├── election_validator.py   # Vaalien validointi
│   ├── data_manager.py         # Datan hallinta
│   ├── config_manager.py       # Konfiguraatio
│   └── error_handling.py       # Virheiden käsittely
├── managers/                # Hallintamoduulit
│   ├── ipfs_sync_manager.py    # IPFS-synkronointi
│   ├── candidate_key_manager.py # Avainten hallinta
│   ├── secure_answer_manager.py # Turvalliset vastaukset
│   ├── question_manager.py     # Kysymysten hallinta
│   ├── elo_manager.py          # ELO-luokitus
│   ├── crypto_manager.py       # Kryptografia
│   ├── analytics_manager.py    # Analytics
│   ├── divine_manager.py       # Jumaltenvaalit-spesifinen
│   ├── ipfs_manager.py         # IPFS-hallinta
│   ├── media_registry.py       # Media-rekisteri
│   ├── enhanced_party_manager.py # Puolueiden hallinta
│   └── quorum_manager.py       # Kvoorum-äänestys
├── nodes/                   # Hajautetut solmut
│   ├── node_manager.py         # Solmujen hallinta
│   ├── network_sync.py         # Verkon synkronointi
│   ├── quorum_voting.py        # Hajautettu äänestys
│   └── worker/
│       └── election_installer.py # Vaalien asennus
├── templates/               # Templatet ja HTML
│   ├── html_generator.py       # HTML-generaattori
│   ├── css_generator.py        # CSS-generaattori
│   ├── party_templates.py      # Puoluetemplatet
│   ├── candidate_templates.py  # Ehdokastemplatet
│   ├── html_templates.py       # HTML-mallit
│   ├── ipfs_publisher.py       # IPFS-julkaisu
│   ├── template_utils.py       # Aputyökalut
│   ├── base_templates.py       # Perustemplatet
│   ├── profile_manager.py      # Profiilien hallinta
│   └── json_templates/         # JSON-template-tiedostot
└── models/                  # Data-mallit
```

## 📁 Data-rakenne

```
data/
├── runtime/
│   ├── meta.json              # Järjestelmän metadata
│   ├── system_chain.json      # Muutoshistoria
│   ├── questions.json         # Kysymykset + ELO-luokitukset
│   ├── candidates.json        # Ehdokkaat
│   ├── parties.json           # Puolueet
│   ├── candidate_answers.json # Ehdokkaiden vastaukset
│   └── ipfs_sync.json         # IPFS-synkronointitila
├── nodes/
│   ├── Jumaltenvaalit2026_nodes.json
│   ├── Jumaltenvaalit2026_network_sync.json
│   └── Jumaltenvaalit2026_votes.json
├── credentials/
│   ├── candidate_certs/       # Ehdokkaiden sertifikaatit
│   └── party_certs/           # Puolueiden sertifikaatit
└── backup/
```

## 🚀 Pika-aloitus

### 1. Asennus

```bash
# Kloonaa repositorio
git clone https://github.com/your-username/decentralized-candidate-matcher.git
cd decentralized-candidate-matcher

# Asenna riippuvuudet
pip install -r requirements.txt

# Alusta järjestelmä
python src/cli/install.py --first-install --election-id Jumaltenvaalit2026
```

### 2. Peruskäyttö

```bash
# Lisää kysymyksiä
python src/cli/manage_questions.py --add \
  --category "Ympäristö" \
  --question "Pitäisikö hiilidioksidipäästöjä vähentää?" \
  --fi "Pitäisikö hiilidioksidipäästöjä vähentää?" \
  --en "Should carbon dioxide emissions be reduced?" \
  --sv "Bör koldioxidutsläppen minskas?"

# Lisää puolueita
python src/cli/manage_parties.py --add \
  --name "Vihreä liitto" \
  --fi "Vihreä liitto" \
  --en "Green Alliance" \
  --sv "Gröna förbundet"

# Lisää ehdokkaita
python src/cli/manage_candidates.py --add \
  --name "Matti Meikäläinen" \
  --party "Vihreä liitto"

# Luo HTML-profiilit IPFS:ään
python src/cli/generate_profiles.py publish-all-to-ipfs --election Jumaltenvaalit2026
```

## 🎯 Käyttötapaukset

### Vaalien järjestäjille
```bash
# Alusta uudet vaalit
python src/cli/install.py --first-install --election-id Kuntavaalit2025

# Hallinnoi kysymyksiä
python src/cli/manage_questions.py --list
python src/cli/compare_questions.py --auto 10

# Tarkista data-eheys
python src/cli/validate_data.py --election-id Kuntavaalit2025
```

### Puolueille
```bash
# Rekisteröi puolue
python src/cli/manage_parties.py --add --name "Oma Puolue"

# Lisää ehdokkaita
python src/cli/manage_candidates.py --add --name "Ehdokas Nimi" --party "Oma Puolue"

# Hallinnoi vastauksia
python src/cli/manage_answers.py --candidate "Ehdokas Nimi" --add
```

### Ehdokkaille
```bash
# Luo henkilökohtaiset tunnistetiedot
python src/cli/candidate_credentials.py --generate

# Anna vastaukset kysymyksiin
python src/cli/manage_answers.py --add --candidate "Oma Nimi"
```

### Käyttäjille
```bash
# Vertaile kysymyksiä parantaaksesi laatua
python src/cli/compare_questions.py

# Selaa IPFS-profiileja
python src/cli/generate_profiles.py status --election Jumaltenvaalit2026

# Katso tilastoja
python src/cli/analytics.py --election Jumaltenvaalit2026
```

## 🔧 Tekniset Ominaisuudet

### ELO-luokitusjärjestelmä
- Kaksitasoinen rating: `current_rating = 1000 + comparison_delta + vote_delta`
- Automaattinen moderaatio: Estää manipuloinnin vaatii yhteisökonsensuksen
- Laadun priorisointi: Korkealuokituksiset kysymykset nousevat esille

### PKI-turvajärjestelmä
- Ehdokkaiden digitaaliset allekirjoitukset
- Puolueiden hajautettu vahvistus (3/3 kvoorumi)
- Tietoturva-avaimet ja sertifikaatit

### IPFS-integrointi
- Täysi yhteensopivuus IPFS Kubo 0.38.2:n kanssa
- Hajautettu datajako ilman keskitettyä palvelinta
- Mock-IPFS testausympäristöä varten

### Monikielisyys
- Suomi, englanti, ruotsi
- Kaikki tekstit lokalisoitu
- Automaattiset käännöspohjat

## 🌐 IPFS-profiilit

Järjestelmä generoi automaattisesti HTML-profiilit kaikille puolueille ja ehdokkaille ja julkaisee ne IPFS-verkkoon:

```bash
# Julkaise kaikki profiilit
python src/cli/generate_profiles.py publish-all-to-ipfs --election Jumaltenvaalit2026

# Tarkista tila
python src/cli/generate_profiles.py status --election Jumaltenvaalit2026
```

**Esimerkki IPFS-linkkejä:**
- Testipuolue: `QmVAPCMdMbYdsDvPeXUJZ9MZ1UpsdNNhgDvZSs7dsPkAYf`
- Zeus: `QmYR3WTKdcphxBuk6zB5mCsK2X9bZv6TcUSoLkhpZrNQvX`
- Athena: `QmXXbqpiJyVRvZLXYNg1Hqns2Mnd8f9iJWhF8gyKsmKgKd`

## 📊 Analytics ja Raportointi

```bash
# Yleiset tilastot
python src/cli/analytics.py --election Jumaltenvaalit2026

# Puoluekohtaiset tilastot
python src/cli/party_stats.py --election Jumaltenvaalit2026

# ELO-tilastot
python src/cli/elo_admin.py --stats

# Vastausten raportit
python src/cli/answer_reports.py --election Jumaltenvaalit2026
```

## 🔐 Tietoturva

- Kaikki ehdokkaiden vastaukset digitaalisesti allekirjoitettuja
- Puolueiden rekisteröinti vaatii hajautetun vahvistuksen
- Data-eheys tarkistetaan system_chain.json:n avulla
- IPFS-data varmennettu hash-pohjaisella eheystarkistuksella

## 🧪 Testaus

```bash
# Suorita kaikki testit
python tests/run_tests.py

# Integraatiotestit
python tests/run_integration_tests.py

# Yksikkötestit
pytest tests/unit/

# IPFS-testaus
python test_ipfs.py
```

## 🔮 Tulevat Ominaisuudet

- [ ] `voting_engine.py` - Varsinainen vaalikoneen ydin
- [ ] Web-käyttöliittymä Reactilla
- [ ] Reaaliaikainen tulospalvelu
- [ ] Mobiili-sovellus
- [ ] Laajempi skaalautuvuustesti
- [ ] Blockchain-integrointi

## 🤝 Osallistu Kehitykseen

1. Forkkaa repositorio
2. Luo feature-haara (`git checkout -b feature/ominaisuus`)
3. Commitoi muutokset (`git commit -am 'Lisää uusi ominaisuus'`)
4. Pushaa haaraan (`git push origin feature/ominaisuus`)
5. Luo Pull Request

## 📜 Lisenssi

Tämä projekti on lisensoitu Apache 2.0 -lisenssillä - katso [LICENSE](LICENSE) tiedosto lisätietoja varten.

## 🆘 Tuki

- [Issues](https://github.com/your-username/decentralized-candidate-matcher/issues)
- [Discussions](https://github.com/your-username/decentralized-candidate-matcher/discussions)
- [Wiki](https://github.com/your-username/decentralized-candidate-matcher/wiki)

---

<div align="center">
  
**🏛️ Demokratia koodiksi - Yhteisö luo, äänestää ja moderoi kysymyksiä hajautetusti** 🚀

</div>
