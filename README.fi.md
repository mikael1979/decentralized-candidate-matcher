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
