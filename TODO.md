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
- [x] **Template-modulaarisuus** - Refaktoroitu html_templates.py erikoistuneisiin moduuleihin

### 🔧 Data Validointi
- [x] `validate_data.py` - Data-eheyden tarkistus
- [x] JSON-skeemat ja validointi
- [x] Eheystarkistukset

---

## 🚧 TEKIJÄLLÄ (🔨 KEHItyksessä)

### 🌐 IPNS & Dynaamiset Osoitteet
- [ ] **IPNSManager-luokan luonti** - `src/managers/ipns_manager.py`
- [ ] **Profiilipohjien päivitys IPNS-linkeillä** - Dynaamiset osoitteet staattisten sijaan
- [ ] **Automaattinen IPNS-päivitys** - Triggeri uusien profiilien generoinnin yhteydessä

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

### 🔄 Päivitettävyys & Versionhallinta
- [ ] **Profiiliversiointi** - Jokaiselle profiilille versionumero
- [ ] **Data-skeeman hallinta** - Yhteensopivuus vanhempien versioiden kanssa

---

## 🎯 PRIORITEETIT

### 🥇 PRIORITEETTI 1 (Seuraavaksi)
1. **IPNS & Dynaamiset osoitteet** - Päivitettävyys koko järjestelmään
2. **Moninode-järjestelmän viimeistely** - Hajautettu arkkitehtuuri

### 🥈 PRIORITEETTI 2 
3. **`voting_engine.py`** - Vaalikoneen ydin
4. **Web-käyttöliittymä** - Graafinen käyttöliittymä

### 🥉 PRIORITEETTI 3
5. **Tulosten visualisointi** - Käyttäjäystävälliset raportit
6. **Laajamittainen testaus** - Skaalautuvuustestit

---

## 🌟 VIIMEISIMMÄT SAAVUTUKSET

### 📅 Tämän Päivän Saavutukset
- **✅ HTML Template Refaktorointi** - `html_templates.py` jaettu modulaarisiin osiin:
  - `candidate_templates.py` (208 riviä) - Ehdokasprofiilit
  - `party_templates.py` (261 riviä) - Puolueprofiilit  
  - `html_templates.py` (59 riviä) - Päämoduuli (87% pienempi)
  - `template_utils.py` (38 riviä) - Aputyökalut
- **✅ Kaikki 48 testiä menevät läpi** refaktoroinnin jälkeen
- **✅ Git Flow -malli** käyttöön: develop-haara luotu
- **✅ IPFS-profiilijulkaisu** toimii täydellisesti

### 🏗️ Arkkitehtuuriparannukset
- **Parempi koodinlaatu** - Yksittäiset tiedostot < 300 riviä
- **Selkeämmät vastuualueet** - Jokaisella template-tyypillä oma moduuli
- **Helppo laajennettavuus** - Uusia template-tyyppejä voi helposti lisätä
- **Täysi yhteensopivuus** - Kaikki olemassa olevat toiminnot säilyvät

---

## 🚀 ALOITA IPNS-TOTEUTUS

```bash
# 1. Vaihda develop-haaraan
git checkout develop

# 2. Luo uusi feature-haara IPNS:lle
git checkout -b feature/ipns-dynamic-links

# 3. Aloita toteutus
# - Luo src/managers/ipns_manager.py
# - Päivitä templatejä käyttämään IPNS-osoitteita
# - Testaa mock-ympäristössä
📊 TEKNINEN TILANNE
Tiedostorakenne (Päivitetty)
text
src/templates/
├── ✅ candidate_templates.py (208 riviä) - Ehdokasprofiilit
├── ✅ party_templates.py (261 riviä) - Puolueprofiilit  
├── ✅ html_templates.py (59 riviä) - Päämoduuli
├── ✅ template_utils.py (38 riviä) - Aputyökalut
├── ✅ css_generator.py (354 riviä) - CSS-generointi
├── ✅ html_generator.py (156 riviä) - HTML-generaattori
└── ✅ profile_manager.py (168 riviä) - Profiilien hallinta
Testitilanne
48 testiä - Kaikki menevät läpi

100% läpäisy refaktoroinnin jälkeen

Modulaarisuus testattu - Kaikki template-moduulit toimivat

Päivitetty: la 15.11.2025
