# 🎯 Master/Worker Asennusopas

## Master-Node Asennus
```bash
# 1. Luo konfiguraatio
python create_install_config.py --election-id president_2024 --name "Presidentinvaalit 2024"

# 2. Asenna master
python master-install.py --election-id president_2024 --config install_config.json

# 3. Tarkista
python master-install.py --verify --election-id president_2024
