# 🎯 Vaalijärjestelmä - TODO & Arkkitehtuuriuudistus

## 📁 UUSI HAKEMISTORAKENNE

```
vaalijarjestelma/
├── 📁 core/                          # Ydinarkkitehtuuri
│   ├── 📁 domain/                    # Domain-pohjainen rakenne
│   │   ├── 📄 entities/              # Domain-entiteetit (Question, Election, Candidate)
│   │   ├── 📄 value_objects/         # Arvokohteet (QuestionId, Rating, MultilingualText)
│   │   ├── 📄 events/                # Domain-tapahtumat
│   │   └── 📄 repositories/          # Repository-rajapinnat
│   ├── 📁 application/               # Sovelluslogiikka
│   │   ├── 📄 use_cases/             # Käyttötapaukset (SubmitQuestion, SyncQuestions)
│   │   ├── 📄 commands/              # Komentomallit
│   │   ├── 📄 queries/               # Kyselyt
│   │   └── 📄 services/              # Sovelluspalvelut
│   └── 📁 infrastructure/            # Tekninen toteutus
│       ├── 📄 persistence/           # Tietojen tallennus (JSON, IPFS)
│       ├── 📄 messaging/             # Viestintä (System Chain, IPFS)
│       ├── 📄 security/              # Turvallisuus (Fingerprint, Integrity)
│       └── 📄 config/                # Konfiguraatio
├── 📁 managers/                      # Yhdistetyt hallintamoduulit
│   ├── 📄 unified_question_handler.py    # Kysymysten hallinta
│   ├── 📄 unified_system_chain.py        # System Chain + IPFS lohkot
│   ├── 📄 integrity_manager.py           # Turvallisuus & fingerprint
│   └── 📄 ipfs_coordinator.py            # IPFS-synkronointi & ajanvaraus
├── 📁 cli/                           # Komentorivityökalut
│   ├── 📄 cli_template.py                # Yhteinen pohja
│   ├── 📄 manage_questions.py            # Kysymysten hallinta CLI
│   ├── 📄 elo_manager.py                 # ELO-laskenta CLI
│   ├── 📄 install_tool.py                # Asennustyökalu
│   ├── 📄 system_bootstrap.py            # Järjestelmän käynnistys
│   └── 📄 integrity_check.py             # Turvallisuustarkistus
├── 📁 utils/                         # Aputyökalut
│   ├── 📄 json_utils.py                  # JSON-käsittely
│   ├── 📄 file_utils.py                  # Tiedostotoiminnot
│   ├── 📄 ipfs_client.py                 # IPFS-asiakas
│   └── 📄 timestamp_utils.py             # Aikaleimojen käsittely
├── 📁 runtime/                       # Ajonaikaiset tiedostot
│   ├── 📁 base_templates/            # Template-tiedostot
│   └── 📁 data/                      # Data-tiedostot (questions.json, etc.)
└── 📁 docs/                          # Dokumentaatio
    ├── 📄 architecture.md                # Arkkitehtuurikuvaus
    └── 📄 api_reference.md               # API-viite
```

## 🔧 TEKNISET MODUULIT JA NIIDEN VASTUUT

### 🎯 **CORE - Ydinarkkitehtuuri**

#### **Domain Layer** (`core/domain/`)
- **Entiteetit**: Business-logiikka (Question, Election, Candidate)
- **Value Objects**: Immutaabelit datarakenteet (QuestionId, Rating)
- **Repositories**: Rajapinnat datan käyttöön (ei toteutusta)
- **Tarkoitus**: Puhdas business-logiikka ilman teknisiä riippuvuuksia

#### **Application Layer** (`core/application/`)
- **Use Cases**: Käyttötapaukset (SubmitQuestion, ProcessComparison)
- **Commands & Queries**: CQRS-malli datan käsittelyyn
- **Services**: Sovelluslogiikan koordinointi
- **Tarkoitus**: Koordinoi domain-logiikkaa ja infrastruktuuria

#### **Infrastructure Layer** (`core/infrastructure/`)
- **Persistence**: Toteuttaa repository-rajapinnat (JSON, IPFS)
- **Messaging**: Viestintä (System Chain, IPFS-lohkot)
- **Security**: Fingerprint-tarkistus, integriteetin valvonta
- **Config**: Konfiguraation hallinta
- **Tarkoitus**: Tekniset toteutukset eristettynä business-logista

### 🛠️ **MANAGERS - Yhdistetyt hallintamoduulit**

#### **Unified Question Handler** (`managers/unified_question_handler.py`)
- **Vastuu**: Kysymysten elinkaaren hallinta
- **Käyttää**: QuestionService + ELO-laskenta + System Chain
- **Tarjoaa**: Yhdenmukainen API kaikille kysymystoiminnoille
- **Korvaa**: `question_manager.py`, `elo_manager.py` osittain

#### **Unified System Chain** (`managers/unified_system_chain.py`)
- **Vastuu**: Lokituksen ja tapahtumien hallinta
- **Käyttää**: Perus System Chain + IPFS-lohkot
- **Tarjoaa**: Yhdenmukainen lokitus kaikille moduuleille
- **Korvaa**: `system_chain_manager.py`, `enhanced_system_chain_manager.py`

#### **Integrity Manager** (`managers/integrity_manager.py`)
- **Vastuu**: Järjestelmän eheyden valvonta
- **Käyttää**: Fingerprint-rekisteri + IPFS-lohkot
- **Tarjoaa**: Kehitys/käyttö-tila -vaihto, automaattinen tarkistus
- **Korvaa**: `enhanced_integrity_manager.py`, `production_lock_manager.py`

#### **IPFS Coordinator** (`managers/ipfs_coordinator.py`)
- **Vastuu**: IPFS-synkronointi ja ajanvaraus
- **Käyttää**: IPFS-lohkot + Schedule Manager
- **Tarjoaa**: Konfliktien välttäminen, optimoitu synkronointi
- **Korvaa**: `ipfs_sync_manager.py`, `ipfs_block_manager.py` osittain

### 💻 **CLI - Komentorivityökalut**

#### **CLI Template** (`cli/cli_template.py`)
- **Vastuu**: Yhteinen pohja kaikille CLI-ohjelmille
- **Tarjoaa**: Automaattinen alustus, virheenkäsittely, logging
- **Käyttää**: Kaikkia manager-moduuleja

#### **Manage Questions** (`cli/manage_questions.py`)
- **Vastuu**: Kysymysten hallinta käyttäjälle
- **Käyttää**: Unified Question Handler
- **Komennot**: submit, list, sync, status

#### **ELO Manager** (`cli/elo_manager.py`)
- **Vastuu**: ELO-laskennan ja vertailujen hallinta
- **Käyttää**: Unified Question Handler
- **Komennot**: compare, vote, recalculate

#### **Install Tool** (`cli/install_tool.py`)
- **Vastuu**: Järjestelmän asennus ja konfiguraatio
- **Käyttää**: Infrastructure config + IPFS Coordinator
- **Komennot**: master-install, worker-join, verify

### 🔧 **UTILS - Aputyökalut**

#### **JSON Utils** (`utils/json_utils.py`)
```python
# Yhteinen JSON-käsittely kaikille moduuleille
def load_json(file_path) -> dict
def save_json(file_path, data) -> bool
def validate_json_schema(data, schema) -> bool
```

#### **File Utils** (`utils/file_utils.py`)
```python
# Tiedostotoiminnot
def ensure_directory(path) -> bool
def calculate_file_hash(file_path) -> str
def backup_file(file_path) -> bool
```

#### **IPFS Client** (`utils/ipfs_client.py`)
```python
# Yhdenmukainen IPFS-asiakas
class StandardIPFSClient:
    def upload(data) -> str
    def download(cid) -> dict
    def get_status() -> dict
```

## 🚀 TOTEUTUSLISTA

### 📋 **VAIHE 1: Perusrakenteen luonti** (3 päivää)
- [ ] Luo uusi hakemistorakenne
- [ ] Siirrä olemassa olevat domain/application/infrastructure -tiedostot
- [ ] Toteuta `managers/unified_system_chain.py`
- [ ] Toteuta `managers/unified_question_handler.py`
- [ ] Toteuta `cli/cli_template.py`

### 📋 **VAIHE 2: Pääohjelmien uudelleenkirjoitus** (4 päivää)
- [ ] Uusi `cli/manage_questions.py` (korvaa vanhan)
- [ ] Uusi `cli/elo_manager.py` (korvaa vanhan)
- [ ] Uusi `cli/install_tool.py` (korvaa `install.py`)
- [ ] Uusi `cli/system_bootstrap.py` (parannettu versio)
- [ ] Uusi `cli/integrity_check.py` (yhdistetty turvallisuus)

### 📋 **VAIHE 3: Manager-moduulien viimeistely** (3 päivää)
- [ ] Toteuta `managers/integrity_manager.py`
- [ ] Toteuta `managers/ipfs_coordinator.py`
- [ ] Toteuta `utils/`-apumoduulit
- [ ] Integroi kaikki moduulit toisiinsa

### 📋 **VAIHE 4: Testaus ja siirto** (2 päivää)
- [ ] Testaa kaikki uudet CLI-ohjelmat
- [ ] Varmista yhteensopivuus olemassa olevan datan kanssa
- [ ] Päivitä dokumentaatio
- [ ] Siirrä tuotantokäyttöön asteittain

## 🎯 TEKNISET TUOTOKSET

### **1. Yhdenmukaiset API:t**
```python
# Kaikki CLI-ohjelmat käyttävät samaa pohjaa
from cli.cli_template import CLITemplate, main_template

class MyCLI(CLITemplate):
    def run(self):
        # Automaattinen alustus, system_chain, integrity check
        return self._handle_command()
```

### **2. Ei toistuvaa koodia**
- ❌ VANHA: Jokainen ohjelma toisti JSON-käsittelyn, loggingin, alustuksen
- ✅ UUSI: Yhteiset utils-moduulit, automaattinen alustus

### **3. Parempi testattavuus**
```python
# Manager-moduuleja on helppo testata
def test_question_handler():
    handler = UnifiedQuestionHandler()
    result = handler.submit_question(test_data, "user123")
    assert result.success == True
```

### **4. Modulaarisuus**
- Jokainen moduuli vastaa yhdestä selkeästä vastuualueesta
- Helppo korvata osa moduuleista (esim. IPFS → PostgreSQL)
- Selkeät riippuvuudet ja rajapinnat

## 💡 MIKÄ TÄMÄ KORJAA?

1. **✅ Pääohjelmien toistuva koodi** - Yhteinen CLI-pohja
2. **✅ Päällekkäiset moduulit** - Yhdistetyt managerit
3. **✅ Sekava riippuvuusjärjestys** - Selkeä layered architecture
4. **✅ Vaikea testata** - Eristetyt moduulit helpommin testattavissa
5. **✅ Monimutkainen ylläpito** - Jokaisella moduulilla yksi vastuu

Tämä uusi rakenne säilyttää kaikki nykyiset toiminnot mutta tekee niistä **modulaarisempia, ylläpidettävämpiä ja skaalautuvampia**.
