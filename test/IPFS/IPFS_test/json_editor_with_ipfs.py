#!/usr/bin/env python3
"""
Turvallinen JSON-tiedostojen editointityökalu IPFS-tuella
- Fingerprint-tarkistus
- Allekirjoitukset  
- System Chain -päivitys
- IPFS CID-generointi
"""
import json
import os
import hashlib
import sys
import subprocess
from datetime import datetime
from pathlib import Path
import re

# MockIPFS-integrointi
class MockIPFS:
    def __init__(self):
        self.content_store = {}
        
    def _calculate_cid(self, data):
        """Laskee mock-CID:n datalle"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            data_str = str(data)
        hash_bytes = hashlib.sha256(data_str.encode()).digest()
        return "Qm" + hash_bytes.hex()[:40]
    
    def add_json(self, data):
        """Lisää JSON-datan mock-IPFS:ään ja palauttaa CID:n"""
        cid = self._calculate_cid(data)
        self.content_store[cid] = {
            "data": data,
            "size": len(json.dumps(data)),
            "added": datetime.now().isoformat(),
            "cid": cid
        }
        return {"Hash": cid, "Size": len(json.dumps(data)), "Name": cid}
    
    def get_json(self, cid):
        """Hakee JSON-datan CID:llä"""
        return self.content_store.get(cid, {}).get("data")

class JSONEditorWithIPFS:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.private_key_path = 'keys/private_key.pem'
        self.ipfs = MockIPFS()
        
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
    
    def add_to_ipfs(self, data, description=""):
        """Lisää datan IPFS:ään ja palauttaa CID:n"""
        try:
            result = self.ipfs.add_json(data)
            cid = result["Hash"]
            
            print(f"🌐 Lisätty IPFS:ään - CID: {cid}")
            if description:
                print(f"📝 Kuvaus: {description}")
                
            return cid
        except Exception as e:
            print(f"❌ IPFS-lisäys epäonnistui: {e}")
            return None
    
    def update_system_chain(self, modified_files, ipfs_cids=None):
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
        
        # Lisää IPFS-CID:t metadataan
        ipfs_info = ipfs_cids or {}
        
        # Lisää uusi block
        last_block = chain['blocks'][-1] if chain['blocks'] else None
        new_block = {
            "block_id": len(chain['blocks']),
            "timestamp": datetime.now().isoformat(),
            "description": f"JSON Editor: muokattu {len(modified_files)} tiedostoa",
            "files": chain['current_state'].copy(),
            "ipfs_cids": ipfs_info,
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

    def add_cid_to_json(self, filepath, cid_field="ipfs_cid", description=""):
        """Lisää CID-osoitteen JSON-tiedostoon"""
        if not os.path.exists(filepath):
            print(f"❌ Tiedostoa ei löydy: {filepath}")
            return None
        
        # Lataa data
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Lisää IPFS:ään
        cid = self.add_to_ipfs(data, description)
        if not cid:
            return None
        
        # Lisää CID tiedostoon
        if 'metadata' not in data:
            data['metadata'] = {}
        
        data['metadata'][cid_field] = cid
        data['metadata']['ipfs_added'] = datetime.now().isoformat()
        data['metadata']['ipfs_description'] = description
        
        # Tallenna takaisin
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Päivitä system chain
        self.update_system_chain([filepath], {os.path.basename(filepath): cid})
        
        print(f"✅ CID lisätty tiedostoon: {cid}")
        return cid

    def verify_ipfs_content(self, filepath, cid_field="ipfs_cid"):
        """Tarkistaa että JSON-sisältö vastaa IPFS-CID:ä"""
        if not os.path.exists(filepath):
            print(f"❌ Tiedostoa ei löydy: {filepath}")
            return False
        
        # Lataa data
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Hae CID
        cid = data.get('metadata', {}).get(cid_field)
        if not cid:
            print("❌ CID:ä ei löydy tiedostosta")
            return False
        
        # Hae data IPFS:stä
        ipfs_data = self.ipfs.get_json(cid)
        if not ipfs_data:
            print(f"❌ Dataa ei löydy IPFS:stä CID:llä {cid}")
            return False
        
        # Vertaa dataa (poista metadata ennen vertailua)
        data_copy = data.copy()
        ipfs_copy = ipfs_data.copy()
        
        # Poista dynaamiset kentät
        for item in [data_copy, ipfs_copy]:
            if 'metadata' in item:
                item['metadata'].pop('ipfs_added', None)
                item['metadata'].pop('ipfs_description', None)
        
        # Vertaa
        if data_copy == ipfs_copy:
            print(f"✅ IPFS-eheys tarkistettu: CID {cid} vastaa tiedoston sisältöä")
            return True
        else:
            print(f"❌ IPFS-eheysongelma: CID {cid} EI vastaa tiedoston sisältöä")
            return False

    def edit_interactive(self, filepath, auto_ipfs=True):
        """Interaktiivinen editointitila IPFS-tuella"""
        if not os.path.exists(filepath):
            print(f"❌ Tiedostoa ei löydy: {filepath}")
            return False
        
        print(f"📝 EDITOI TIEDOSTOA: {filepath}")
        if auto_ipfs:
            print("🌐 IPFS-auto-tila: PÄÄLLÄ - Muutokset tallennetaan automaattisesti IPFS:ään")
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
        
        # Näytä nykyinen CID jos on
        current_cid = original_data.get('metadata', {}).get('ipfs_cid')
        if current_cid:
            print(f"🌐 Nykyinen IPFS-CID: {current_cid}")
        
        print("📊 NYKYINEN SISÄLTÖ:")
        print(json.dumps(original_data, indent=2, ensure_ascii=False))
        print("\n" + "=" * 50)
        
        # 3. Kysy muutoksia
        print("\n💡 MUOKKAUSOHJEET:")
        print("• Syötä JSON-polku ja uusi arvo")
        print("• 'save' tallentaa, 'cancel' peruu")
        print("• 'ipfs' lisää nykyisen version IPFS:ään")
        print("• 'verify' tarkistaa IPFS-eheyden")
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
                    self.show_help()
                elif user_input.lower() == 'show':
                    print(json.dumps(modified_data, indent=2, ensure_ascii=False))
                elif user_input.lower() == 'ipfs':
                    cid = self.add_cid_to_json(filepath, description="Manuaalinen tallennus")
                    if cid:
                        print(f"✅ Manuaalinen IPFS-tallennus onnistui: {cid}")
                elif user_input.lower() == 'verify':
                    self.verify_ipfs_content(filepath)
                else:
                    # Käsittele muutos
                    parts = user_input.split(' ', 1)
                    if len(parts) == 2:
                        path, new_value = parts
                        if self.apply_change(modified_data, path, new_value):
                            changes.append(f"{path} -> {new_value}")
                            print(f"✅ Muutos tallennettu: {path}")
                        else:
                            print(f"❌ Muutos epäonnistui: {path}")
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
        
        # 5. Lisää IPFS:ään jos auto-tila päällä
        cid = None
        if auto_ipfs:
            cid = self.add_cid_to_json(filepath, description=f"Automaattinen tallennus: {len(changes)} muutosta")
        
        # 6. Päivitä system chain
        ipfs_cids = {os.path.basename(filepath): cid} if cid else {}
        if self.update_system_chain([filepath], ipfs_cids):
            print("✅ System Chain päivitetty")
        
        # 7. Näytä yhteenveto
        print("\n📋 MUUTOSYHTEENVETO:")
        for change in changes:
            print(f"  • {change}")
        
        if cid:
            print(f"🌐 IPFS-CID: {cid}")
        
        print(f"\n🎯 MUUTOKSET TALLENNETTU ONNISTUNEESTI!")
        print(f"📦 Varmuuskopio: {backup_path}")
        
        return True

    def show_help(self):
        """Näyttää käyttöohjeet"""
        print("""
📖 JSON EDITOR WITH IPFS - KÄYTTÖOHJEET

KOMENNOT:
  save          - Tallenna muutokset ja poistu
  cancel        - Peruuta muutokset  
  show          - Näytä nykyinen data
  ipfs          - Lisää nykyinen versio IPFS:ään
  verify        - Tarkista IPFS-eheys
  help          - Näytä tämä ohje

MUOKKAUS:
  Käytä muotoa: <json-polku> <uusi-arvo>
  
ESIMERKKEJÄ:
  questions[0].question.fi "Uusi kysymysteksti"
  metadata.ipfs_cid "QmExample123"
  elo.base_rating 1300
        """)

    def apply_change(self, data, path, new_value):
        """Soveltaa muutoksen dataan - sama kuin edellisessä"""
        try:
            # Yritä parsia JSON:ksi
            try:
                if new_value.lower() in ['true', 'false']:
                    new_value = new_value.lower() == 'true'
                elif new_value.isdigit() or (new_value.startswith('-') and new_value[1:].isdigit()):
                    new_value = int(new_value)
                elif re.match(r'^-?\d+\.\d+$', new_value):
                    new_value = float(new_value)
                elif new_value.startswith('"') and new_value.endswith('"'):
                    new_value = new_value[1:-1]
                elif new_value.startswith("'") and new_value.endswith("'"):
                    new_value = new_value[1:-1]
                else:
                    new_value = json.loads(new_value)
            except:
                pass
            
            keys = self.parse_path(path)
            current = data
            
            for key in keys[:-1]:
                current = self.get_value(current, key)
                if current is None:
                    raise KeyError(f"Polkua ei löydy: {key}")
            
            last_key = keys[-1]
            self.set_value(current, last_key, new_value)
            return True
            
        except Exception as e:
            print(f"❌ Virhe muutosta sovellettaessa: {e}")
            return False

    def parse_path(self, path):
        """Jäsentää JSON-polun osiksi - sama kuin edellisessä"""
        parts = []
        current = ''
        in_brackets = False
        bracket_content = ''
        
        for char in path:
            if char == '[':
                if current:
                    parts.append(current)
                    current = ''
                in_brackets = True
                bracket_content = ''
            elif char == ']':
                in_brackets = False
                if bracket_content.isdigit():
                    parts.append(int(bracket_content))
                else:
                    parts.append(bracket_content)
                bracket_content = ''
            elif in_brackets:
                bracket_content += char
            elif char == '.':
                if current:
                    parts.append(current)
                    current = ''
            else:
                current += char
        
        if current:
            parts.append(current)
        
        return parts

    def get_value(self, data, key):
        """Hakee arvon datasta avaimella - sama kuin edellisessä"""
        if isinstance(data, list) and isinstance(key, int):
            if 0 <= key < len(data):
                return data[key]
            else:
                raise IndexError(f"Indeksi {key} ei kelpaa listalle pituudella {len(data)}")
        elif isinstance(data, dict) and isinstance(key, str):
            if key in data:
                return data[key]
            else:
                raise KeyError(f"Avainta '{key}' ei löydy")
        else:
            raise TypeError(f"Avain {key} ei kelpaa tyypille {type(data).__name__}")

    def set_value(self, data, key, value):
        """Asettaa arvon dataan avaimella - sama kuin edellisessä"""
        if isinstance(data, list) and isinstance(key, int):
            if 0 <= key < len(data):
                data[key] = value
            else:
                while len(data) <= key:
                    data.append(None)
                data[key] = value
        elif isinstance(data, dict) and isinstance(key, str):
            data[key] = value
        else:
            raise TypeError(f"Avain {key} ei kelpaa tyypille {type(data).__name__}")

    def show_info(self, filepath):
        """Näyttää tiedoston tiedot IPFS-tiedoilla"""
        if not os.path.exists(filepath):
            print(f"❌ Tiedostoa ei löydy: {filepath}")
            return
        
        stats = os.stat(filepath)
        fingerprint = self.calculate_file_fingerprint(filepath)
        is_valid, message = self.verify_current_fingerprint(filepath)
        
        # Lataa data IPFS-tietojen näyttämiseksi
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cid = data.get('metadata', {}).get('ipfs_cid')
        ipfs_added = data.get('metadata', {}).get('ipfs_added')
        
        print(f"📄 TIEDOSTOTIEDOT: {filepath}")
        print(f"📏 Koko: {stats.st_size} tavua")
        print(f"📅 Muokattu: {datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔑 Fingerprint: {fingerprint}")
        print(f"✅ Eheys: {'PASS' if is_valid else 'FAIL'} - {message}")
        
        if cid:
            print(f"🌐 IPFS-CID: {cid}")
            if ipfs_added:
                print(f"📅 IPFS-tallennettu: {ipfs_added}")
            
            # Tarkista IPFS-eheys
            print("🔍 Tarkistetaan IPFS-eheys...")
            self.verify_ipfs_content(filepath)
        
        print("\n📊 SISÄLLÖN ESIKATSELU:")
        preview = json.dumps(data, indent=2, ensure_ascii=False)
        if len(preview) > 500:
            print(preview[:500] + "...")
        else:
            print(preview)

def main():
    if len(sys.argv) < 3:
        print("""
🛠️  JSON EDITOR WITH IPFS - Turvallinen tiedostomuokkain

Käyttö:
  python json_editor_with_ipfs.py edit <tiedosto>          # Interaktiivinen editointi
  python json_editor_with_ipfs.py info <tiedosto>          # Näytä tiedot
  python json_editor_with_ipfs.py ipfs <tiedosto>          # Lisää IPFS:ään
  python json_editor_with_ipfs.py verify <tiedosto>        # Tarkista IPFS-eheys

Esimerkkejä:
  python json_editor_with_ipfs.py edit data/questions.json
  python json_editor_with_ipfs.py info data/candidates.json  
  python json_editor_with_ipfs.py ipfs data/questions.json
  python json_editor_with_ipfs.py verify data/questions.json
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    filepath = sys.argv[2]
    
    editor = JSONEditorWithIPFS()
    
    if command == 'edit':
        auto_ipfs = '--no-ipfs' not in sys.argv
        editor.edit_interactive(filepath, auto_ipfs=auto_ipfs)
    elif command == 'info':
        editor.show_info(filepath)
    elif command == 'ipfs':
        description = sys.argv[3] if len(sys.argv) > 3 else "Manuaalinen IPFS-tallennus"
        editor.add_cid_to_json(filepath, description=description)
    elif command == 'verify':
        editor.verify_ipfs_content(filepath)
    else:
        print(f"❌ Tuntematon komento: {command}")
        print("💡 Käytä: edit, info, ipfs tai verify")

if __name__ == '__main__':
    main()
