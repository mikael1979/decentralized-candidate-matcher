# initialization.py
import json
import shutil
from datetime import datetime

class FileInitializer:
    def __init__(self, base_dir="base_templates", runtime_dir="runtime"):
        self.base_dir = base_dir
        self.runtime_dir = runtime_dir
        
    def initialize_runtime_files(self):
        """Kloonaa base-tiedostot runtime-kansioon"""
        base_files = [
            'questions.base.json', 'meta.base.json', 'governance.base.json',
            'community.base.json', 'install_config.base.json', 
            'system_chain.base.json', 'ipfs.base.json', 'ipfs_conf.base.json'
        ]
        
        for base_file in base_files:
            runtime_file = base_file.replace('.base.json', '.json')
            source_path = f"{self.base_dir}/{base_file}"
            target_path = f"{self.runtime_dir}/{runtime_file}"
            
            # Kloonaa base -> runtime
            shutil.copy2(source_path, target_path)
            print(f"Kloonattu: {source_path} -> {target_path}")
            
        # Alusta tyhjät runtime-tiedostot
        self.initialize_empty_runtime_files()
        
    def initialize_empty_runtime_files(self):
        """Alusta tyhjät runtime-tiedostot"""
        empty_files = [
            'new_questions.json',
            'active_questions.json', 
            'ipfs_questions.json',
            'parties.json',
            'party_profiles.json',
            'candidates.json',
            'candidate_profiles.json'
        ]
        
        for file in empty_files:
            file_path = f"{self.runtime_dir}/{file}"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "1.0.0",
                        "source": "empty_initialization"
                    },
                    "data": []
                }, f, indent=2, ensure_ascii=False)
            
            print(f"Alustettu tyhjä: {file_path}")

# Käyttö
initializer = FileInitializer()
initializer.initialize_runtime_files()
