#!/usr/bin/env python3
#[file name]: create_install_config.py
#[file content begin]

"""
Vaalijärjestelmän konfiguraatiotiedostojen luontityökalu
Kysyy käyttäjältä tarvittavat tiedot ja luo asennustiedostot
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
import sys

def get_input(prompt, default=None, required=True):
    """Kysyy käyttäjältä syötettä"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    while True:
        value = input(prompt).strip()
        if not value and default:
            return default
        elif not value and required:
            print("❌ Tämä kenttä on pakollinen!")
        elif value:
            return value

def get_multilingual_input(field_name, languages=['fi', 'en', 'sv']):
    """Kysyy monikielistä tekstiä"""
    result = {}
    print(f"\n📝 Syötä {field_name} seuraavilla kielillä:")
    
    for lang in languages:
        lang_name = {
            'fi': 'suomeksi',
            'en': 'englanniksi', 
            'sv': 'ruotsiksi'
        }.get(lang, lang)
        
        result[lang] = get_input(f"  {lang_name}", required=True)
    
    return result

def get_date_input(prompt):
    """Kysyy päivämäärää varmistaen oikean muodon"""
    while True:
        date_str = get_input(prompt, required=True)
        try:
            # Tarkista että päivämäärä on oikeassa muodossa
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            print("❌ Virheellinen päivämäärämuoto! Käytä muotoa: YYYY-MM-DD")

def get_boolean_input(prompt, default=True):
    """Kysyy kyllä/ei -valintaa"""
    default_text = "Y" if default else "N"
    prompt = f"{prompt} (Y/N) [{default_text}]: "
    
    while True:
        value = input(prompt).strip().upper()
        if not value:
            return default
        elif value in ['Y', 'YES', 'K', 'KYLLÄ']:
            return True
        elif value in ['N', 'NO', 'E', 'EI']:
            return False
        else:
            print("❌ Syötä Y (kyllä) tai N (ei)")

def get_phases():
    """Kysyy vaalin vaiheet/päivät"""
    phases = []
    phase_count = int(get_input("Kuinka monta vaihetta/vaalipäivää vaalissa on", "1"))
    
    for i in range(phase_count):
        print(f"\n📅 Vaihe {i+1}:")
        phase = {
            "phase": i + 1,
            "date": get_date_input("  Vaalipäivä (YYYY-MM-DD)"),
            "description": get_multilingual_input("vaiheen kuvaus")
        }
        phases.append(phase)
    
    return phases

def create_election_config():
    """Luo vaalikonfiguraation käyttäjän syötteiden perusteella"""
    
    print("🎯 VAALIN PERUSTIEDOT")
    print("=" * 50)
    
    election_id = get_input("Vaalin yksilöllinen ID (esim. president_2024)")
    election_name = get_multilingual_input("vaalin nimi")
    election_description = get_multilingual_input("vaalin kuvaus")
    
    print("\n📊 VAALIN TYYPPI JA AJANKOHTA")
    election_type = get_input("Vaalityyppi", "presidential")
    phases = get_phases()
    
    print("\n⚙️  JÄRJESTELMÄASETUKSET")
    timelock_enabled = get_boolean_input("Käytetäänkö timelockia tuloksille", True)
    edit_deadline = get_date_input("Muokkausdeadline (YYYY-MM-DD)")
    grace_period = int(get_input("Grace period tunteina", "48"))
    community_managed = get_boolean_input("Yhteisöhallinnointi käytössä", True)
    
    print("\n🌍 VAIKUTUSALUE")
    districts_input = get_input("Vaalipiirit (pilkulla eroteltuna, 'koko_maa' koko maan vaaleissa)", "koko_maa")
    districts = [d.strip() for d in districts_input.split(',')]
    
    # Luo vaalikonfiguraatio
    election_config = {
        "election_id": election_id,
        "name": election_name,
        "description": election_description,
        "dates": phases,
        "type": election_type,
        "phases": len(phases),
        "timelock_enabled": timelock_enabled,
        "edit_deadline": edit_deadline,
        "grace_period_hours": grace_period,
        "community_managed": community_managed,
        "districts": districts,
        "candidate_count": None,  # Täytetään myöhemmin
        "status": "upcoming",
        "config_cid": f"QmConfig{uuid.uuid4().hex[:16]}",  # Mock-CID
        "created": datetime.now().isoformat()
    }
    
    return election_config

def create_install_config(election_config):
    """Luo install_config.base.json tiedoston"""
    
    install_config = {
        "election_data": {
            "id": election_config["election_id"],
            "ipfs_cid": election_config["config_cid"],
            "name": election_config["name"],
            "date": election_config["dates"][0]["date"],  # Ensimmäinen vaalipäivä
            "type": election_config["type"],
            "timelock_enabled": election_config["timelock_enabled"],
            "edit_deadline": election_config["edit_deadline"],
            "grace_period_hours": election_config["grace_period_hours"],
            "community_managed": election_config["community_managed"],
            "phases": election_config["phases"],
            "districts": election_config["districts"]
        },
        "community_governance": {
            "multisig_wallet": "{{MULTISIG_WALLET}}",
            "proposal_system": "{{PROPOSAL_SYSTEM_URL}}",
            "voting_contract": "{{VOTING_CONTRACT}}",
            "emergency_council": {
                "members": 5,
                "activation_threshold": 3
            }
        },
        "metadata": {
            "created": datetime.now().isoformat(),
            "version": "1.0.0",
            "generated_by": "create_install_config.py"
        }
    }
    
    return install_config

def create_meta_config(election_config):
    """Luo meta.base.json tiedoston"""
    
    meta_config = {
        "election": {
            "id": election_config["election_id"],
            "name": election_config["name"],
            "date": election_config["dates"][0]["date"],
            "type": election_config["type"],
            "timelock_enabled": election_config["timelock_enabled"],
            "edit_deadline": election_config["edit_deadline"],
            "grace_period_hours": election_config["grace_period_hours"],
            "governance_model": "community_driven"
        },
        "system_info": {
            "system_id": f"system_{election_config['election_id']}",
            "public_key": "{{SYSTEM_PUBLIC_KEY}}",
            "created": datetime.now().isoformat(),
            "governance_contract": "{{GOVERNANCE_CONTRACT_ADDRESS}}"
        },
        "community_governance": {
            "validators": [],
            "current_proposals": [],
            "voting_parameters": {
                "quorum": 15,
                "approval_threshold": 60
            }
        },
        "version": "1.0.0",
        "metadata": {
            "created": datetime.now().isoformat(),
            "config_source": "manual_creation"
        }
    }
    
    return meta_config

def create_elections_list(election_config):
    """Luo elections_list.json tiedoston"""
    
    elections_list = {
        "metadata": {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "ipfs_cid": f"QmElectionsList{uuid.uuid4().hex[:16]}",  # Mock-CID
            "description": {
                "fi": "Käsin luotu vaalilista",
                "en": "Manually created elections list", 
                "sv": "Manuellt skapad valista"
            }
        },
        "elections": [election_config],
        "election_types": {
            election_config["type"]: {
                "description": {
                    "fi": f"{election_config['name']['fi']} - tyyppi",
                    "en": f"{election_config['name']['en']} - type",
                    "sv": f"{election_config['name']['sv']} - typ"
                },
                "term_years": 4,  # Oletusarvo
                "max_terms": None
            }
        },
        "system_config": {
            "default_timelock_enabled": True,
            "default_grace_period_hours": 48,
            "default_community_managed": True,
            "supported_languages": ["fi", "en", "sv"],
            "version_control": True,
            "ipfs_backed": True
        }
    }
    
    return elections_list

def save_configs(election_config, output_dir="config_output"):
    """Tallentaa kaikki konfiguraatiotiedostot"""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 1. Luo install_config.base.json
    install_config = create_install_config(election_config)
    install_file = output_path / "install_config.base.json"
    with open(install_file, 'w', encoding='utf-8') as f:
        json.dump(install_config, f, indent=2, ensure_ascii=False)
    print(f"✅ Luotu: {install_file}")
    
    # 2. Luo meta.base.json
    meta_config = create_meta_config(election_config)
    meta_file = output_path / "meta.base.json"
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(meta_config, f, indent=2, ensure_ascii=False)
    print(f"✅ Luotu: {meta_file}")
    
    # 3. Luo elections_list.json
    elections_list = create_elections_list(election_config)
    elections_file = output_path / "elections_list.json"
    with open(elections_file, 'w', encoding='utf-8') as f:
        json.dump(elections_list, f, indent=2, ensure_ascii=False)
    print(f"✅ Luotu: {elections_file}")
    
    # 4. Luo yksinkertainen system_chain.base.json
    system_chain = {
        "chain_id": election_config["election_id"],
        "created_at": datetime.now().isoformat(),
        "description": f"Vaalijärjestelmä ketju: {election_config['name']['fi']}",
        "version": "1.0.0",
        "blocks": [
            {
                "block_id": 0,
                "timestamp": datetime.now().isoformat(),
                "description": "Konfiguraation luonti",
                "files": {
                    "install_config.base.json": "{{HASH}}",
                    "meta.base.json": "{{HASH}}",
                    "elections_list.json": "{{HASH}}"
                },
                "previous_hash": None,
                "block_hash": "{{CREATION_HASH}}"
            }
        ],
        "current_state": {
            "election_id": election_config["election_id"],
            "election_name": election_config["name"]["fi"],
            "config_created": datetime.now().isoformat()
        },
        "metadata": {
            "algorithm": "sha256",
            "system_id": f"system_{election_config['election_id']}",
            "config_source": "manual_creation"
        }
    }
    
    system_chain_file = output_path / "system_chain.base.json"
    with open(system_chain_file, 'w', encoding='utf-8') as f:
        json.dump(system_chain, f, indent=2, ensure_ascii=False)
    print(f"✅ Luotu: {system_chain_file}")
    
    return output_path

def show_usage_instructions(election_config, output_dir):
    """Näyttää käyttöohjeet luotujen tiedostojen käyttöön"""
    
    print("\n" + "="*60)
    print("🎉 KONFIGURAATIOT LUOTU ONNISTUNEESTI!")
    print("="*60)
    
    print(f"\n📁 Tiedostot tallennettu hakemistoon: {output_dir}")
    print(f"🏛️  Vaali: {election_config['name']['fi']}")
    print(f"🆔 Vaali-ID: {election_config['election_id']}")
    
    print(f"\n🚀 ASENNA JÄRJESTELMÄ:")
    print(f"python install.py --config-file={output_dir}/elections_list.json --election-id={election_config['election_id']} --first-install")
    
    print(f"\n💡 VAIHTOEHTOISET ASENNUSTAVAT:")
    print(f"# 1. Käytä suoraan install_configia:")
    print(f"python install.py --config-file={output_dir}/install_config.base.json --election-id={election_config['election_id']} --first-install")
    
    print(f"\n# 2. Asenna ilman first-install lippua (lisäkoneet):")
    print(f"python install.py --config-file={output_dir}/elections_list.json --election-id={election_config['election_id']}")
    
    print(f"\n# 3. Tarkista asennus:")
    print(f"python install.py --config-file={output_dir}/elections_list.json --election-id={election_config['election_id']} --verify")
    
    print(f"\n📋 LUODUT TIEDOSTOT:")
    for file in Path(output_dir).glob("*.json"):
        print(f"   📄 {file.name}")
    
    print(f"\n⚠️  HUOMIOITAVAA:")
    print("   - Korvaa {{MULTISIG_WALLET}} ja muut placeholderit oikeilla arvoilla")
    print("   - Tarkista erityisesti päivämäärät")
    print("   - Testaa aina asennus ennen tuotantokäyttöä")

def main():
    """Pääohjelma"""
    
    print("🎯 VAAILIJÄRJESTELMÄN KONFIGURAATION LUONTI")
    print("=" * 60)
    print("Tämä työkalu luo vaalijärjestelmälle tarvittavat konfiguraatiotiedostot")
    print("Vastaa seuraaviin kysymyksiin luodaksesi vaalin konfiguraation\n")
    
    try:
        # 1. Luo vaalikonfiguraatio
        election_config = create_election_config()
        
        # 2. Kysy tallennushakemisto
        output_dir = get_input("Tallennushakemisto", "config_output")
        
        # 3. Tallenna konfiguraatiot
        saved_path = save_configs(election_config, output_dir)
        
        # 4. Näytä käyttöohjeet
        show_usage_instructions(election_config, output_dir)
        
        print(f"\n✅ VALMIS! Järjestelmä on nyt valmis asennettavaksi.")
        
    except KeyboardInterrupt:
        print("\n\n❌ Konfiguraation luonti keskeytetty")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Virhe konfiguraation luonnissa: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#[file content end]
