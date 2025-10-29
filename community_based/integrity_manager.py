# integrity_manager.py
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

class IntegrityManager:
    """Hallinnoi ohjelmatiedostojen integriteettivalvontaa"""
    
    def __init__(self, mode: str = "development"):
        self.mode = mode  # "development" | "production"
        self.fingerprints_file = "runtime/file_fingerprints.json"
        self.required_modules = [
            "integrity_manager.py",
            "installation_engine.py", 
            "metadata_manager.py",
            "elo_manager.py",
            "complete_elo_calculator.py",
            "system_chain_manager.py",
            "active_questions_manager.py",
            "ipfs_sync_manager.py"
        ]
    
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
    
    def verify_integrity(self, fingerprint_registry: Dict = None) -> Dict:
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
    
    def lock_system_for_production(self, ipfs_client) -> str:
        """Lukitse järjestelmä käyttötilaan ja tallenna fingerprintit IPFS:ään"""
        if self.mode != "development":
            raise ValueError("Vain kehitystilassa voi lukita järjestelmän")
        
        fingerprint_registry = self.generate_fingerprint_registry()
        fingerprint_registry["metadata"]["locked_for_production"] = datetime.now().isoformat()
        fingerprint_registry["metadata"]["mode"] = "production"
        
        # Tallennetaan paikallisesti
        with open(self.fingerprints_file, 'w', encoding='utf-8') as f:
            json.dump(fingerprint_registry, f, indent=2, ensure_ascii=False)
        
        # Tallennetaan IPFS:ään
        cid = ipfs_client.upload(fingerprint_registry)
        
        # Päivitetään system_chain
        from system_chain_manager import log_action
        log_action(
            "system_lock",
            f"Järjestelmä lukittu käyttötilaan - Fingerprint CID: {cid}",
            user_id="integrity_manager"
        )
        
        return cid
    
    def _load_fingerprint_registry(self) -> Optional[Dict]:
        """Lataa fingerprint-rekisteri"""
        try:
            with open(self.fingerprints_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

# Singleton instance
_integrity_manager = None

def get_integrity_manager(mode: str = "development") -> IntegrityManager:
    global _integrity_manager
    if _integrity_manager is None:
        _integrity_manager = IntegrityManager(mode)
    return _integrity_manager

def verify_system_integrity() -> bool:
    """Yksinkertainen API integriteetin tarkistukseen"""
    manager = get_integrity_manager()
    result = manager.verify_integrity()
    
    if not result["verified"]:
        print("🔒 INTEGRITEETTITARKISTUS EPÄONNISTUI!")
        for violation in result["violations"]:
            print(f"   ❌ {violation}")
        
        if manager.mode == "production":
            print("🚫 Järjestelmä pysäytetty turvallisuussyistä")
            sys.exit(1)
    
    return result["verified"]
