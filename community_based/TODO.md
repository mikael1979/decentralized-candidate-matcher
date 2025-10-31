# TODO - Vaalijärjestelmän Kehitys

## 🚀 SEURAAVAT VAIHEET

### 🔧 Tärkeät Korjaukset
- [ ] **Integroi `create_install_config.py` → `elections_list_manager.py`**
  - Uudet vaalit tallennetaan automaattisesti elections_list.json:iin
  - Install_config CID generoidaan automaattisesti
- [ ] **Tarkista että Jumaltenvaalit_2026 on elections_list.json:ssa**
  - Lisää install_config_cid jos puuttuu
- [ ] **Testaa active_questions lukittu/avoin tila**
  - Varmista että vaalikone toimii molemmissa tiloissa

### 🌐 Käyttöliittymän Kehitys
- [ ] **Web-käyttöliittymä (Flask)**
  - Kysymysten vastaaminen selaimessa
  - Tulosten näyttäminen
  - Responsiivinen design
- [ ] **API-reitit**
  - REST API vaalikoneelle
  - JSON-pohjainen data-vaihto

### 📊 Data & Synkronointi
- [ ] **IPFS-synkronointi**
  - Oikea IPFS-integrointi (ei mock)
  - Data-synkronointi monella koneella
- [ ] **Vaalikonfiguraatioiden hallinta**
  - Useampia samanaikaisia vaaleja
  - Vaalien tilan hallinta (upcoming → active → completed)

### 🧪 Testaus & Dokumentaatio
- [ ] **Kattava testaus**
  - Yksikkötestit kaikille moduuleille
  - Integraatiotestit
  - Käyttöliittymätestit
- [ ] **Käyttöohjeet**
  - Asennusohjeet
  - Vaalien luontiohjeet
  - Ylläpitöohjeet

### 🎯 Pitkän Aikavälin Tavoitteet
- [ ] **Mobile-sovellus**
- [ ] **AI-pohjainen kysymysten generointi**
- [ ] **Blockchain-integrointi**
- [ ] **Kansainvälinen skaalaus**

## 📝 NYKYINEN TILA

### ✅ Valmiit Ominaisuudet
- ELO-pohjainen kysymysten luokitus
- System_chain muutoshistoria
- Active questions hallinta
- Komentorivivaalikone
- Hajautettu arkkitehtuuri
- Kreikkalaisten jumalien testidata

### 🔄 Käynnissä Olevat
- Elections_list.json integraatio
- Install_config CID -järjestelmä

## 🐛 Tunnetut Ongelmat
1. `create_install_config.py` ei päivitä elections_list.json:ia automaattisesti
2. Jumaltenvaalit_2026 puuttuu elections_list.json:ista
3. IPFS on vielä mock-toteutus

## 💡 Ideat Tulevaisuutta Varten
- Graafiset tilastot ja visualisoinnit
- Reaaliaikainen äänestystilanne
- Sosiaalinen jakaminen
- Monikielisyys (lisää kieliä)

---
*Päivitetty: $(date)*

**Huomisen suunnitelma: Aloita elections_list.json integraation korjauksesta!**
