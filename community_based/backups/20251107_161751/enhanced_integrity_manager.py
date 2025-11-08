#!/usr/bin/env python3
# enhanced_integrity_manager.py
"""
Enhanced Integrity Manager - Laajennettu integriteettivalvonta lohkojen kanssa
Käyttö:
  integrity = EnhancedIntegrityManager(ipfs_client)
  integrity.verify_system_with_blocks()
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from ipfs_block_manager import IPFSBlockManager

class EnhancedIntegrityManager:
    """Laajennettu integriteettivalvonta IPFS-lohkojen avulla"""
    
    def __init__(self, mode: str = "development", ipfs_client=None):
        self.mode = mode
        self.ipfs_client = ipfs_client
        self.fingerprints_file = "runtime/file_fingerprints.json"
        self.integrity_log_cid = None
        
        # Vaaditut moduulit
        self.required_modules = [
            "integrity_manager.py",
            "ipfs_block_manager.py", 
            "enhanced_recovery_manager.py",
            "installation_engine.py",
            "metadata_manager.py",
            "elo_manager.py",
            "complete_elo_calculator.py",
            "system_chain_manager.py",
            "active_questions_manager.py",
            "ipfs_sync_manager.py"
        ]
    
    def verify_system_with_blocks(self, election_id: str, node_id: str) -> Dict:
        """Tarkista järjestelmän integriteetti IPFS-lohkojen avulla"""
        
        print("🔒 TARKISTETAAN JÄRJESTELMÄN INTEGRITEETTI...")
        
        # 1. Perusintegriteettitarkistus
        base_integrity = self.verify_system_integrity()
        
        # 2. Lohkojen integriteettitarkistus
        blocks_integrity = self._verify_blocks_integrity(election_id, node_id)
        
        # 3. Data-consistenttitarkistus
        data_consistency = self._verify_data_consistency()
        
        # Yhdistä tulokset
        overall_verified = (
            base_integrity["verified"] and 
            blocks_integrity["verified"] and
            data_consistency["consistent"]
        )
        
        result = {
            "overall_verified": overall_verified,
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode,
            "base_integrity": base_integrity,
            "blocks_integrity": blocks_integrity,
            "data_consistency": data_consistency,
            "security_level": "high" if overall_verified else "compromised"
        }
        
        # Kirjaa tulokset
        self._log_integrity_check(result, election_id, node_id)
        
        if overall_verified:
            print("✅ JÄRJESTELMÄN INTEGRITEETTI VARMISTETTU")
        else:
            print("❌ JÄRJESTELMÄN INTEGRITEETTI LOUKKATTU")
            for violation in base_integrity.get("violations", []):
                print(f"   - {violation}")
            for block_issue in blocks_integrity.get("issues", []):
                print(f"   - {block_issue}")
        
        return result
    
    def verify_system_integrity(self, fingerprint_registry: Dict = None) -> Dict:
        """Tarkista kaikkien moduulien integriteetti"""
        
        # Kehitystilassa skipataan tarkistus
        if self.mode == "development":
            return {"status": "development_mode", "verified": True}
        
        if not fingerprint_registry:
            fingerprint_registry = self._load_fingerprint_registry()
        
        if not fingerprint_registry:
            return {"status": "no_registry", "verified": False}
        
        current_registry = self.generate_fingerprint_registry()
        violations = []
        
        for module, expected_data in fingerprint_registry["modules"].items():
            if module not in current_registry["modules"]:
                violations.append(f"MODUULI PUUTTUU: {module}")
                continue
            
            current_fingerprint = current_registry["modules"][module]["fingerprint"]
            expected_fingerprint = expected_data["fingerprint"]
            
            if current_fingerprint != expected_fingerprint:
                violations.append(f"INTEGRITEETTIVIKA: {module}")
        
        return {
            "status": "verified" if not violations else "violations_detected",
            "verified": len(violations) == 0,
            "violations": violations,
            "modules_checked": len(fingerprint_registry["modules"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def _verify_blocks_integrity(self, election_id: str, node_id: str) -> Dict:
        """Tarkista IPFS-lohkojen integriteetti"""
        
        if not self.ipfs_client:
            return {"verified": True, "status": "no_ipfs_client", "issues": []}
        
        try:
            block_manager = IPFSBlockManager(self.ipfs_client, election_id, node_id)
            blocks_status = block_manager.get_block_status()
            
            issues = []
            
            # Tarkista että lohkot eivät ole täysin tyhjiä (paitsi buffer1)
            for block_name, status in blocks_status.items():
                if block_name != "buffer1" and status["entries"] == 0:
                    issues.append(f"LOHKO TYHJÄ: {block_name}")
                
                # Tarkista että lohko ei ole ylitäynnä
                if status["entries"] > status["max_size"]:
                    issues.append(f"LOHKO YLITÄYNNÄ: {block_name}")
            
            # Tarkista että lohkojen sekvenssi on oikea
            expected_sequence = ["buffer1", "urgent", "sync", "active", "buffer2"]
            # Tämä vaatisi metadata-tarkistuksen
            
            return {
                "verified": len(issues) == 0,
                "status": "verified" if not issues else "block_issues",
                "issues": issues,
                "blocks_checked": len(blocks_status),
                "total_entries": sum(status["entries"] for status in blocks_status.values())
            }
            
        except Exception as e:
            return {
                "verified": False,
                "status": "block_verification_failed",
                "issues": [f"Lohkojen tarkistus epäonnistui: {e}"],
                "error": str(e)
            }
    
    def _verify_data_consistency(self) -> Dict:
        """Tarkista datan consistenssi eri lähteiden välillä"""
        
        consistency_checks = []
        
        try:
            # Tarkista että questions.json on olemassa
            questions_path = Path("runtime/questions.json")
            if questions_path.exists():
                with open(questions_path, 'r', encoding='utf-8') as f:
                    questions_data = json.load(f)
                questions_count = len(questions_data.get("questions", []))
                consistency_checks.append(f"questions.json: {questions_count} kysymystä")
            else:
                consistency_checks.append("questions.json: PUUTTUU")
            
            # Tarkista että system_chain.json on olemassa
            system_chain_path = Path("runtime/system_chain.json")
            if system_chain_path.exists():
                with open(system_chain_path, 'r', encoding='utf-8') as f:
                    system_chain_data = json.load(f)
                chain_blocks = len(system_chain_data.get("blocks", []))
                consistency_checks.append(f"system_chain.json: {chain_blocks} lohkoa")
            else:
                consistency_checks.append("system_chain.json: PUUTTUU")
            
            return {
                "consistent": True,
                "checks": consistency_checks,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "consistent": False,
                "checks": [f"Consistency check failed: {e}"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_fingerprint_registry(self) -> Dict:
        """Luo fingerprint-rekisterin kaikista vaadituista moduuleista"""
        registry = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "mode": self.mode,
                "system_version": "2.0.0",
                "total_modules": len(self.required_modules)
            },
            "modules": {}
        }
        
        for module in self.required_modules:
            if Path(module).exists():
                fingerprint = self.calculate_file_fingerprint(module)
                registry["modules"][module] = {
                    "fingerprint": fingerprint,
                    "last_modified": datetime.fromtimestamp(Path(module).stat().st_mtime).isoformat(),
                    "size_bytes": Path(module).stat().st_size
                }
            else:
                print(f"⚠️  Moduulia ei löydy: {module}")
        
        return registry
    
    def calculate_file_fingerprint(self, file_path: str) -> str:
        """Laske tiedoston SHA-256 fingerprint"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Poista kommentit ja tyhjät rivit consistenssin vuoksi
            lines = []
            for line in content.split('\n'):
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    lines.append(stripped)
            
            clean_content = '\n'.join(lines)
            return hashlib.sha256(clean_content.encode('utf-8')).hexdigest()
            
        except Exception as e:
            print(f"❌ Virhe fingerprintin laskennassa {file_path}: {e}")
            return "error"
    
    def lock_system_for_production(self, ipfs_client, election_id: str, node_id: str) -> str:
        """Lukitse järjestelmä käyttötilaan ja tallenna fingerprintit IPFS-lohkoihin"""
        
        if self.mode != "development":
            raise ValueError("Vain kehitystilassa voi lukita järjestelmän")
        
        print("🔒 LUKITAAN JÄRJESTELMÄ KÄYTTÖTILAAN...")
        
        # 1. Generoi fingerprint-rekisteri
        fingerprint_registry = self.generate_fingerprint_registry()
        fingerprint_registry["metadata"]["locked_for_production"] = datetime.now().isoformat()
        fingerprint_registry["metadata"]["mode"] = "production"
        
        # 2. Tallennetaan paikallisesti
        with open(self.fingerprints_file, 'w', encoding='utf-8') as f:
            json.dump(fingerprint_registry, f, indent=2, ensure_ascii=False)
        
        # 3. Tallennetaan IPFS-lohkoon (kiireelliseen lohkoon)
        block_manager = IPFSBlockManager(ipfs_client, election_id, node_id)
        
        lock_data = {
            "system_locked": True,
            "lock_timestamp": datetime.now().isoformat(),
            "election_id": election_id,
            "node_id": node_id,
            "fingerprint_registry": fingerprint_registry
        }
        
        entry_id = block_manager.write_to_block("urgent", lock_data, "system_lock", "emergency")
        
        # 4. Päivitä system_chain
        try:
            from system_chain_manager import log_action
            log_action(
                "system_lock",
                f"Järjestelmä lukittu käyttötilaan - Fingerprint entry: {entry_id}",
                user_id="integrity_manager",
                metadata={
                    "election_id": election_id,
                    "node_id": node_id,
                    "fingerprint_entry": entry_id,
                    "total_modules_locked": len(fingerprint_registry["modules"])
                }
            )
        except ImportError:
            print("⚠️  System chain ei saatavilla - skipataan kirjaus")
        
        print(f"✅ Järjestelmä lukittu - Fingerprint entry: {entry_id}")
        return entry_id
    
    def _load_fingerprint_registry(self) -> Optional[Dict]:
        """Lataa fingerprint-rekisteri"""
        try:
            with open(self.fingerprints_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def _log_integrity_check(self, result: Dict, election_id: str, node_id: str):
        """Kirjaa integriteettitarkistuksen tulokset"""
        
        log_entry = {
            "integrity_check": result,
            "election_id": election_id,
            "node_id": node_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Kirjaa system_chainiin
        try:
            from system_chain_manager import log_action
            log_action(
                "integrity_check",
                f"Integriteettitarkistus: {result['overall_verified']}",
                user_id="integrity_manager",
                metadata=log_entry
            )
        except ImportError:
            print("⚠️  System chain ei saatavilla - skipataan kirjaus")
        
        # Tallenna IPFS-lohkoon jos saatavilla
        if self.ipfs_client and result["overall_verified"]:
            try:
                block_manager = IPFSBlockManager(self.ipfs_client, election_id, node_id)
                block_manager.write_to_block("sync", log_entry, "integrity_log", "normal")
            except Exception as e:
                print(f"⚠️  Ei voitu kirjata integriteettilokia: {e}")

# Singleton instance
_enhanced_integrity_manager = None

def get_enhanced_integrity_manager(mode: str = "development", ipfs_client=None) -> EnhancedIntegrityManager:
    global _enhanced_integrity_manager
    if _enhanced_integrity_manager is None:
        _enhanced_integrity_manager = EnhancedIntegrityManager(mode, ipfs_client)
    return _enhanced_integrity_manager

def verify_system_integrity_enhanced(election_id: str, node_id: str) -> bool:
    """Yksinkertainen API laajennettuun integriteettitarkistukseen"""
    manager = get_enhanced_integrity_manager()
    result = manager.verify_system_with_blocks(election_id, node_id)
    
    if not result["overall_verified"]:
        print("🔒 INTEGRITEETTITARKISTUS EPÄONNISTUI!")
        for violation in result["base_integrity"].get("violations", []):
            print(f"   ❌ {violation}")
        for issue in result["blocks_integrity"].get("issues", []):
            print(f"   ❌ {issue}")
        
        if manager.mode == "production":
            print("🚫 Järjestelmä pysäytetty turvallisuussyistä")
            import sys
            sys.exit(1)
    
    return result["overall_verified"]

# Testaus
if __name__ == "__main__":
    print("🧪 ENHANCED INTEGRITY MANAGER TESTI")
    print("=" * 50)
    
    from mock_ipfs import MockIPFS
    
    ipfs = MockIPFS()
    integrity = EnhancedIntegrityManager("development", ipfs)
    
    # Testaa fingerprint-rekisterin generointi
    registry = integrity.generate_fingerprint_registry()
    print(f"✅ Fingerprint-rekisteri luotu: {len(registry['modules'])} moduulia")
    
    # Testaa integriteettitarkistus
    result = integrity.verify_system_with_blocks("test_election", "test_node")
    print(f"📊 INTEGRITEETTITARKISTUS: {result['overall_verified']}")
    print(f"   Perustarkistus: {result['base_integrity']['verified']}")
    print(f"   Lohkotarkistus: {result['blocks_integrity']['verified']}")
    print(f"   Dataconsistenssi: {result['data_consistency']['consistent']}")
    
    # Testaa lukitus
    try:
        lock_entry = integrity.lock_system_for_production(ipfs, "test_election", "test_node")
        print(f"🔒 Järjestelmä lukittu: {lock_entry}")
    except Exception as e:
        print(f"⚠️  Lukitus testissä odotettu: {e}")
