# 🌐 IPFS Integraation Arkkitehtuuri

## 🎯 Tavoitteet

### Päätavoitteet
1. **Hajautettu datajako** - Useat nodet voivat synkronoida dataa
2. **Data redundanssi** - Data säilyy vaikka yksittäinen node häviäisi
3. **Transparentti historia** - Kaikki muutokset tallennetaan IPFS:ään
4. **Offline-tuki** - Nodet voivat toimia offline-tilassa

### Tekniset Tavoitteet
- JSON-data synkronointi IPFS:n kautta
- Conflict resolution usean noden välillä
- Data versionointi CID:den avulla
- Mock-IPFS testausta varten

## 🏗️ Arkkitehtuuri

### Data Flow

Paikallinen Node → IPFS Network → Muut Nodet
↓ ↓ ↓
JSON-tiedot CID-referenssit Synkronointi


### Komponentit

#### 1. IPFS Manager
- Yhteys IPFS-daemoniin
- Data lisäys ja haku
- CID management

#### 2. Sync Manager
- Automaattinen synkronointi
- Conflict detection
- Change tracking

#### 3. Conflict Resolution
- Timestamp-pohjainen
- Manual intervention
- Community voting

## 📁 Toteutussuunnitelma

### Vaihe 1: Perus IPFS-integrointi
- [ ] `ipfs_manager.py` - Perus IPFS-toiminnot
- [ ] Mock-IPFS testausta varten
- [ ] JSON-data lisäys IPFS:ään

### Vaihe 2: Data Synkronointi
- [ ] `sync_manager.py` - Automaattinen synkronointi
- [ ] Conflict detection
- [ ] Change tracking

### Vaihe 3: Advanced Features
- [ ] Multi-node support
- [ ] Data versioning
- [ ] Backup & recovery

## 🔧 Tekniset Yksityiskohdat

### Data Structure IPFS:ssä
```json
{
  "election_data": {
    "questions_cid": "Qm...",
    "candidates_cid": "Qm...", 
    "parties_cid": "Qm...",
    "metadata_cid": "Qm...",
    "last_updated": "2024-01-15T10:00:00Z"
  }
}

Synkronointiprotokolla
1.Local data muuttuu

2.Data lisätään IPFS:ään → uusi CID

3.CID tallennetaan local registryyn

4.Muut nodet tarkistavat uudet CID:t

5.Data synkronoidaan tarvittaessa


### B. **Aloitus: IPFS Manager Luonnos**

**src/managers/ipfs_manager.py** (LUONNOS):
```python
#!/usr/bin/env python3
"""
IPFS Manager - Luonnos
"""
import json
from typing import Optional, Dict, Any
from datetime import datetime

class IPFSManager:
    def __init__(self, election_id: str, use_mock: bool = True):
        self.election_id = election_id
        self.use_mock = use_mock
        self.mock_store = {}  # Mock-tallennus testausta varten
    
    def add_data(self, data: Dict[str, Any]) -> str:
        """Lisää data IPFS:ään ja palauta CID"""
        if self.use_mock:
            return self._mock_add_data(data)
        else:
            return self._real_ipfs_add_data(data)
    
    def get_data(self, cid: str) -> Optional[Dict[str, Any]]:
        """Hae data IPFS:stä CID:llä"""
        if self.use_mock:
            return self._mock_get_data(cid)
        else:
            return self._real_ipfs_get_data(cid)
    
    def _mock_add_data(self, data: Dict[str, Any]) -> str:
        """Mock-toteutus data lisäykselle"""
        import hashlib
        
        # Luo mock-CID
        data_str = json.dumps(data, sort_keys=True)
        cid = f"mock_{hashlib.sha256(data_str.encode()).hexdigest()[:16]}"
        
        # Tallenna mock-tietokantaan
        self.mock_store[cid] = {
            "data": data,
            "created": datetime.now().isoformat(),
            "election_id": self.election_id
        }
        
        return cid
    
    def _mock_get_data(self, cid: str) -> Optional[Dict[str, Any]]:
        """Mock-toteutus data haulle"""
        return self.mock_store.get(cid, {}).get("data")
    
    def _real_ipfs_add_data(self, data: Dict[str, Any]) -> str:
        """Todellinen IPFS-integrointi (TOTEUTETAAN MYÖHEMMIN)"""
        # TODO: Implement real IPFS client
        raise NotImplementedError("Real IPFS integration not yet implemented")
    
    def _real_ipfs_get_data(self, cid: str) -> Optional[Dict[str, Any]]:
        """Todellinen IPFS-integrointi (TOTEUTETAAN MYÖHEMMIN)"""
        # TODO: Implement real IPFS client
        raise NotImplementedError("Real IPFS integration not yet implemented")
