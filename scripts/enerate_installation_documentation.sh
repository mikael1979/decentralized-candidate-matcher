#!/bin/bash
# generate_installation_documentation.sh
# Generoi asennusdokumentaation ja järjestelmän alustuksen

set -e

echo "📚 GENEROI ASENNUSDOKUMENTAATIO"
echo "==============================="

# Varmista, että olet oikeassa hakemistossa
if [ ! -d "src" ] || [ ! -d "base_templates" ]; then
    echo "❌ Virhe: Suorita skripti projektin juurihakemistosta"
    exit 1
fi

# Luo docs-hakemisto jos sitä ei ole
mkdir -p docs

# Tarkista riippuvuudet
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq ei ole asennettu - JSON-käsittely rajoitettu"
fi

# Luo dokumentaatiotiedosto
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DOC_FILE="docs/installation_documentation_${TIMESTAMP}.md"

cat > "$DOC_FILE" << EOF
# 🔧 Asennusdokumentaatio - Järjestelmän Alustus

## 📅 Generoitu: $(date)
## 🏛️ Vaali: Jumaltenvaalit2026

## 🎯 YLEISKUVAUS

Tämä dokumentaatio kuvaa **ensiasennusprosessin** ja **konfiguraation hallinnan** vaalikonejärjestelmässä. Se on tarkoitettu sekä **ensimmäisen noden asentajille** että **uusien noden liittäjille** hajautettuun verkkoon.

## 📋 ASENNUSPROSESSI

### 1. Ensiasennus (Master/First-node)

\`\`\`bash
# 1. Kloonaa repositorio
git clone https://github.com/mikael1979/decentralized-candidate-matcher.git
cd decentralized-candidate-matcher

# 2. Asenna riippuvuudet
pip install -r requirements.txt

# 3. Suorita ensiasennus
python src/cli/install.py --first-install --election-id "Jumaltenvaalit2026" --node-type coordinator
\`\`\`

**Mitä tämä tekee:**
- ✅ Luo \`config.json\` template-pohjalta
- ✅ Generoi \`meta.json\` ja \`system_chain.json\`
- ✅ Julkaise config IPFS:ään ja tallenna CID
- ✅ Lisää vaali \`elections_list.json\`:iin
- ✅ Luo hakemistorakenteen \`data/runtime/\`

### 2. Työaseman asennus (Worker-node)

\`\`\`bash
# 1. Hae vaalilista IPFS:stä
python src/cli/install.py --list-elections

# 2. Liity olemassa olevaan vaaliin
python src/cli/install.py --election-id "Jumaltenvaalit2026" --node-type worker
\`\`\`

**Mitä tämä tekee:**
- ✅ Lataa config IPFS:stä
- ✅ Luo yksilöllisen node-identiteetin
- ✅ Yhdistää verkkoon automaattisesti
- ✅ Säilyttää samaa data-nimiavaruutta

## ⚙️ CONFIG-JÄRJESTELMÄN YKSITYISKOHDAT

### Config-hierarkia

\`\`\`json
{
  "metadata": {
    "election_id": "Jumaltenvaalit2026",
    "version": "2.0.0",
    "config_hash": "sha256:abc123...",
    "template_hash": "sha256:def456..."
  },
  "election_config": {
    "answer_scale": {"min": -5, "max": 5},
    "confidence_scale": {"min": 1, "max": 5},
    "max_questions": 50,
    "max_candidates": 12
  },
  "system_config": {
    "data_path": "./data/runtime",
    "ipfs_api": "http://127.0.0.1:5001",
    "node_type": "coordinator"
  }
}
\`\`\`

### Tärkeimmät Config-parametrit

| Parametri | Oletus | Kuvaus |
|-----------|--------|--------|
| \`node_type\` | coordinator | coordinator/worker/validator |
| \`ipfs_mode\` | auto | real/mock/auto |
| \`max_questions\` | 50 | Maksimikysymysmäärä |
| \`answer_scale\` | -5 to +5 | Vastausten skaala |
| \`multinode_enabled\` | true | Hajautettu tila päällä |

## 🌐 HAJAUTETUN VERKON ASETUKSET

### Node-identiteetti

Jokaisella nodella on **uniikki identiteetti**:
- \`node_{timestamp}_{16merkki_fingerprint}\`
- Esim: \`node_1763806050840_ac86f6eb\`

### Bootstrap-solmut

Config tiedostossa voidaan määritellä bootstrap-solmut:
\`\`\`json
"network_config": {
  "bootstrap_nodes": [
    "QmNode123... (IPFS CID)",
    "http://192.168.1.100:8000 (HTTP endpoint)"
  ],
  "discovery_timeout": 30
}
\`\`\`

## 🔒 TURVALLISUUSASETUKSET

### Kriittiset turvamekanismit

1. **Config-eheys**:
   - \`config_hash\` tarkistetaan aina käynnistettäessä
   - Väärä hash → järjestelmä pysähtyy

2. **IPFS-mock/real-tila**:
   - Kehitystyökalut → \`mock\`-tila
   - Tuotanto → \`real\`-tila
   - Automaattinen → \`auto\`-tila

3. **Data-polku**:
   - Vaalikohtaiset hakemistot: \`data/runtime/{election_id}/\`
   - Estää datan sekoittumisen

## 🛠️ YLEISIMMÄT ONGELMAT JA RATKAISUT

### Ongelma 1: Config ei löydy

**Oireet**:
- \`ConfigurationError: No config file found\`
- \`FileNotFoundError: config.json\`

**Ratkaisu**:
\`\`\`bash
# Poista rikkinäinen config
rm config.json

# Suorita uusi asennus
python src/cli/install.py --first-install --election-id "Jumaltenvaalit2026"
\`\`\`

### Ongelma 2: IPFS-yhteys epäonnistuu

**Oireet**:
- \`IPFSConnectionError\`
- \`Connection refused\`

**Ratkaisu**:
\`\`\`bash
# 1. Tarkista IPFS-daemonin tila
ipfs daemon status || ipfs daemon &

# 2. Vaihda mock-tilaan väliaikaisesti
sed -i 's/"ipfs_mode": "real"/"ipfs_mode": "mock"/' config.json
\`\`\`

### Ongelma 3: Node-identiteetti ristiriidassa

**Oireet**:
- \`NodeConflictError\`
- \`Duplicate node ID detected\`

**Ratkaisu**:
\`\`\`bash
# 1. Poista vanha node-data
rm -rf data/nodes/*

# 2. Luo uusi identiteetti
python src/cli/install.py --election-id "Jumaltenvaalit2026" --regenerate-identity
\`\`\`

## 📊 ASENNUSSTATISTIIKKA

\`\`\`
Asennuksia yhteensä: $(grep -c '"election_id"' config/elections/*/election_config.json 2>/dev/null || echo 0)
Aktiivisia nodeja: $(find data/nodes -name "*_nodes.json" -exec jq '.nodes | length' {} + 2>/dev/null | awk '{s+=$1} END {print s}' || echo 0)
Config-versio: $(jq -r '.metadata.version' config.json 2>/dev/null || echo "Ei saatavilla")
\`\`\`

## 🚀 SEURAAVAT ASENNUSVINKIT

1. **Testaa ensin mock-tilassa**:
   \`\`\`bash
   python src/cli/install.py --first-install --election-id "Testivaalit" --ipfs-mode mock
   \`\`\`

2. **Käytä template-päivityksiä**:
   \`\`\`bash
   python src/cli/install.py --update-templates --election-id "Jumaltenvaalit2026"
   \`\`\`

3. **Varmuuskopioi ennen päivityksiä**:
   \`\`\`bash
   python src/cli/validate_data.py --backup
   \`\`\`

## 📞 LISÄTIETOJA

- [README.md](./README.md) - Perusohjeet
- [TODO.md](./TODO.md) - Seuraavat vaiheet
- [scripts/setup_jumaltenvaalit.sh](./scripts/setup_jumaltenvaalit.sh) - Automaattinen asennus
EOF

echo "✅ Asennusdokumentaatio generoitu: $DOC_FILE"
