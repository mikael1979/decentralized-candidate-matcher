#!/bin/bash
# generate_managers_documentation.sh
# Generoi hallintamoduulien dokumentaation

set -e

echo "🧩 GENEROI MANAGER-DOKUMENTAATIO"
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
DOC_FILE="docs/managers_documentation_${TIMESTAMP}.md"

cat > "$DOC_FILE" << EOF
# 🧩 Hallintamoduulit - Managers Documentation

## 📅 Generoitu: $(date)
## 🏛️ Vaali: Jumaltenvaalit2026

## 🔑 CRYPTO MANAGER (`src/managers/crypto_manager.py`)

### Tarkoitus
PKI-avainten hallinta ja digitaalisten allekirjoitusten toteutus

### Keskeiset metodit
- \`generate_key_pair()\` - Luo RSA-avainparin
- \`sign_data()\` - Allekirjoittaa datan yksityisavaimella
- \`verify_signature()\` - Varmistaa allekirjoituksen julkinen avain
- \`calculate_fingerprint()\` - Laskee avaimen sormenjäljen

### Käyttöesimerkki
\`\`\`python
crypto = CryptoManager()
keys = crypto.generate_key_pair()
signature = crypto.sign_data(keys["private_key"], {"data": "voting"})
is_valid = crypto.verify_signature(keys["public_key"], {"data": "voting"}, signature)
\`\`\`

### Riippuvuudet
- \`cryptography\`-kirjasto
- SHA-256 hash-algoritmi

## ⚖️ QUORUM MANAGER (`src/managers/quorum_manager.py`)

### Tarkoitus
Hajautettu päätöksenteko ja puolueiden vahvistus

### Nykyinen malli
- **3/3-kvoorumi** - Kaikkien nodeiden täytyy hyväksyä
- **Käytössä**: Puolueiden rekisteröinti, kriittiset muutokset

### Siirtymä TAQ-malliin
- **Tiered Adaptive Quorum** - Dynaaminen kynnys
- **Trust-tiers**: foundation (3.0), verified (2.0), standard (1.0), new (0.5)
- **Aikamäärät**: Nopea vahvistus (24h) → Vakaa (7vrk) → Manuaalinen

### Käyttöesimerkki
\`\`\`python
quorum = QuorumManager("Jumaltenvaalit2026")
proposal_id = quorum.start_vote("new_party", {"name": "Olympos United"}, min_approvals=2)
quorum.cast_vote(proposal_id, "node_zeus", "approve", public_key)
status = quorum.get_vote_status(proposal_id)
\`\`\`

## 📈 ELO MANAGER (`src/managers/elo_manager.py`)

### Tarkoitus
Kysymysten laadun arviointi ja priorisointi

### Matemaattinen malli
- **Perusrating**: 1000
- **K-factor**: 32 (sensitiivisyys)
- **Odotusarvo**: \`1 / (1 + 10^((rating_b - rating_a) / 400))\`
- **Uusi luokitus**: \`rating + K * (actual - expected)\`

### Käyttö CLI:ssä
\`\`\`bash
# Automaattinen vertailu (5 kierrosta)
python src/cli/compare_questions.py --election Jumaltenvaalit2026 --auto 5

# Interaktiivinen vertailu
python src/cli/compare_questions.py --election Jumaltenvaalit2026
\`\`\`

### Tilastomittarit
- Keskitaso: \`jq '.questions | map(.elo_rating) | add / length' data/runtime/questions.json\`
- Top 5 kysymystä: \`jq '.questions | sort_by(.elo_rating) | reverse | limit(5; .)'\`

## 🌐 IPFS SYNC MANAGER (`src/managers/ipfs_sync_manager.py`)

### Tarkoitus
Tehokas data-synkronointi IPFS-verkkoon

### Synkronointistrategiat
| Strategia | Käyttötapaus | Tehokkuus | 
|-----------|------------|-----------|
| Täysi synkronointi | Ensimmäinen kerta | 100% data |
| Delta-synkronointi | Päivitykset | 70-90% säästö |
| Arkistointi | Backupit | Tiivis pakkaus |

### Koodin rakenne
```python
class IPFSSyncManager:
    def full_sync(self):  # Kaikki tiedostot
    def incremental_sync(self):  # Vain muuttuneet
    def verify_integrity(self):  # Eheystarkistus
    def publish_config(self):  # Config-julkaisu
