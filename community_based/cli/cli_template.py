#!/usr/bin/env python3
"""
CLI Template - Yhteinen pohja kaikille komentorivityökaluille
Tarjoaa: Automaattinen alustus, virheenkäsittely, logging
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

class CLITemplate:
    """Yhteinen pohja kaikille komentorivityökaluille"""
    
    def __init__(self, description: str, runtime_dir: str = "runtime"):
        self.description = description
        self.runtime_dir = Path(runtime_dir)
        self.initialized = False
        self.system_chain = None
        self.question_handler = None
        
    def initialize_system(self) -> bool:
        """Alusta järjestelmä - yhteinen kaikille ohjelmille"""
        try:
            print(f"🔄 Alustetaan {self.description}...")
            
            # 1. Tarkista runtime-hakemisto
            self.runtime_dir.mkdir(exist_ok=True)
            print(f"   📁 Runtime-hakemisto: {self.runtime_dir}")
            
            # 2. Alusta Unified System Chain
            try:
                from managers.unified_system_chain import get_system_chain
                self.system_chain = get_system_chain(str(self.runtime_dir))
                print("   🔗 System Chain: ✅")
            except ImportError as e:
                print(f"   🔗 System Chain: ❌ ({e})")
                self.system_chain = None
            
            # 3. Alusta Unified Question Handler
            try:
                from managers.unified_question_handler import get_question_handler
                self.question_handler = get_question_handler(str(self.runtime_dir))
                print("   ❓ Question Handler: ✅")
            except ImportError as e:
                print(f"   ❓ Question Handler: ❌ ({e})")
                self.question_handler = None
            
            # 4. Tarkista integriteetti (vain tuotantotilassa)
            if self._is_production_mode():
                print("   🔒 Tuotantotila - tarkistetaan integriteetti...")
                integrity_ok = self._check_system_integrity()
                if not integrity_ok:
                    print("❌ Järjestelmän eheys vaarantunut!")
                    return False
            else:
                print("   🔓 Kehitystila - integriteettitarkistus ohitettu")
            
            self.initialized = True
            print("✅ Järjestelmä alustettu onnistuneesti")
            return True
            
        except Exception as e:
            print(f"❌ Järjestelmän alustus epäonnistui: {e}")
            return False
    
    def _is_production_mode(self) -> bool:
        """Tarkista onko järjestelmä tuotantotilassa"""
        lock_file = self.runtime_dir / "production.lock"
        return lock_file.exists()
    
    def _check_system_integrity(self) -> bool:
        """Tarkista järjestelmän eheys"""
        try:
            from enhanced_integrity_manager import verify_system_integrity_enhanced
            
            # Hae vaali ID
            try:
                with open(self.runtime_dir / 'meta.json', 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                election_id = meta_data['election']['id']
            except:
                election_id = "unknown_election"
            
            result = verify_system_integrity_enhanced(election_id, "main_node")
            return result
            
        except ImportError:
            print("⚠️  Enhanced integrity manager ei saatavilla - jatketaan ilman tarkistusta")
            return True
        except Exception as e:
            print(f"⚠️  Integriteettitarkistus epäonnistui: {e}")
            return False
    
    def log_action(self, action_type: str, description: str, **kwargs) -> bool:
        """Yhdenmukainen lokitus kaikille CLI-ohjelmille"""
        if self.system_chain:
            result = self.system_chain.log_action(action_type, description, **kwargs)
            return result["success"]
        else:
            print(f"⚠️  System chain ei saatavilla - lokitus ohitettu: {action_type}")
            return False
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Luo perusparser - ylikirjoita tämä aliluokissa"""
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('--runtime-dir', default='runtime', help='Runtime-hakemiston polku')
        return parser
    
    def run(self) -> int:
        """Suorita ohjelma - YLIKIRJOITA TÄMÄ aliluokissa"""
        raise NotImplementedError("Ylikirjoita run()-metodi aliluokissa")
    
    def handle_error(self, error: Exception, context: str = "") -> int:
        """Yhteinen virheenkäsittely"""
        print(f"❌ Virhe {context}: {error}")
        
        # Lokita virhe system chainiin
        self.log_action(
            action_type="error_occurred",
            description=f"Virhe: {context} - {str(error)}",
            user_id="system",
            metadata={"error_type": type(error).__name__, "context": context}
        )
        
        return 1
    
    def print_success(self, message: str, details: Optional[Dict] = None):
        """Yhteinen onnistumisen tulostus"""
        print(f"✅ {message}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")

def main_template(cli_class):
    """
    Pääohjelman pohja kaikille CLI-ohjelmille
    
    Käyttö:
        class MyCLI(CLITemplate):
            def run(self):
                # Oma logiikka
                return 0
        
        if __name__ == "__main__":
            sys.exit(main_template(MyCLI))
    """
    try:
        # Luo CLI-instanssi
        cli = cli_class()
        
        # Alusta järjestelmä
        if not cli.initialize_system():
            return 1
        
        # Suorita ohjelma
        return cli.run()
        
    except KeyboardInterrupt:
        print("\n⏹️  Keskeytetty käyttäjän toimesta")
        return 1
    except Exception as e:
        print(f"❌ Odottamaton virhe: {e}")
        import traceback
        traceback.print_exc()
        return 1

# Esimerkki käytöstä
class ExampleCLI(CLITemplate):
    """Esimerkki CLI-ohjelmasta"""
    
    def __init__(self):
        super().__init__("Esimerkki CLI-ohjelma")
    
    def create_parser(self) -> argparse.ArgumentParser:
        parser = super().create_parser()
        parser.add_argument('--test', action='store_true', help='Testikomento')
        return parser
    
    def run(self) -> int:
        args = self.create_parser().parse_args()
        
        if args.test:
            print("🧪 Testikomento suoritettu!")
            
            # Esimerkki lokituksesta
            self.log_action(
                action_type="test_command",
                description="Testikomento suoritettu onnistuneesti",
                user_id="example_user"
            )
            
            self.print_success("Testi onnistui", {"runtime_dir": str(self.runtime_dir)})
            return 0
        else:
            self.create_parser().print_help()
            return 1

# Testaus
if __name__ == "__main__":
    print("🧪 CLI TEMPLATE TESTI")
    print("=" * 50)
    
    # Testaa esimerkki-CLI:ä
    sys.exit(main_template(ExampleCLI))
