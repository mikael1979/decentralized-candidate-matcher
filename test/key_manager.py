#!/usr/bin/env python3
"""
SSH Key Manager - Apuohjelma avainten hallintaan ja tarkistukseen
"""

import os
import subprocess
import sys
from pathlib import Path

class SSHKeyManager:
    def __init__(self, key_dir="~/.ssh"):
        self.key_dir = Path(key_dir).expanduser()
    
    def check_key_permissions(self, key_name):
        """Tarkista avaimen oikeudet"""
        private_key = self.key_dir / key_name
        public_key = self.key_dir / f"{key_name}.pub"
        
        print(f"🔍 Tarkistetaan avaimen {key_name} oikeudet...")
        
        # Tarkista että tiedostot ovat olemassa
        if not private_key.exists():
            print(f"❌ Privaattia avainta ei löydy: {private_key}")
            return False
        
        if not public_key.exists():
            print(f"❌ Julkista avainta ei löydy: {public_key}")
            return False
        
        # Tarkista oikeudet
        private_stat = private_key.stat()
        public_stat = public_key.stat()
        
        # Privaatin avaimen tulee olla vain omistajan luettavissa
        private_mode = private_stat.st_mode & 0o777
        if private_mode != 0o600:
            print(f"❌ Privaatin avaimen oikeudet väärät: {oct(private_mode)} (pitäisi olla 0o600)")
            print("💡 Korjaa: chmod 600 ~/.ssh/vaalikone_superadmin")
            return False
        
        # Julkisen avaimen tulee olla luettavissa
        public_mode = public_stat.st_mode & 0o777
        if public_mode not in [0o644, 0o600]:
            print(f"⚠️  Julkisen avaimen oikeudet epätavalliset: {oct(public_mode)}")
        
        print("✅ Avaimen oikeudet OK")
        return True
    
    def show_key_fingerprint(self, key_name):
        """Näytä avaimen sormenjälki"""
        public_key = self.key_dir / f"{key_name}.pub"
        
        if not public_key.exists():
            print(f"❌ Avainta ei löydy: {public_key}")
            return
        
        try:
            result = subprocess.run(
                ["ssh-keygen", "-lf", str(public_key)],
                capture_output=True, text=True, check=True
            )
            print(f"🔑 Avaimen {key_name} sormenjälki:")
            print(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"❌ Virhe sormenjäljen luonnissa: {e}")
    
    def test_key_pair(self, key_name):
        """Testaa että avainpari on eheä"""
        private_key = self.key_dir / key_name
        
        if not private_key.exists():
            print(f"❌ Privaattia avainta ei löydy: {private_key}")
            return False
        
        try:
            # Yritä lukea julkisen avaimen privaatista avaimesta
            result = subprocess.run(
                ["ssh-keygen", "-y", "-f", str(private_key)],
                capture_output=True, text=True, check=True
            )
            print("✅ Avainpari on eheä")
            print(f"📝 Julkinen avain privaatista avaimesta:")
            print(result.stdout.strip())
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Avainpari on vioittunut tai salasana väärin: {e}")
            return False
    
    def create_new_key(self, key_name, email, key_type="ed25519"):
        """Luo uusi avainpari"""
        private_key = self.key_dir / key_name
        public_key = self.key_dir / f"{key_name}.pub"
        
        if private_key.exists() or public_key.exists():
            print(f"⚠️  Avain {key_name} on jo olemassa")
            overwrite = input("Ylikirjoitetaanko? (k/e): ").strip().lower()
            if overwrite != 'k':
                return False
        
        try:
            cmd = [
                "ssh-keygen", "-t", key_type,
                "-C", email,
                "-f", str(private_key),
                "-N", ""  # Tyhjä salasana (käyttäjä syöttää interaktiivisesti)
            ]
            
            subprocess.run(cmd, check=True)
            print(f"✅ Avainpari {key_name} luotu onnistuneesti!")
            
            # Aseta turvalliset oikeudet
            private_key.chmod(0o600)
            public_key.chmod(0o644)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Virhe avaimen luonnissa: {e}")
            return False

def main():
    """Pääfunktio"""
    manager = SSHKeyManager()
    
    print("🔑 SSH-AVAIMEN HALLINTAOHJELMA")
    print("=" * 40)
    
    while True:
        print("\nValitse toiminto:")
        print("1. Tarkista avaimen oikeudet")
        print("2. Näytä avaimen sormenjälki")
        print("3. Testaa avaimen eheys")
        print("4. Luo uusi avainpari")
        print("5. Lopeta")
        
        choice = input("Valinta (1-5): ").strip()
        
        if choice == "1":
            key_name = input("Avaimen nimi (ilman .pub): ").strip()
            manager.check_key_permissions(key_name)
        
        elif choice == "2":
            key_name = input("Avaimen nimi (ilman .pub): ").strip()
            manager.show_key_fingerprint(key_name)
        
        elif choice == "3":
            key_name = input("Avaimen nimi (ilman .pub): ").strip()
            manager.test_key_pair(key_name)
        
        elif choice == "4":
            key_name = input("Uuden avaimen nimi: ").strip()
            email = input("Sähköposti/kommentti: ").strip()
            key_type = input("Avaimen tyyppi (ed25519/rsa, oletus ed25519): ").strip() or "ed25519"
            manager.create_new_key(key_name, email, key_type)
        
        elif choice == "5":
            print("Hei hei!")
            break
        
        else:
            print("❌ Virheellinen valinta")

if __name__ == "__main__":
    main()
