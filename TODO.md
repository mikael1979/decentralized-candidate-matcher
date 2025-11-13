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

### 🔧 Data Validointi
- [x] `validate_data.py` - Data-eheyden tarkistus
- [x] JSON-skeemat ja validointi
- [x] Eheystarkistukset

---

## 🚧 TEKIJÄLLÄ (🔨 KEHItyksessä)

### 🖥️ Moninode-järjestelmä
- [ ] `node_management.py` - Solmujen hallinta
- [ ] `network_sync.py` - Verkon synkronointi
- [ ] `quorum_voting.py` - Hajautettu äänestys
- [ ] Täysin hajautettu arkkitehtuuri

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

### 📱 Käyttäjäkokemus
- [ ] React/Vue frontend
- [ ] Mobiiliystävällisyys
- [ ] Reaaliaikainen tulospalvelu

---

## 🎯 PRIORITEETIT

### 🥇 PRIORITEETTI 1 (Seuraavaksi)
1. **Moninode-järjestelmän viimeistely** - Hajautettu arkkitehtuuri
2. **`voting_engine.py`** - Vaalikoneen ydin

### 🥈 PRIORITEETTI 2 
3. **Web-käyttöliittymä** - Graafinen käyttöliittymä
4. **Tulosten visualisointi** - Käyttäjäystävälliset raportit

### 🥉 PRIORITEETTI 3
5. **Laajamittainen testaus** - Skaalautuvuustestit
6. **Dokumentaatio** - Käyttöohjeet ja API-dokumentaatio

---

## 🏗️ TEKNISET TIEDOT

### Tiedostorakenne

src/
├── cli/
│ ├── ✅ install.py # Järjestelmän asennus
│ ├── ✅ manage_questions.py # Kysymysten hallinta
│ ├── ✅ manage_candidates.py # Ehdokkaiden hallinta
│ ├── ✅ manage_parties.py # Puolueiden hallinta
│ ├── ✅ compare_questions.py # ELO-vertailu
│ ├── ✅ elo_admin.py # ELO-hallinta
│ ├── ✅ link_candidate_to_party.py
│ ├── ✅ manage_answers.py # Ehdokkaiden vastaukset
│ ├── ✅ ipfs_sync.py # IPFS-synkronointi
│ ├── ✅ analytics.py # Analytics
│ ├── ✅ generate_profiles.py # HTML-profiilit
│ ├── 🔨 node_management.py # Moninode-hallinta
│ └── ⏳ voting_engine.py # Vaalikoneen ydin
├── core/
│ ├── ✅ ipfs_client.py # IPFS-integrointi
│ └── ✅ pki_manager.py # PKI-turvajärjestelmä
├── nodes/
│ ├── 🔨 network_sync.py # Verkon synkronointi
│ ├── 🔨 node_manager.py # Solmujen hallinta
│ └── 🔨 quorum_voting.py # Hajautettu äänestys
└── templates/
├── ✅ html_generator.py # HTML-generaattori
└── ✅ base_template.css # CSS-tyylit


### Data-tiedostot

data/
├── runtime/
│ ├── ✅ meta.json # Järjestelmän metadata
│ ├── ✅ system_chain.json # Muutoshistoria
│ ├── ✅ questions.json # Kysymykset + ELO-luokitukset
│ ├── ✅ candidates.json # Ehdokkaat
│ ├── ✅ parties.json # Puolueet
│ ├── ✅ candidate_answers.json # Ehdokkaiden vastaukset
│ └── ✅ ipfs_sync.json # IPFS-synkronointitila
├── nodes/
│ ├── 🔨 Jumaltenvaalit2026_nodes.json
│ ├── 🔨 Jumaltenvaalit2026_network_sync.json
│ └── 🔨 Jumaltenvaalit2026_votes.json
└── credentials/
├── ✅ candidate_certs/ # Ehdokkaiden sertifikaatit
└── ✅ party_certs/ # Puolueiden sertifikaatit


---

## 🎉 VIIMEISIMMÄT SAAVUTUKSET (TÄMÄN PÄIVÄN)

### 🌟 TÄRKEIMMÄT SAAVUTUKSET
- **✅ HTML Profiilien Generointi** - Kaikki puolueet ja ehdokkaat saatavilla IPFS:stä
- **✅ IPFS-Integrointi Korjattu** - Täysi yhteensopivuus IPFS Kubo 0.38.2:n kanssa
- **✅ Oikeat IPFS-CID:t** - Kaikki profiilit julkaistu oikeaan IPFS-verkkoon
- **✅ Release v1.0.0** - Ensimmäinen tuotantovalmissa versio

### 🔧 Tekniset Parannukset
- **Korvattu `ipfshttpclient`** suoralla HTTP API:lla
- **UTF-8 tuki** suomen kielelle IPFS:ässä
- **Väriteemat** puolueille
- **Base.json metadata-järjestelmä**

### 📊 Tuotantovalmiudet
- **12 profiilia** saatavilla IPFS-verkossa
- **5 puoluetta** ja **12 ehdokasta** julkaistu
- **Kaikki testit menevät läpi**
- **Koodi päähaarassa** ja tagattu v1.0.0

---

## 🚀 TUOTANTOVALMIS JÄRJESTELMÄ

### 📦 Mitä on Valmiina
```bash
# 1. Generoi kaikki profiilit IPFS:ään
python src/cli/generate_profiles.py publish-all-to-ipfs --election Jumaltenvaalit2026

# 2. Tarkista profiilien tila
python src/cli/generate_profiles.py status --election Jumaltenvaalit2026

# 3. HTML-profiilit saatavilla
#    https://ipfs.io/ipfs/QmVAPCMdMbYdsD... (Testipuolue)
#    https://ipfs.io/ipfs/QmYR3WTKdcphx... (Zeus)

🌐 IPFS-Linkit
Testipuolue: QmVAPCMdMbYdsDvPeXUJZ9MZ1UpsdNNhgDvZSs7dsPkAYf

Zeus: QmYR3WTKdcphxBuk6zB5mCsK2X9bZv6TcUSoLkhpZrNQvX

Athena: QmXXbqpiJyVRvZLXYNg1Hqns2Mnd8f9iJWhF8gyKsmKgKd

💡 SEURAAVAT ASKELEET
🔨 Välitavoitteet
Viimeistele moninode-järjestelmä - Hajautettu arkkitehtuuri

Toteuta voting_engine.py - Vaalikoneen ydinlogiikka

🎯 Pitkän tähtäimen tavoitteet
Web-käyttöliittymä - Moderni React-sovellus

Skaalautuvuus - Suurten vaalien tuki

13.11.2025
