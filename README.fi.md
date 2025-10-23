# Hajautettu Vaalikone - Frontend Development Guide

## Yleiskatsaus

Tämä on hajautettu vaalikonejärjestelmä, joka käyttää IPFS-teknologiaa kysymysten jakamiseen ja synkronointiin. Järjestelmä sisältää älykästä kysymysvalintaa Elo-luokitusjärjestelmän avulla.

## Tekniset Ominaisuudet

### 🏗️ Arkkitehtuuri
- **Backend**: Python + Flask
- **Frontend**: HTML/CSS/JavaScript (voidaan integroida minkä tahansa frontend-frameworkin kanssa)
- **Data Storage**: JSON-tiedostot + IPFS hajautetulle tallennukselle
- **Authentication**: Salasana-pohjainen admin-järjestelmä

### 🔗 API-yhteydet
Kaikki frontend-toiminnot toteutetaan REST API:n kautta. Backend tarjoaa täydellisen API:n kaikkiin toimintoihin.

## Frontend-kehitys

### Vaatimukset
- Moderni selain (ES6+ tuki)
- HTTP-pyynnöt (fetch API tai axios)
- JSON-datan käsittely

### Asennus ja Käynnistys

1. **Kloonaa projekti**:
```bash
git clone <repository-url>
cd decentralized-candidate-matcher

# Fingerprint-ketjujärjestelmä (System Chain)

Tämä järjestelmä toteuttaa **blockchain-tyylisen historiakirjan** kaikille vaalikoneen JSON-tiedostoille. Se mahdollistaa:

- **Eheyden tarkistuksen** jokaisen tiedoston tilalle
- **Historian seurannan** kaikista muutoksista
- **Rekursiivisen allekirjoituksen** superadmin → puolueadmin → ehdokas
- **Vikasietoisen päivityksen** ilman rikkoutuneiden tilojen syntymistä

## 📁 Rakenne

Ketju tallennetaan tiedostoon:


Se sisältää:
- `blocks`: lista lohkoista (0 = genesis)
- `current_state`: viimeisin tiedostojen fingerprint-tila
- `metadata`: allekirjoitus ja järjestelmätiedot

### 🔗 Lohkorakenne

Jokainen lohko (`block`) sisältää:

| Kenttä | Kuvaus |
|--------|--------|
| `block_id` | Lohkon järjestysnumero (0 = ensimmäinen) |
| `timestamp` | Lohkon luontiaika ISO 8601 -muodossa |
| `description` | Ihmisluettava kuvaus muutoksesta |
| `files` | Kaikkien seurattujen tiedostojen **SHA256-fingerprintit** |
| `previous_hash` | Edellisen lohkon `block_hash` (tai `null` genesisissä) |
| `block_hash` | Tämän lohkon SHA256-hash (lasketaan **koko lohkosta**) |

### 📂 Seurattavat tiedostot

Seuraavat tiedostot sisällytetään aina `files`-osiin:

- `questions.json`
- `candidates.json`
- `meta.json`
- `admins.json`
- `newquestions.json` (kun se ei ole tyhjä)

> ✅ **Huom**: Myös `*_tmp.json`-tiedostot **ei** sisällytetä ketjuun – ne ovat **vain työtila**. Vain viralliset tiedostot merkitään ketjuun **synkronoinnin yhteydessä**.

## 🔁 Päivitysprosessi

1. **Muokkaus**: Admin muokkaa sisältöä `*_tmp.json`-tiedostossa
2. **Tarkistus**: Sisältö tarkistetaan (validointi, allekirjoitus)
3. **Synkronointi**: `superadmin_setting_tool.py` kutsuu `sync_tmp_to_official()`
4. **Ketjupäivitys**:
   - Lasketaan uudet fingerprintit kaikille tiedostoille
   - Luodaan uusi lohko
   - Asetetaan `previous_hash = edellinen block_hash`
   - Lasketaan uusi `block_hash`
   - Allekirjoitetaan koko `system_chain.json` **superadminin yksityisavaimella**
5. **Tallennus**: `system_chain.json` kirjoitetaan turvallisesti (`os.replace`)

## 🔑 Rekursiivinen allekirjoitus

- **Superadmin** allekirjoittaa:
  - `system_chain.json`
  - `admins.json`
- **Puolueadmin** allekirjoittaa:
  - Oma `party_key` (tulevaisuudessa)
  - Ehdokkaiden muutokset **omassa puolueessaan**
- **Ehdokas** (valinnainen):
  - Voi allekirjoittaa omat vastauksensa

Avainparit tallennetaan:???


## 🛡️ Turvallisuus

- Kaikki `block_hash`-arvot ovat **SHA256**-tiivisteitä
- Koko `system_chain.json` allekirjoitetaan **RSA-2048**:lla
- Yksityiset avaimet **salataan salasanalla**
- `write_json()` käyttää **väliaikaistiedostoa + `os.replace()`** → ei rikkoutuneita tiloja

## 🧪 Tarkistus

Voit tarkistaa ketjun eheyden seuraavasti:

1. Laske jokaisen lohkon `block_hash` uudelleen
2. Varmista, että `block[i].previous_hash == block[i-1].block_hash`
3. Tarkista `system_chain.json`:n allekirjoitus julkisella avaimella

Tämä takaa, että **kaikki tiedostot ovat muuttumattomia** ja **kaikki muutokset on kirjattu**.



