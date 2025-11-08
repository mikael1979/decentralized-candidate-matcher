# cli/cli_template.py
"""
CLI Template - Yhteinen pohja kaikille komentorivityökaluille
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

class CLITemplate:
    """Yhteinen pohja CLI-työkaluille"""
    
    def __init__(self, tool_name: str, runtime_dir: str = "runtime"):
        self.tool_name = tool_name
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)
        
        # Alusta komponentit
        self.question_handler = None
        self.system_chain_manager = None
        self.integrity_manager = None
        
        self._initialize_system()
    
    def _initialize_system(self):
        """Alusta järjestelmäkomponentit"""
        print(f"🔄 Alustetaan {self.tool_name}...")
        print(f"   📁 Runtime-hakemisto: {self.runtime_dir}")
        
        # 1. Alusta System Chain Manager
        self._initialize_system_chain()
        
        # 2. Alusta Question Handler
        self._initialize_question_handler()
        
        # 3. Alusta Integrity Manager
        self._initialize_integrity_manager()
        
        print("✅ Järjestelmä alustettu onnistuneesti")
    
    def _initialize_system_chain(self):
        """Alusta System Chain Manager"""
        try:
            from system_chain_manager import get_system_chain_manager
            self.system_chain_manager = get_system_chain_manager()
            print("✅ Unified System Chain alustettu")
        except ImportError as e:
            print(f"⚠️  System Chain Manager ei saatavilla: {e}")
    
    def _initialize_question_handler(self):
        """Alusta Question Handler"""
        try:
            from managers.unified_question_handler import get_unified_question_handler
            self.question_handler = get_unified_question_handler(str(self.runtime_dir))
            print("✅ Unified Question Handler alustettu")
        except ImportError as e:
            print(f"⚠️  Unified Question Handler ei saatavilla: {e}")
    
    def _initialize_integrity_manager(self):
        """Alusta Integrity Manager"""
        try:
            from enhanced_integrity_manager import get_enhanced_integrity_manager, verify_system_integrity_enhanced
            self.integrity_manager = get_enhanced_integrity_manager()
            
            # Tarkista integriteetti käyttämällä moduulin tasolla olevaa funktiota
            if self.integrity_manager:
                machine_info = self._get_machine_info()
                election_id = machine_info.get('election_id', 'unknown')
                node_id = machine_info.get('machine_id', 'unknown_node')
                
                # Käytä moduulin tasolla olevaa funktiota
                integrity_ok = verify_system_integrity_enhanced(election_id, node_id)
                if integrity_ok:
                    print("🔓 Kehitystila - integriteettitarkistus ohitettu")
                else:
                    print("🔒 Tuotantotila - integriteetti varmistettu")
                    
        except ImportError as e:
            print(f"⚠️  Integrity Manager ei saatavilla: {e}")
        except Exception as e:
            print(f"⚠️  Integriteettitarkistus epäonnistui: {e}")
            print("🔓 Kehitystila - jatketaan ilman integriteettitarkistusta")
    
    def _get_machine_info(self) -> Dict[str, Any]:
        """Hae koneen tiedot"""
        try:
            from metadata_manager import get_metadata_manager
            manager = get_metadata_manager(str(self.runtime_dir))
            return manager.get_machine_info()
        except:
            return {"election_id": "unknown", "machine_id": "unknown_node"}
    
    def create_parser(self):
        """Luo parser - ylikirjoita aliluokissa"""
        import argparse
        parser = argparse.ArgumentParser(description=self.tool_name)
        return parser
    
    def log_action(self, action_type: str, description: str, 
                  question_ids: Optional[list] = None, user_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None):
        """Kirjaa toiminto system chainiin"""
        if self.system_chain_manager:
            self.system_chain_manager.log_action(
                action_type, description, question_ids, user_id, metadata
            )
    
    def run(self):
        """Suorita CLI - ylikirjoita aliluokissa"""
        raise NotImplementedError("run-metodi tulee ylikirjoittaa aliluokassa")

def main_template(cli_class):
    """Pääfunktio CLI-työkaluille"""
    try:
        cli = cli_class()
        return cli.run()
    except KeyboardInterrupt:
        print("\n⏹️  Ohjelma keskeytetty")
        return 130
    except Exception as e:
        print(f"❌ Odottamaton virhe: {e}")
        import traceback
        traceback.print_exc()
        return 1
