#!/usr/bin/env python3
"""
Turvallinen JSON-tiedostojen editointityökalu
- Fingerprint-tarkistus
- Allekirjoitukset
- System Chain -päivitys
"""
import json
import os
import hashlib
import sys
import subprocess
from datetime import datetime
from pathlib import Path

class JSONEditor:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.private_key_path = 'keys/private_key.pem'
        
    def calculate_file_fingerprint(self, filepath):
        """Laskee tiedoston fingerprintin"""
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def verify_current_fingerprint(self, filepath):
        """Tarkistaa nykyisen fingerprintin system_chain:sta"""
        chain_path = os.path.join(self.data_dir, 'system_chain.json')
        if not os.path.exists(chain_path):
            return True, "System chain ei ole, luodaan uusi"
            
        with open(chain_path, 'r') as f:
            chain = json.load(f)
            
        filename = os.path.basename(filepath)
        current_state = chain.get('current_state', {})
        expected_hash = current_state.get(filename)
        
        if not expected_hash:
            return True, f"Tiedostoa {filename} ei löydy system_chainista"
            
        actual_hash = self.calculate_file_fingerprint(filepath)
        return actual_hash == expected_hash, f"Odottettu: {expected_hash}, Saatu: {actual_hash}"
    
    def sign_data(self, data):
        """Allekirjoittaa datan (yksinkertaistettu)"""
        # Käytä superadmin_työkalua allekirjoitukseen
        try:
            result = subprocess.run([
                'python', 'superadmin_setting_tool.py', 'sign-data',
                '--data', json.dumps(data)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Fallback: mock-allekirjoitus
        return f"mock_signature_{hashlib.sha256(json.dumps(data).encode()).hexdigest()[:16]}"
    
    def update_system_chain(self, modified_files):
        """Päivittää system_chain.json muutettujen tiedostojen kanssa"""
        chain_path = os.path.join(self.data_dir, 'system_chain.json')
        
        if os.path.exists(chain_path):
            with open(chain_path, 'r') as f:
                chain = json.load(f)
        else:
            chain = {
                "chain_id": "default_chain",
                "created_at": datetime.now().isoformat(),
                "blocks": [],
                "current_state": {},
                "metadata": {"algorithm": "sha256"}
            }
        
        # Päivitä current_state
        for filepath in modified_files:
            filename = os.path.basename(filepath)
            chain['current_state'][filename] = self.calculate_file_fingerprint(filepath)
        
        # Lisää uusi block
        last_block = chain['blocks'][-1] if chain['blocks'] else None
        new_block = {
            "block_id": len(chain['blocks']),
            "timestamp": datetime.now().isoformat(),
            "description": f"Muokattu tiedostoja: {', '.join(modified_files)}",
            "files": chain['current_state'].copy(),
            "previous_hash": last_block['block_hash'] if last_block else None
        }
        
        # Laske blockin hash
        block_hash = hashlib.sha256(json.dumps(new_block, sort_keys=True).encode()).hexdigest()
        new_block['block_hash'] = f"sha256:{block_hash}"
        
        chain['blocks'].append(new_block)
        
        # Tallenna
        with open(chain_path, 'w') as f:
            json.dump(chain, f, indent=2)
        
        return True
    
    def edit_interactive(self, filepath):
        """Interaktiivinen editointitila"""
        if not os.path.exists(filepath):
            print(f"❌ Tiedostoa ei löydy: {filepath}")
            return False
        
        print(f"📝 EDITOI TIEDOSTOA: {filepath}")
        print("=" * 50)
        
        # 1. Tarkista fingerprint
        is_valid, message = self.verify_current_fingerprint(filepath)
        if not is_valid:
            print(f"⚠️  VAROITUS: Fingerprint ei täsmää: {message}")
            response = input("Jatketaanko silti? (y/N): ")
            if response.lower() != 'y':
                return False
        
        # 2. Lataa data
        with open(filepath, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        print("📊 NYKYINEN SISÄLTÖ:")
        print(json.dumps(original_data, indent=2, ensure_ascii=False))
        print("\n" + "=" * 50)
        
        # 3. Kysy muutoksia
        print("\n💡 MUOKKAUSOHJEET:")
        print("• Syötä JSON-polku ja uusi arvo (esim: 'questions[0].question.fi' 'Uusi teksti')")
        print("• Lopeta syöttämällä 'save' tallentaaksesi")
        print("• Peruuta syöttämällä 'cancel'")
        print()
        
        modified_data = original_data.copy()
        changes = []
        
        while True:
            try:
                user_input = input("muutos> ").strip()
                
                if user_input.lower() == 'save':
                    break
                elif user_input.lower() == 'cancel':
                    print("❌ Muutoksia peruttu")
                    return False
                elif user_input.lower() == 'help':
                    print("💡 Komennot: save, cancel, help, show")
                elif user_input.lower() == 'show':
                    print(json.dumps(modified_data, indent=2, ensure_ascii=False))
                else:
                    # Käsittele muutos
                    parts = user_input.split(' ', 1)
                    if len(parts) == 2:
                        path, new_value = parts
                        self.apply_change(modified_data, path, new_value)
                        changes.append(f"{path} -> {new_value}")
                        print(f"✅ Muutos tallennettu: {path}")
                    else:
                        print("❌ Virheellinen muoto. Käytä: 'polku uusi_arvo'")
                        
            except (KeyboardInterrupt, EOFError):
                print("\n❌ Muutoksia peruttu")
                return False
            except Exception as e:
                print(f"❌ Virhe: {e}")
        
        if not changes:
            print("ℹ️  Ei muutoksia tallennettu")
            return True
        
        # 4. Tallenna muutokset
        print(f"\n💾 TALLENNETAAN {len(changes)} MUUTOSTA...")
        
        # Varmuuskopioi alkuperäinen
        backup_path = filepath + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(original_data, f, indent=2, ensure_ascii=False)
        
        # Tallenna uusi versio
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(modified_data, f, indent=2, ensure_ascii=False)
        
        # 5. Päivitä system chain
        if self.update_system_chain([filepath]):
            print("✅ System Chain päivitetty")
        
        # 6. Näytä yhteenveto
        print("\n📋 MUUTOSYHTEENVETO:")
        for change in changes:
            print(f"  • {change}")
        
        print(f"\n🎯 MUUTOKSET TALLENNETTU ONNISTUNEESTI!")
        print(f"📦 Varmuuskopio: {backup_path}")
        
        return True
    
    def apply_change(self, data, path, new_value):
        """Soveltaa muutoksen dataan"""
        # Yritä parsia JSON:ksi
        try:
            new_value = json.loads(new_value)
        except:
            pass  # Pysy merkkijonona
        
        keys = path.split('.')
        current = data
        
        # Navigoi polkuun
        for key in keys[:-1]:
            if '[' in key and ']' in key:
                # Array access: questions[0]
                base_key = key.split('[')[0]
                index = int(key.split('[')[1].split(']')[0])
                current = current[base_key][index]
            else:
                current = current[key]
        
        # Aseta uusi arvo
        last_key = keys[-1]
        if '[' in last_key and ']' in last_key:
            base_key = last_key.split('[')[0]
            index = int(last_key.split('[')[1].split(']')[0])
            current[base_key][index] = new_value
        else:
            current[last_key] = new_value
    
    def show_info(self, filepath):
        """Näyttää tiedoston tiedot"""
        if not os.path.exists(filepath):
            print(f"❌ Tiedostoa ei löydy: {filepath}")
            return
        
        fingerprint = self.calculate_file_fingerprint(filepath)
        is_valid, message = self.verify_current_fingerprint(filepath)
        
        print(f"📄 TIEDOSTOTIEDOT: {filepath}")
        print(f"📏 Koko: {os.path.getsize(filepath)} tavua")
        print(f"🔑 Fingerprint: {fingerprint}")
        print(f"✅ Eheys: {'PASS' if is_valid else 'FAIL'} - {message}")
        
        # Näytä pieni esikatselu
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n📊 SISÄLLÖN ESIKATSELU:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")

def main():
    if len(sys.argv) < 3:
        print("""
🛠️  JSON EDITOR - Turvallinen tiedostomuokkain

Käyttö:
  python json_editor.py edit <tiedosto>      # Interaktiivinen editointi
  python json_editor.py info <tiedosto>      # Näytä tiedot
  python json_editor.py set <tiedosto> <polku> <arvo>  # Suora asetus

Esimerkkejä:
  python json_editor.py edit data/questions.json
  python json_editor.py info data/candidates.json
  python json_editor.py set data/questions.json 'questions[0].question.fi' '"Uusi teksti"'
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    filepath = sys.argv[2]
    
    editor = JSONEditor()
    
    if command == 'edit':
        editor.edit_interactive(filepath)
    elif command == 'info':
        editor.show_info(filepath)
    elif command == 'set' and len(sys.argv) == 5:
        path = sys.argv[3]
        value = sys.argv[4]
        # Toteuta suora asetus
        print("🚧 Suora asetus - toteutus kesken")
    else:
        print(f"❌ Tuntematon komento: {command}")

if __name__ == '__main__':
    main()
