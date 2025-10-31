# TODO - Vaalijärjestelmän Kehitys

## 🚀 SEURAAVAT VAIHEET

### 🔧 Tärkeät Korjaukset
- [x] **Integroi `create_install_config.py` → `elections_list_manager.py`**
  - Uudet vaalit tallennetaan automaattisesti elections_list.json:iin
  - Install_config CID generoidaan automaattisesti
- [x] **Tarkista että Jumaltenvaalit_2026 on elections_list.json:ssa**
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
- Elections_list.json integraatio (päivitetty automaattiseksi)
- Install_config CID -järjestelmä (nyt generoidaan automaattisesti)

### 🔄 Käynnissä Olevat
- Active_questions lukitustilan testaus
- IPFS-siirtymä mockista oikeaan

## 🐛 Tunnetut Ongelmat
1. `create_install_config.py` integraatio vaatii vielä integraatiotestit
2. Jumaltenvaalit_2026 CID:n validointi puutteellinen
3. IPFS on vielä mock-toteutus (siirtymä käynnissä)

## 💡 Ideat Tulevaisuutta Varten
- Graafiset tilastot ja visualisoinnit
- Reaaliaikainen äänestystilanne
- Sosiaalinen jakaminen
- Monikielisyys (lisää kieliä)
- Fingerprint-lukituksen automaattinen päivitys kehitystilasta käyttötilaan

---
*Päivitetty: October 31, 2025*

**Huomisen suunnitelma: Jatka active_questions lukitustilan testauksella ja siirry IPFS-integrointiin!**
