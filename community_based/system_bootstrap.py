#!/usr/bin/env python3
# system_bootstrap.py
"""
Järjestelmän käynnistysmoduuli - PÄIVITETTY NIMIAVARUUDEN KANSSA
Suoritetaan jokaisen ohjelman alussa
Käyttö: Lisää jokaisen ohjelman alkuun:
  from system_bootstrap import verify_system_startup
  verify_system_startup()
"""

import sys
import os
import json
from pathlib import Path

def verify_system_startup():
    """Suorita järjestelmän käynnistyksen tarkistukset - PÄIVITETTY NIMIAVARUUDEN KANSSA"""
    
    # Estä rekursio jos bootstrap itse suoritetaan
    if "SYSTEM_BOOTSTRAP_RUNNING" in os.environ:
        return True
    os.environ["SYSTEM_BOOTSTRAP_RUNNING"] = "true"
    
    try:
        print("🔍 Järjestelmän käynnistystarkistukset - PÄIVITETTY")
        print("=" * 50)
        
        # 1. Tarkista runtime-hakemisto
        runtime_dir = Path("runtime")
        if not runtime_dir.exists():
            print("❌ Runtime-hakemisto puuttuu - suorita ensin alustus")
            print("💡 Käytä: python initialization.py")
            return False
        
        # 2. Tarkista perustiedostot
        required_files = [
            "runtime/meta.json",
            "runtime/system_metadata.json", 
            "runtime/system_chain.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Puuttuvat perustiedostot:")
            for file in missing_files:
                print(f"   - {file}")
            print("💡 Suorita: python install.py --verify")
            return False
        
        # 3. Tarkista nimiavaruuden eheys
        namespace_check = _verify_namespace_integrity()
        if not namespace_check["success"]:
            print("❌ Nimiavaruuden eheysongelmia:")
            for issue in namespace_check.get("issues", []):
                print(f"   - {issue}")
        
        # 4. Tarkista fingerprintit tuotantotilassa
        lock_file = Path("runtime/production.lock")
        if lock_file.exists():
            print("🔒 Tuotantotila - tarkistetaan fingerprintit...")
            
            try:
                from production_lock_manager import ProductionLockManager
                lock_manager = ProductionLockManager()
                
                if not lock_manager.verify_on_startup():
                    print("❌ JÄRJESTELMÄN EHYS VAARANTUNUT!")
                    print("🚫 Ohjelma pysäytetty turvallisuussyistä")
                    return False
                
                print("✅ Järjestelmän eheys varmistettu")
                
            except ImportError as e:
                print(f"⚠️  Tuotantotilan tarkistus ei saatavilla: {e}")
                print("💡 Jatketaan ilman fingerprint-tarkistusta")
            except Exception as e:
                print(f"⚠️  Fingerprint-tarkistus epäonnistui: {e}")
                print("💡 Jatketaan varotoimintana")
        
        else:
            print("🔓 Kehitystila - fingerprint-tarkistus ohitettu")
        
        # 5. Tarkista IPFS-yhteys ja ajanvaraus
        ipfs_check = _verify_ipfs_environment()
        if not ipfs_check["ipfs_available"]:
            print("⚠️  IPFS ei saatavilla - käytetään mock-tilaa")
        
        # 6. Tarkista vaalin tila
        election_check = _verify_election_status()
        if not election_check["valid"]:
            print(f"⚠️  Vaalitarkistus: {election_check.get('message', 'Tuntematon virhe')}")
        
        # 7. Tarkista palautusjärjestelmä
        recovery_check = _verify_recovery_system()
        if not recovery_check["initialized"]:
            print(f"⚠️  Palautusjärjestelmä: {recovery_check.get('message', 'Ei alustettu')}")
        
        print("✅ Käynnistystarkistukset läpäisty")
        return True
        
    except Exception as e:
        print(f"❌ Käynnistystarkistukset epäonnistuivat: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Puhdista environment variable
        if "SYSTEM_BOOTSTRAP_RUNNING" in os.environ:
            del os.environ["SYSTEM_BOOTSTRAP_RUNNING"]

def _verify_namespace_integrity() -> Dict:
    """Tarkista nimiavaruuden eheys - UUSI"""
    try:
        issues = []
        
        # Tarkista system_metadata
        with open('runtime/system_metadata.json', 'r', encoding='utf-8') as f:
            system_meta = json.load(f)
        
        system_namespace = system_meta.get('election_specific', {}).get('namespace')
        system_election_id = system_meta.get('election_specific', {}).get('election_id')
        
        if not system_namespace:
            issues.append("System_metadasta puuttuu nimiavaruus")
        
        # Tarkista meta.json
        with open('runtime/meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta_election_id = meta.get('election', {}).get('id')
        
        # Tarkista että vaali-ID:t täsmäävät
        if system_election_id != meta_election_id:
            issues.append(f"Vaali-ID sopimattomuus: system={system_election_id}, meta={meta_election_id}")
        
        # Tarkista election_registry (jos on master)
        registry_file = Path("runtime/election_registry.json")
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            registry_namespace = registry.get('election_registry', {}).get('namespace')
            registry_election_id = registry.get('election_registry', {}).get('election_id')
            
            if registry_namespace != system_namespace:
                issues.append(f"Nimiavaruussopimattomuus: system={system_namespace}, registry={registry_namespace}")
            
            if registry_election_id != system_election_id:
                issues.append(f"Vaali-ID sopimattomuus registryssä: {registry_election_id} != {system_election_id}")
        
        # Tarkista että nimiavaruus alkaa oikein
        if system_namespace and not system_namespace.startswith(f"election_{system_election_id}"):
            issues.append(f"Nimiavaruus ei vastaa vaalia: {system_namespace}")
        
        # Tarkista metadata_managerin näkymä
        try:
            from metadata_manager import get_metadata_manager
            manager = get_metadata_manager()
            namespace_info = manager.get_namespace_info()
            
            if namespace_info["namespace"] != system_namespace:
                issues.append(f"Metadata_manager nimiavaruus: {namespace_info['namespace']} != {system_namespace}")
            
            if namespace_info["election_id"] != system_election_id:
                issues.append(f"Metadata_manager vaali-ID: {namespace_info['election_id']} != {system_election_id}")
                
        except ImportError:
            issues.append("Metadata_manager ei saatavilla nimiavaruustarkistukseen")
        
        success = len(issues) == 0
        if success:
            print(f"✅ Nimiavaruus vahvistettu: {system_namespace}")
            print(f"   Vaali: {system_election_id}")
        
        return {
            "success": success,
            "namespace": system_namespace,
            "election_id": system_election_id,
            "issues": issues
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "issues": [f"Nimiavaruuden tarkistus epäonnistui: {e}"]
        }

def _verify_ipfs_environment() -> Dict:
    """Tarkista IPFS-ympäristö - PÄIVITETTY"""
    try:
        from ipfs_schedule_manager import IPFSScheduleManager
        
        # Tarkista ajanvarauskonfiguraatio
        schedule_config = Path("ipfs_schedule_config.json")
        if not schedule_config.exists():
            return {
                "ipfs_available": False,
                "schedule_available": False,
                "message": "IPFS-ajanvarauskonfiguraatiota ei löydy"
            }
        
        # Yritä alustaa ajanvarausmanageri
        try:
            schedule_manager = IPFSScheduleManager()
            schedule_status = schedule_manager.get_schedule_status()
            
            return {
                "ipfs_available": True,
                "schedule_available": True,
                "schedule_status": schedule_status,
                "message": "IPFS ja ajanvaraus käytettävissä"
            }
            
        except Exception as e:
            return {
                "ipfs_available": False,
                "schedule_available": False,
                "message": f"IPFS-ajanvaraus epäonnistui: {e}"
            }
            
    except ImportError:
        return {
            "ipfs_available": False,
            "schedule_available": False,
            "message": "IPFS-ajanvarausmoduulia ei saatavilla"
        }

def _verify_election_status() -> Dict:
    """Tarkista vaalin tila - PÄIVITETTY"""
    try:
        with open('runtime/meta.json', 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        
        with open('runtime/system_metadata.json', 'r', encoding='utf-8') as f:
            system_metadata = json.load(f)
        
        election_id = meta_data['election']['id']
        election_name = meta_data['election']['name']['fi']
        node_type = system_metadata.get('election_specific', {}).get('node_type', 'unknown')
        namespace = system_metadata.get('election_specific', {}).get('namespace', 'unknown')
        
        print(f"🏛️  Aktiivinen vaali: {election_name}")
        print(f"   ID: {election_id}")
        print(f"   Nimiavaruus: {namespace}")
        print(f"   Node-tyyppi: {node_type}")
        
        # Tarkista election_registry (jos on master)
        registry_file = Path("runtime/election_registry.json")
        worker_count = 0
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            worker_nodes = registry.get('election_registry', {}).get('worker_nodes', [])
            worker_count = len(worker_nodes)
            print(f"   Työasemia: {worker_count}")
        
        return {
            "valid": True,
            "election_id": election_id,
            "election_name": election_name,
            "node_type": node_type,
            "namespace": namespace,
            "worker_count": worker_count
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "message": f"Vaalin tarkistus epäonnistui: {e}"
        }

def _verify_recovery_system() -> Dict:
    """Tarkista palautusjärjestelmä - PÄIVITETTY"""
    try:
        from enhanced_recovery_manager import get_enhanced_recovery_manager
        
        # Hae recovery manageri
        recovery_manager = get_enhanced_recovery_manager()
        status = recovery_manager.get_recovery_status()
        
        if status["recovery_system_initialized"]:
            print(f"✅ Palautusjärjestelmä: {status['total_backup_entries']} varmuuskopiota")
            print(f"   Käyttö: {status['usage_percentage']:.1f}%")
            print(f"   Ajanvaraus: {'✅ Käytössä' if status['schedule_enabled'] else '❌ Ei käytössä'}")
            
            return {
                "initialized": True,
                "backup_count": status["total_backup_entries"],
                "usage_percentage": status["usage_percentage"],
                "schedule_enabled": status["schedule_enabled"],
                "namespace": status["namespace"]
            }
        else:
            return {
                "initialized": False,
                "message": "Palautusjärjestelmä ei alustettu"
            }
            
    except ImportError as e:
        return {
            "initialized": False,
            "message": f"Palautusjärjestelmän moduulia ei saatavilla: {e}"
        }
    except Exception as e:
        return {
            "initialized": False,
            "message": f"Palautusjärjestelmän tarkistus epäonnistui: {e}"
        }

def bootstrap_system():
    """Vanhempi nimi yhteensopivuuden vuoksi"""
    return verify_system_startup()

# Automaattinen suoritus kun moduuli importataan
# HUOM: Kommentoitu pois että ohjelmat voivat kontrolloida itse
# if __name__ != "__main__":
#     verify_system_startup()

def print_system_status():
    """Tulosta järjestelmän nykyinen tila - PÄIVITETTY"""
    
    print("\n📊 JÄRJESTELMÄN TILA - PÄIVITETTY:")
    print("=" * 50)
    
    # Tarkista tuotantotila
    lock_file = Path("runtime/production.lock")
    if lock_file.exists():
        try:
            with open(lock_file, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            print(f"🔒 TUOTANTOTILA (lukittu: {lock_data.get('locked_at', 'unknown')})")
            print(f"   Fingerprint CID: {lock_data.get('fingerprint_entry', 'local')}")
            print(f"   Moduuleja: {lock_data.get('total_modules', 'unknown')}")
            print(f"   Vaali: {lock_data.get('election_id', 'unknown')}")
        except:
            print("🔒 TUOTANTOTILA (lukittu)")
    else:
        print("🔓 KEHITYSTILA")
    
    # Tarkista vaali ja nimiavaruus
    try:
        with open('runtime/meta.json', 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        with open('runtime/system_metadata.json', 'r', encoding='utf-8') as f:
            system_metadata = json.load(f)
        
        election_id = meta_data['election']['id']
        election_name = meta_data['election']['name']['fi']
        namespace = system_metadata.get('election_specific', {}).get('namespace', 'unknown')
        node_type = system_metadata.get('election_specific', {}).get('node_type', 'unknown')
        
        print(f"🏛️  VAAli: {election_name}")
        print(f"   ID: {election_id}")
        print(f"   Nimiavaruus: {namespace}")
        print(f"   Node-tyyppi: {node_type}")
    except:
        print("🏛️  VAAli: Tuntematon")
    
    # Tarkista IPFS
    ipfs_status = _verify_ipfs_environment()
    ipfs_display = "🌐 OIKEA IPFS" if ipfs_status["ipfs_available"] else "🔄 MOCK IPFS"
    schedule_display = "✅ AJANVARAUS" if ipfs_status.get("schedule_available") else "❌ EI AJANVARAUSTA"
    
    print(f"{ipfs_display} {schedule_display}")
    
    # Tarkista palautusjärjestelmä
    recovery_status = _verify_recovery_system()
    if recovery_status["initialized"]:
        print(f"💾 PALAUTUSJÄRJESTELMÄ: {recovery_status['backup_count']} kopiota ({recovery_status['usage_percentage']:.1f}%)")
    else:
        print("💾 PALAUTUSJÄRJESTELMÄ: Ei alustettu")
    
    # Tarkista nimiavaruuden eheys
    namespace_check = _verify_namespace_integrity()
    namespace_display = "✅ EHJÄ" if namespace_check["success"] else "❌ ONGELMIA"
    print(f"🔗 NIMIAVARUUS: {namespace_display}")
    
    if not namespace_check["success"] and namespace_check.get("issues"):
        print("   Ongelmat:")
        for issue in namespace_check["issues"]:
            print(f"   - {issue}")
    
    print("=" * 50)

def check_system_health() -> Dict:
    """Tarkista järjestelmän terveys - UUSI"""
    health_checks = {
        "namespace_integrity": _verify_namespace_integrity(),
        "ipfs_environment": _verify_ipfs_environment(),
        "election_status": _verify_election_status(),
        "recovery_system": _verify_recovery_system(),
        "production_lock": _check_production_lock()
    }
    
    # Laska kokonaisterveys
    all_healthy = all([
        health_checks["namespace_integrity"]["success"],
        health_checks["election_status"]["valid"],
        health_checks["production_lock"]["valid"]
    ])
    
    health_checks["overall_health"] = "healthy" if all_healthy else "degraded"
    
    return health_checks

def _check_production_lock() -> Dict:
    """Tarkista tuotantolukon tila"""
    lock_file = Path("runtime/production.lock")
    
    if not lock_file.exists():
        return {
            "locked": False,
            "valid": True,
            "message": "Kehitystila - ei lukkoa"
        }
    
    try:
        with open(lock_file, 'r', encoding='utf-8') as f:
            lock_data = json.load(f)
        
        # Tarkista että lukko on voimassa
        locked_at = lock_data.get('locked_at')
        election_id = lock_data.get('election_id')
        
        return {
            "locked": True,
            "valid": True,
            "locked_at": locked_at,
            "election_id": election_id,
            "message": "Tuotantotila aktiivinen"
        }
        
    except Exception as e:
        return {
            "locked": True,
            "valid": False,
            "error": str(e),
            "message": "Virhe lukkotiedostossa"
        }

# Komentorivikäyttö
if __name__ == "__main__":
    # Komentoriviparametrit
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            print_system_status()
            sys.exit(0)
        elif command == "health":
            health = check_system_health()
            print(json.dumps(health, indent=2, ensure_ascii=False))
            sys.exit(0)
        elif command == "verify":
            success = verify_system_startup()
            sys.exit(0 if success else 1)
        else:
            print(f"Tuntematon komento: {command}")
            print("Käytettävissä olevat komennot: status, health, verify")
            sys.exit(1)
    
    # Oletus: suorita tarkistus ja näytä tila
    print("🚀 JÄRJESTELMÄN KÄYNNISTYSTARKISTUS - PÄIVITETTY")
    print("=" * 60)
    
    success = verify_system_startup()
    
    if success:
        print_system_status()
        print("\n🎯 Järjestelmä on valmis käyttöön!")
        
        # Näytä terveystila
        health = check_system_health()
        if health["overall_health"] == "healthy":
            print("💚 Järjestelmä on terve")
        else:
            print("🟡 Järjestelmässä on lieviä ongelmia")
            
    else:
        print("\n❌ Järjestelmän tarkistus epäonnistui!")
        
        # Näytä yksityiskohtaiset terveystiedot
        health = check_system_health()
        print("\n🔍 TARKEMMAT TIEDOT:")
        for check_name, check_result in health.items():
            if check_name != "overall_health":
                status = "✅" if check_result.get("success", check_result.get("valid", False)) else "❌"
                print(f"   {status} {check_name}: {check_result.get('message', 'Tuntematon tila')}")
        
        sys.exit(1)
