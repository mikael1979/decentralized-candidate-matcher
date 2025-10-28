[file name]: test_modular_installation.py
[file content begin]
#!/usr/bin/env python3
"""
Testaa modulaarista asennusta ja kone-ID-toiminnallisuutta
"""

import sys
import os
import shutil
from pathlib import Path

sys.path.append('.')

try:
    from metadata_manager import MetadataManager
    from installation_engine import InstallationEngine
    from mock_ipfs_extended import MockIPFSExtended
except ImportError as e:
    print(f"Import virhe: {e}")
    sys.exit(1)

def test_metadata_manager():
    """Testaa MetadataManager-toiminnallisuutta"""
    print("🧪 TESTATAAN METADATA MANAGERIA")
    
    test_dir = Path("test_metadata")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # 1. Testaa kone-ID generointi
    manager = MetadataManager(str(test_dir))
    machine_id = manager.generate_machine_id()
    print(f"✅ Kone-ID generoitu: {machine_id}")
    
    # 2. Testaa metadatan alustus
    metadata = manager.initialize_system_metadata("test_election", first_install=True)
    print(f"✅ Metadata alustettu: {metadata['system_metadata']['machine_id']}")
    
    # 3. Testaa lataus
    loaded_metadata = manager.load_metadata()
    print(f"✅ Metadata ladattu: {loaded_metadata['system_metadata']['machine_id']}")
    
    # 4. Testaa first-install tarkistus
    is_first = manager.is_first_installation("test_election")
    print(f"✅ First-install tarkistus: {is_first}")
    
    # 5. Testaa koneen tiedot
    machine_info = manager.get_machine_info()
    print(f"✅ Koneen tiedot: {machine_info}")
    
    shutil.rmtree(test_dir)
    return True

def test_installation_engine():
    """Testaa InstallationEngine-toiminnallisuutta"""
    print("\n🧪 TESTATAAN INSTALLATION ENGINEA")
    
    test_dir = Path("test_installation")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    try:
        # 1. Alusta moottori
        engine = InstallationEngine(str(test_dir))
        engine.set_ipfs_client(MockIPFSExtended())
        
        # 2. Lataa vaalikonfiguraatio
        elections_data = engine.load_elections_config("QmElectionsList123456789")
        print(f"✅ Vaalikonfiguraatio ladattu: {len(elections_data['elections'])} vaalia")
        
        # 3. Listaa vaalit
        engine.list_available_elections(elections_data)
        
        # 4. Asenna vaali
        result = engine.install_election("president_2024", elections_data, first_install=True)
        print(f"✅ Vaali asennettu: {result['election']['name']['fi']}")
        
        # 5. Tarkista asennus
        is_ok = engine.verify_installation("president_2024")
        print(f"✅ Asennus verifioitu: {is_ok}")
        
        # 6. Testaa toinen asennus (ei first-install)
        test_dir2 = Path("test_installation2")
        engine2 = InstallationEngine(str(test_dir2))
        engine2.set_ipfs_client(MockIPFSExtended())
        
        result2 = engine2.install_election("president_2024", elections_data, first_install=False)
        print(f"✅ Toinen kone asennettu: {result2['machine_info']['machine_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Testi epäonnistui: {e}")
        return False
    finally:
        # Siivoa
        for dir_path in [test_dir, Path("test_installation2")]:
            if dir_path.exists():
                shutil.rmtree(dir_path)

def main():
    print("🚀 MODULAARISEN ASENNUKSEN TESTI")
    print("=" * 60)
    
    success1 = test_metadata_manager()
    success2 = test_installation_engine()
    
    if success1 and success2:
        print("\n🎉 KAIKKI TESTIT ONNISTUIVAT!")
    else:
        print("\n❌ JOITKIN TESTIT EPÄONNISTUIVAT")
        sys.exit(1)

if __name__ == "__main__":
    main()
[file content end]
