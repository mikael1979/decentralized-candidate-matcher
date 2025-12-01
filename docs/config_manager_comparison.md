# 🔧 CONFIG_MANAGER-VERTAILU

## 📊 YLEISKATSAUS

| Ominaisuus | core/config_manager.py | managers/taq_config_manager.py |
|------------|------------------------|--------------------------------|
| **Koko** | 400 riviä | 201 riviä |
| **Pääluokka** | ConfigManager | TAQConfigManager |
| **Tarkoitus** | Yleinen config-hallinta | TAQ-kvoorumin spesifinen |

## 🎯 core/config_manager.py - YLEINEN CONFIG
- **Vaalikohtainen konfiguraatio**
- **Config-tiedostojen lukeminen/kirjoittaminen**
- **Config-eheyden tarkistus**
- **Config-päivityshistoria**
- **TAQ-integrointi config-päivityksiin**

## 🗳️ managers/taq_config_manager.py - TAQ-SPESIFINEN
- **TAQ-kvoorumin config-ehdotukset**
- **Config-äänestyslogiikka**
- **Proposal-hallinta**
- **Äänestysten käsittely**
- **Konsensuslaskenta**

## 🔗 RIIPPUVUUDET

core/config_manager.py → managers/taq_config_manager.py
- ConfigManager käyttää TAQConfigManageria config-päivityksissä
- TAQConfigManager on erikoistunut TAQ-toimintoihin

## 💡 KÄYTTÖTAPAUKSET

### ConfigManager (core):
```python
from src.core.config_manager import ConfigManager
manager = ConfigManager()
config = manager.get_election_config("vaali2024")
from src.managers.taq_config_manager import TAQConfigManager  
taq_manager = TAQConfigManager("vaali2024")
proposal_id = taq_manager.propose_config_update(changes, "minor", "perustelu", "node123")
