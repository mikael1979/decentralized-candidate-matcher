# 🏛️ Hajautetun Vaalikoneen Kehitys - Päivitetty TODO Lista

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
- [x] `manage_candidates.py` - Ehdokkaiden lisäys ja hallinta
- [x] `candidates.json` - Ehdokkaiden perustiedot
- [x] UUID-pohjainen ID-generointi
- [x] Duplikaattien esto

### 🏛️ Puolueiden Hallinta
- [x] `manage_parties.py` - Puolueiden hajautettu hallinta
- [x] `parties.json` - Puolueiden data-rakenne
- [x] Hajautettu vahvistus (3/3 kvoorumi)
- [x] `link_candidate_to_party.py` - Ehdokkaiden linkitys

### 📝 Ehdokkaiden Vastausten Hallinta
- [x] `manage_answers.py` - Ehdokkaiden vastausten hallinta
- [x] Vastausten validointi (-5 - +5 asteikolla)
- [x] Perustelut monikielisinä
- [x] Luottamustasot (1-5)

### 🔐 PKI Turvajärjestelmä
- [x] `candidate_credentials.py` - Ehdokkaiden identiteetin varmennus
- [x] `enhanced_party_verification.py` - Puolueiden vahvistus
- [x] Hajautettu allekirjoitusjärjestelmä
- [x] Tietoturva-avaimet ja sertifikaatit

### 🌐 IPFS Hajautettu Tallenus
- [x] `ipfs_client.py` - IPFS-integrointi (Kubo 0.38.2 yhteensopiva)
- [x] `ipfs_sync.py` - Hajautettu datajako
- [x] Mock-IPFS testausta varten
- [x] Synkronointiprotokolla
- [x] **UUSI:** Modulaarinen IPFS-arkkitehtuuri
  - [x] `archive_manager.py` - Arkistointi
  - [x] `delta_manager.py` - Muutosten seuranta
  - [x] `sync_orchestrator.py` - Synkronoinnin koordinointi

### 📊 Analytics ja Raportointi
- [x] `analytics.py` - Vaalitilastot ja analyysit
- [x] `party_stats.py` - Puoluetilastot
- [x] Tulosten analysointi
- [x] Raporttien generointi

### 🎨 HTML Profiilien Generointi
- [x] `generate_profiles.py` - Profiilisivujen CLI
- [x] `html_generator.py` - HTML-template-järjestelmä
- [x] Väriteemat puolueille
- [x] IPFS-julkaisu profiileista
- [x] Base.json metadata-järjestelmä

### 🔧 Data Validointi & Eheys
- [x] `validate_data.py` - Data-eheyden tarkistus
- [x] `cleanup_data.py` - Duplikaattien poisto ja siivous
- [x] `data_validator.py` - Validointimoduuli
- [x] JSON-skeemat ja validointi
- [x] Eheystarkistukset
- [x] Varmuuskopiointijärjestelmä

### 🗳️ Vaalikoneen Ydin
- [x] `voting_engine.py` - Varsinainen vaalikone
- [x] Käyttäjän vastausten keräys
- [x] Yhteensopivuuslaskenta
- [x] Tulosten järjestely

---

## 🚧 KEHITYKSESSÄ (🔨 TYÖN ALLA)

### ⚙️ Config-järjestelmä (UUSI)
- [ ] `config.json` - Keskitetty konfiguraatio
- [ ] `config_manager.py` - Config-hallinta
- [ ] `install.py --first-install` - Konfiguraation alustus
- [ ] IPFS-tallennus configille
- [ ] Hash-fingerprint system_chain:iin

### 🖥️ Moninode-järjestelmä
- [ ] `node_management.py` - Solmujen hallinta
- [ ] `network_sync.py` - Verkon synkronointi
- [ ] `quorum_voting.py` - Hajautettu äänestys
- [ ] Täysin hajautettu arkkitehtuuri

---

## 📋 SEURAAVAT VAIHEET (⏳ ODOTTAA)

### 🖥️ Käyttöliittymät
- [ ] Web-käyttöliittymä (Flask/FastAPI)
- [ ] CLI-käyttöliittymä (rich/click)
- [ ] Tulosten visualisointi

### 📱 Käyttäjäkokemus
- [ ] React/Vue frontend
- [ ] Mobiiliystävällisyys
- [ ] Reaaliaikainen tulospalvelu

---

## 🎯 PRIORITEETIT

### 🥇 PRIORITEETTI 1 (Seuraavaksi)
1. **Config-järjestelmä** - Keskitetty konfiguraatio
2. **Moninode-järjestelmän viimeistely** - Hajautettu arkkitehtuuri

### 🥈 PRIORITEETTI 2 
3. **Web-käyttöliittymä** - Graafinen käyttöliittymä
4. **Tulosten visualisointi** - Käyttäjäystävälliset raportit

### 🥉 PRIORITEETTI 3
5. **Laajamittainen testaus** - Skaalautuvuustestit
6. **Dokumentaatio** - Käyttöohjeet ja API-dokumentaatio

---

## 🏗️ PÄIVITETTY TEKNINEN RAKENNE

### Tiedostorakenne
```
src/
├── cli/
│   ├── ✅ install.py              # Järjestelmän asennus
│   ├── ✅ manage_questions.py     # Kysymysten hallinta
│   ├── ✅ manage_candidates.py    # Ehdokkaiden hallinta (UUID-ID:t)
│   ├── ✅ manage_parties.py       # Puolueiden hallinta
│   ├── ✅ compare_questions.py    # ELO-vertailu
│   ├── ✅ elo_admin.py           # ELO-hallinta
│   ├── ✅ link_candidate_to_party.py
│   ├── ✅ manage_answers.py      # Ehdokkaiden vastaukset
│   ├── ✅ ipfs_sync.py           # IPFS-synkronointi
│   ├── ✅ analytics.py           # Analytics
│   ├── ✅ generate_profiles.py   # HTML-profiilit
│   ├── ✅ cleanup_data.py        # Data-siivoustyökalu
│   ├── ✅ voting_engine.py       # Vaalikoneen ydin
│   ├── 🔨 node_management.py     # Moninode-hallinta
│   └── 🔨 config_manager.py      # Config-hallinta (UUSI)
├── core/
│   ├── ✅ ipfs_client.py         # IPFS-integrointi
│   ├── ✅ pki_manager.py         # PKI-turvajärjestelmä
│   ├── ✅ file_utils.py          # Tiedostotyökalut
│   ├── ✅ data_validator.py      # Data-validointi
│   ├── 🔨 config_manager.py      # Konfiguraatio (UUSI)
│   └── ipfs/
│       ├── ✅ archive_manager.py  # Arkistointi
│       ├── ✅ delta_manager.py    # Muutosten seuranta
│       └── ✅ sync_orchestrator.py # Synkronointi
├── nodes/
│   ├── 🔨 network_sync.py        # Verkon synkronointi
│   ├── 🔨 node_manager.py        # Solmujen hallinta
│   └── 🔨 quorum_voting.py       # Hajautettu äänestys
└── templates/
    ├── ✅ html_generator.py      # HTML-generaattori
    └── ✅ base_template.css      # CSS-tyylit
```

### Data-tiedostot
```
data/
├── runtime/
│   ├── ✅ meta.json              # Järjestelmän metadata
│   ├── ✅ system_chain.json      # Muutoshistoria
│   ├── ✅ questions.json         # Kysymykset + ELO-luokitukset
│   ├── ✅ candidates.json        # Ehdokkaat (UUID-ID:t)
│   ├── ✅ parties.json           # Puolueet
│   ├── ✅ candidate_answers.json # Ehdokkaiden vastaukset
│   └── ✅ ipfs_sync.json         # IPFS-synkronointitila
├── backup/
│   ├── ✅ 20251118_065730/       # Varmuuskopiot
│   └── ✅ 20251118_070652/
├── nodes/
│   ├── 🔨 Jumaltenvaalit2026_nodes.json
│   ├── 🔨 Jumaltenvaalit2026_network_sync.json
│   └── 🔨 Jumaltenvaalit2026_votes.json
└── credentials/
    ├── ✅ candidate_certs/       # Ehdokkaiden sertifikaatit
    └── ✅ party_certs/           # Puolueiden sertifikaatit
```

---

## 🎉 VIIMEISIMMÄT SAAVUTUKSET (19.11.2025)

### 🌟 PÄIVITETYT SAAVUTUKSET
- **✅ Modulaarinen IPFS-arkkitehtuuri** - Archive, Delta, Sync moduulit
- **✅ Vaalikoneen ydin valmis** - `voting_engine.py` toimii
- **✅ Template-järjestelmän parannus** - Parempi base template -hallinta
- **✅ Package-rakenne** - `setup.py` ja egg-info

### 🔧 Tekniset Parannukset
- **Refaktoroitu IPFS-koodi** - Modulaarisempi ja ylläpidettävämpi
- **Paranneltu synkronointi** - `sync_orchestrator.py`
- **Testit uusille moduuleille** - `test_ipfs_modular.py`
- **Stabiili main-haara** - Kaikki toiminnot testattu

---

## 🚀 TUOTANTOVALMIS JÄRJESTELMÄ

### 📦 Mitä on Valmiina
```bash
# 1. Käynnistä vaalikone
python src/cli/voting_engine.py --election Jumaltenvaalit2026 --start

# 2. Analytics-raportit
python src/cli/analytics.py wrapper --election Jumaltenvaalit2026

# 3. Hallitse dataa
python src/cli/manage_answers.py list --election Jumaltenvaalit2026
python src/cli/manage_candidates.py --election Jumaltenvaalit2026 --list

# 4. IPFS-synkronointi
python src/cli/ipfs_sync.py --election Jumaltenvaalit2026 --publish
```

---

## 💡 SEURAAVAT ASKELEET

### 🔨 Välitavoitteet (Seuraavaksi)
1. **Config-järjestelmä** - Keskitetty konfiguraatio (feature/config-system branch)
2. **Moninode-järjestelmä** - Hajautettu arkkitehtuuri

### 🎯 Pitkän tähtäimen tavoitteet
3. **Web-käyttöliittymä** - Moderni React-sovellus
4. **Skaalautuvuus** - Suurten vaalien tuki

---

## 🌟 UUSI CONFIG-JÄRJESTELMÄ (feature/config-system)

### 🎯 Tavoitteet
- **Yksinkertaisemmat komennot** (ei tarvi --election joka kerta)
- **IPFS-pohjainen deployment** - helpompi worker-node setup
- **Hash-fingerprint** - configin eheyden varmistus
- **Template-pohjainen** - base_config.json + generointi

### 📋 To Do Config-järjestelmälle
- [ ] `config.json` template
- [ ] `src/core/config_manager.py`
- [ ] `install.py --first-install` päivitys
- [ ] CLI-komentojen päivitys (optionaaliset --election)
- [ ] IPFS-tallennus & hash-validointi
- [ ] System_chain integrointi

---
*Päivitetty: 19.11.2025 - feature/config-system branch*

