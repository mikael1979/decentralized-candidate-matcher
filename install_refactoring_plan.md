# 📋 INSTALL.PY REFAKTOROINTISUUNNITELMA

## 📊 NYKYTILA
- Tiedosto: `src/cli/install.py`
- Koko: 336 riviä
- Luokkia: 0
- Funktioita: 8
- Click-komentoja: 6 (1 pääkomento)

## 🎯 TAVOITE
- Päämoduulin koko: ~50 riviä (85% vähennys)
- Modulaarinen rakenne: 5-7 erikoistunutta moduulia
- Backward compatibility: Täysin yhteensopiva

## 🏗️ SUUNNITELTU RAKENNE

### 1. src/cli/install/utils/
- `ipfs_utils.py` - IPFS-toiminnot (get_static_marker_cid, check_system_installed, load_elections_list)
- `node_utils.py` - Node-initialization (initialize_node)
- `election_utils.py` - Vaalitiedot (show_elections_hierarchy, validate_election_id)
- `file_utils.py` - Tiedostotoiminnot (initialize_basic_data_files)

### 2. src/cli/install/commands/
- `install_command.py` - Pääasennuskomento (install_system)

### 3. src/cli/install/__init__.py
- Import-koordinaattori

### 4. src/cli/install/__main__.py
- CLI-pääkoordinaattori (~50 riviä)

## 🔄 REFAKTOROINTIPROSESSI

### Vaihe 1: Luo hakemistorakenne
mkdir -p src/cli/install/{utils,commands}

### Vaihe 2: Siirrä apufunktiot utils/-hakemistoon
# a) ipfs_utils.py (IPFS-toiminnot)
# b) node_utils.py (Node-initialization)
# c) election_utils.py (Vaalitiedot)
# d) file_utils.py (Tiedostotoiminnot)

### Vaihe 3: Siirrä pääkomento commands/-hakemistoon
# install_command.py

### Vaihe 4: Luo __init__.py ja __main__.py

### Vaihe 5: Testaa integraatio

### Vaihe 6: Päivitä dokumentaatio

## 📈 ARVIO
- **Aikavaatimus**: 2-3 tuntia
- **Vaikeusaste**: Helppo (ei luokkia, vain funktioita)
- **Riskit**: Hyvin pieni
- **Hyödyt**: 85% vähennys päämoduulissa

## ✅ TOIMINNOT JA NIIDEN SIIRTO
1. get_static_marker_cid() → ipfs_utils.py
2. check_system_installed() → ipfs_utils.py  
3. load_elections_list() → ipfs_utils.py
4. initialize_node() → node_utils.py
5. show_elections_hierarchy() → election_utils.py
6. validate_election_id() → election_utils.py
7. initialize_basic_data_files() → file_utils.py
8. install_system() → commands/install_command.py

