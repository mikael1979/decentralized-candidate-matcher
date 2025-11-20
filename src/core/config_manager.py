"""
Configuraatiohallinta modulaariselle vaalikoneelle
"""
import json
import os
from datetime import datetime
from pathlib import Path
import hashlib


class ConfigManager:
    """
    Keskitetty config-hallinta joka hyödyntää templatea
    """
    
    def __init__(self, config_path="config.json", template_path="templates/config.base.json"):
        self.config_path = Path(config_path)
        self.template_path = Path(template_path)
        self._config = None
        self._template = None
    
    def load_template(self):
        """Lataa config template"""
        if self._template is None:
            if not self.template_path.exists():
                raise FileNotFoundError(f"Template tiedostoa ei löydy: {self.template_path}")
            
            with open(self.template_path, 'r', encoding='utf-8') as f:
                self._template = json.load(f)
        
        return self._template
    
    def generate_config(self, election_id, node_type="coordinator", version="1.0.0"):
        """
        Generoi config tiedoston templatesta
        
        Args:
            election_id: Vaalin tunniste
            node_type: Solmun tyyppi (coordinator/worker)
            version: Järjestelmän versio
        """
        template = self.load_template()
        
        # Korvaa placeholderit
        config_json = json.dumps(template)
        replacements = {
            "{{ELECTION_ID}}": election_id,
            "{{NETWORK_ID}}": f"{election_id}_network",
            "{{NODE_TYPE}}": node_type,
            "{{TIMESTAMP}}": datetime.now().isoformat(),
            "{{VERSION}}": version
        }
        
        for placeholder, value in replacements.items():
            config_json = config_json.replace(placeholder, value)
        
        config = json.loads(config_json)
        
        # Lasketaan hash fingerprint ENNEN kuin lisätään hashit
        config_hash = self._calculate_config_hash(config)
        template_hash = self._calculate_template_hash()
        
        # Lisätään hashit configiin
        config["metadata"]["config_hash"] = config_hash
        config["metadata"]["template_hash"] = template_hash
        
        return config
    
    def save_config(self, config, path=None):
        """Tallentaa config tiedoston"""
        save_path = Path(path) if path else self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return save_path
    
    def load_config(self, path=None):
        """Lataa config tiedoston"""
        load_path = Path(path) if path else self.config_path
        
        if not load_path.exists():
            return None
        
        with open(load_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)
        
        return self._config
    
    def get_election_id(self, election_param=None):
        """
        Hae vaali-ID: parametristä tai configista
        
        Args:
            election_param: Komentoriviparametrina annettu vaali-ID
            
        Returns:
            Vaali-ID string
        """
        if election_param:
            return election_param
        
        config = self.load_config()
        if config and "metadata" in config:
            return config["metadata"].get("election_id")
        
        return None
    
    def get_data_path(self, election_id=None):
        """
        Hae data-polku vaalille
        
        Args:
            election_id: Vaali-ID (jos None, käytetään configista)
            
        Returns:
            Data-polku string
        """
        if not election_id:
            election_id = self.get_election_id()
        
        config = self.load_config()
        base_path = "./data"
        
        if config and "system_config" in config:
            base_path = config["system_config"].get("data_path", "./data")
        
        return f"{base_path}/runtime/{election_id}" if election_id else f"{base_path}/runtime"
    
    def validate_config_integrity(self, config=None):
        """
        Validoi configin eheys hasheilla
        
        Args:
            config: Validointiin käytettävä config (jos None, ladataan)
            
        Returns:
            Tuple (is_valid, message)
        """
        if config is None:
            config = self.load_config()
        
        if not config or "metadata" not in config:
            return False, "Config tiedosto puuttuu tai on virheellinen"
        
        expected_hash = config["metadata"].get("config_hash")
        if not expected_hash:
            return False, "Config hash puuttuu"
        
        current_hash = self._calculate_config_hash(config)
        if current_hash != expected_hash:
            return False, f"Config integrity check failed. Expected: {expected_hash}, Got: {current_hash}"
        
        return True, "Config integrity valid"
    
    def _calculate_config_hash(self, config):
        """Laskee config-tiedoston hash fingerprintin"""
        # Poista hashit laskennasta, jotta ne pysyvät vakiona
        config_copy = config.copy()
        if "metadata" in config_copy:
            metadata_copy = config_copy["metadata"].copy()
            if "config_hash" in metadata_copy:
                del metadata_copy["config_hash"]
            if "template_hash" in metadata_copy:
                del metadata_copy["template_hash"]
            config_copy["metadata"] = metadata_copy
        
        config_string = json.dumps(config_copy, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(config_string.encode()).hexdigest()
    
    def _calculate_template_hash(self):
        """Laskee template-tiedoston hashin"""
        template = self.load_template()
        template_string = json.dumps(template, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(template_string.encode()).hexdigest()
    
    def get_config_value(self, key_path, default=None):
        """
        Hae config arvo key pathilla (esim. "election_config.answer_scale.min")
        
        Args:
            key_path: Pisteen erottelema polku configiin
            default: Oletusarvo jos avainta ei löydy
            
        Returns:
            Config arvo tai default
        """
        config = self.load_config()
        if not config:
            return default
        
        keys = key_path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current


# Singleton instance for easy import
config_manager = ConfigManager()

# Helper functions for backward compatibility
def get_election_id(election_param=None):
    """Helper function for easy election ID access"""
    return config_manager.get_election_id(election_param)

def get_data_path(election_id=None):
    """Helper function for easy data path access"""
    return config_manager.get_data_path(election_id)
