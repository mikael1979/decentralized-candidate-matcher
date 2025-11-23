# Hajautettu Vaalikone - Decentralized Candidate Matcher

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![IPFS Compatible](https://img.shields.io/badge/IPFS-Kubo%200.38.2-green.svg)](https://docs.ipfs.tech/)
[![Multinode Ready](https://img.shields.io/badge/Multinode-Enabled-success.svg)]()
[![Status: Production Ready](https://img.shields.io/badge/Status-TUOTANTOVALMIS-success.svg)]()

Hajautettu, yhteisöohjattu vaalikonejärjestelmä...

Hajautettu, yhteisöohjattu vaalikonejärjestelmä, joka käyttää ELO-luokitusjärjestelmää kysymysten priorisointiin ja automoderaatioon. Järjestelmä on suunniteltu tukemaan useita samanaikaisia vaaleja hajautetusti ilman keskitettyä hallintapalvelinta.

## 📋 Sisällysluettelo

- [Pääominaisuudet](#-pääominaisuudet)
- [Vaatimukset](#-vaatimukset)
- [Pika-aloitus](#🚀-pika-aloitus)
- [Multinode-tuki](#🌐-multinode-tuki-uusi)
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
- **Multinode-tuki** – Hajautettu multimode-järjestelmä konsensusmekanismilla
- **Config-järjestelmä** – Template-pohjainen konfiguraatio  
- **ELO-luokitusjärjestelmä** – Kysymysten laadun automaattinen arviointi  
- **PKI-turvajärjestelmä** – Ehdokkaiden ja puolueiden varmennus  
- **IPFS-integrointi** – Hajautettu datajako ja tallennus  
- **Reaaliaikainen analytics** – Vaalitilastot ja analyysit  
- **HTML-profiilit** – Automaattiset profiilisivut IPFS:ään  
- **Remove/Update toiminnot** – Täydellinen data-hallinta  

## 🛠️ Vaatimukset

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
2. Peruskäyttö
bash
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
🌐 Multinode-tuki (UUSI!)
Järjestelmä tukee nyt hajautettua multimode-arkkitehtuuria:

Multinode-ominaisuudet
Ehdokkaiden hallinta verkossa - Ehdokasmuutokset synkronoidaan konsensusmekanismilla

Voting-sessioiden jakaminen - Äänestyssession tiedot jaetaan verkon nodejen kesken

Node-identiteetit - Jokaisella nodella on uniikki identiteetti ja rooli

Konsensusprotokolla - Muutokset hyväksytään verkoston enemmistöllä

Multinode-käyttö
bash
# Ehdokkaiden hallinta verkossa
python src/cli/manage_candidates.py --list --enable-multinode

# Voting-sessio verkossa
python src/cli/voting_engine.py --start --enable-multinode

# Verkontilastot
python src/cli/voting_engine.py --network-stats --enable-multinode

# Debug-tila bootstrap-peereille
python src/cli/manage_candidates.py --enable-multinode --bootstrap-debug
Multinode-arkkitehtuuri
text
┌─────────────────┐    ┌─────────────────┐
│   Coordinator   │◄──►│    Worker       │
│     Node        │    │     Node        │
└─────────────────┘    └─────────────────┘
         ▲                       ▲
         └───── Consensus ───────┘
📖 Käyttöopas
Vaalien Järjestäjille
bash
# Alusta vaali
python src/cli/install.py --first-install --election-id "Olympos2024"

# Listaa kysymykset
python src/cli/manage_questions.py --list

# Vertaile kysymyksiä ELO-perusteella
python src/cli/compare_questions.py --auto 10

# Tarkista järjestelmän tila
python src/cli/analytics.py wrapper
Multinode-hallinta
bash
# Ehdokkaiden hallinta verkossa
python src/cli/manage_candidates.py --add --name-fi "Verkkoehdokas" --enable-multinode

# Tarkista verkontilastot
python src/cli/voting_engine.py --network-stats --enable-multinode

# Listaa voting-sessiot verkosta
python src/cli/voting_engine.py --list-sessions --enable-multinode
Puolueille & Ehdokkaille
bash
# Rekisteröi ehdokas
python src/cli/manage_candidates.py --add --name-fi "Athena" --party "Olympos"

# Lisää vastauksia
python src/cli/manage_answers.py add --candidate-id athena_002 --question-id q_sota_01 --answer 5 --confidence 5

# Päivitä profiili
python src/cli/manage_candidates.py --update athena_002 --name-fi "Athena Parhenos"
Äänestäjille
bash
# Osallistu äänestykseen
python src/cli/voting_engine.py --start

# Katso tulokset
python src/cli/voting_engine.py --results session_olympos_20241201_120000

# Selaa analytiikkaa
python src/cli/analytics.py wrapper
Data-hallinta
bash
# Päivitä kysymys
python src/cli/manage_questions.py --update q_hallinto_01 --question-fi "Pitäisikö ukkoseniskuoikeuksia rajoittaa?"

# Poista ehdokas
python src/cli/manage_candidates.py --remove ares_003

# Poista vastaus
python src/cli/manage_answers.py remove --candidate-id zeus_001 --question-id q_hallinto_01
⚙️ Config-järjestelmä
Järjestelmä käyttää template-pohjaista config-järjestelmää:

json
{
  "metadata": {
    "election_id": "Olympos2024",
    "network_id": "Olympos2024_network",
    "deployed_at": "2025-11-23T10:15:29.768942",
    "version": "1.0.0",
    "config_hash": "156ce22e284095eda83f6a4a7506c67dc0a327b44aecce97e945f8429bb000a7",
    "template_hash": "9bca700f3bc37e3addf0eec70d395b3dfdf94d001cff8821c46abc59949acdd6"
  },
  "network_config": {
    "enable_multinode": true,
    "node_type": "coordinator",
    "bootstrap_peers": []
  }
}
📊 Analytics & Raportointi
bash
python src/cli/analytics.py wrapper
Raportti sisältää:

✅ Järjestelmän tila (healthy / needs_attention)

📈 Data-tilastot (kysymykset, ehdokkaat, vastaukset)

🏆 Kysymysten ELO-jakauma

🌐 Verkontilastot (multinode-tilassa)

🔧 Konkreettiset suositukset puutteiden korjaamiseksi

📋 Terveysindikaattorit

🌐 IPFS-integrointi
bash
# Config julkaistaan automaattisesti asennuksessa
python src/cli/install.py --first-install --election-id "Olympos2024"

# Julkaise kaikki profiilit IPFS:ään
python src/cli/generate_profiles.py publish-all-to-ipfs

# Synkronoi data IPFS-verkkoon
python src/cli/ipfs_sync.py --status
🔒 Tietoturva
Data Validointi - Kaikki vastaukset validoitu (−5…+5, varmuus 1…5)

Eheysvarmistus - Data-eheys varmistettu system_chain.json:llä

Hash-fingerprint - Configin muutosten seuranta

CID-tarkistus - IPFS-pohjainen eheystarkistus

PKI-todennus - Ehdokkaiden ja puolueiden varmennus

Konsensusvarmistus - Multinode-muutokset vaativat verkoston hyväksynnän

🐛 Vianetsintä
Yleisimmät ongelmat
Config ei lataa:

bash
rm config/active_election.json
python src/cli/install.py --first-install --election-id "Asgard2024"
IPFS-yhteysongelma:

bash
# Käynnistä IPFS-daemon
ipfs daemon

# Tarkista yhteys
python src/cli/ipfs_sync.py --status
Data-eheysongelma:

bash
# Tarkista data-eheys
python src/cli/validate_data.py --full-check

# Korjaa system_chain
python src/cli/validate_data.py --repair
Multinode-ongelmat:

bash
# Tarkista node-identiteetit
ls -la data/nodes/{election_id}/

# Käytä debug-tilaa
python src/cli/manage_candidates.py --enable-multinode --bootstrap-debug

# Tarkista verkontilastot
python src/cli/voting_engine.py --network-stats --enable-multinode
📁 Projektin Rakenne
text
src/
├── cli/                    # Komentorivityökalut
│   ├── install.py              # Järjestelmän asennus + config
│   ├── voting_engine.py        # Vaalikoneen ydin (multinode-tuki)
│   ├── analytics.py            # Analytics & raportointi
│   ├── manage_questions.py     # Kysymysten hallinta (add/remove/update)
│   ├── manage_candidates.py    # Ehdokkaiden hallinta (multinode-tuki)
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
├── nodes/                   # UUSI: Multinode-järjestelmä
│   ├── core/
│   │   ├── node_identity.py     # Node identiteetit
│   │   └── network_manager.py   # Verkkohallinta
│   └── protocols/
│       └── consensus.py         # Konsensusmekanismi
└── templates/               # Templatet
    └── config.base.json        # Config template
🔮 Tulevat Ominaisuudet
Moderni React-web-käyttöliittymä - Graafinen käyttöliittymä

Reaaliaikainen tulospalvelu - Live-tulokset

Mobiilisovellus - Äänestys mobiililaitteilla

Blockchain-integrointi - Lisäeheystakuu (valinnainen)

Käännöstoiminnot - Laajempi kielituki (mukaan lukien muinaiskreikka)

API-rajapinta - Kolmannen osapuolen integraatiot

🤝 Kehitykseen Osallistuminen
Forkkaa repositorio

Luo feature-haara:

bash
git checkout -b feature/oma-ominaisuus
Tee muutokset ja testaa

Commitoi muutokset:

bash
git commit -am 'Lisää uusi ominaisuus: kuvaus'
Pushaa haara:

bash
git push origin feature/oma-ominaisuus
Avaa Pull Request

Testaus
bash
# Suorita perustestit
python tests/test_config_manager.py

# Testaa multinode-toiminnallisuus
python src/cli/manage_candidates.py --list --enable-multinode
python src/cli/voting_engine.py --network-stats --enable-multinode

# Täydellinen testirundi
python src/cli/install.py --first-install --election-id "Testivaalit2024" --node-type coordinator
python src/cli/manage_questions.py --add --question-fi "Testikysymys"
python src/cli/manage_candidates.py --add --name-fi "Testiehdokas"
python src/cli/analytics.py wrapper
python src/cli/voting_engine.py --start
📄 Lisenssi
Apache License 2.0 - Katso LICENSE tiedosto lisätietoja varten.



Demokratia koodiksi – Hajautettu vaalikone käyttövalmiina

"Yksinkertaisemmat komennot, tehokkaampi demokratia"


🌐 Multinode-tuki saatavilla!
```
