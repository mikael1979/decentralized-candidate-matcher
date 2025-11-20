#!/bin/bash

echo "🏛️  Asennetaan Jumaltenvaalit 2026 -järjestelmää..."

# Tarkista ympäristö
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 tarvitaan"
    exit 1
fi

# Luo virtuaaliympäristö
echo "📦 Luodaan virtuaaliympäristö..."
python3 -m venv venv
source venv/bin/activate

# Asenna riippuvuudet
echo "📚 Asennetaan riippuvuudet..."
pip install -r requirements.txt

# Asenna Jumaltenvaalit config-järjestelmällä
echo "⚡ Asennetaan Jumaltenvaalit 2026 (config-järjestelmä)..."
python src/cli/install.py --first-install --election-id Jumaltenvaalit2026 --node-type coordinator

# Lisää esimerkkidataa (ILMAN --election parametria - config muistaa!)
echo "🎯 Lisätään esimerkkidataa..."
python src/cli/manage_questions.py --add --category "Hallinto" --question-fi "Pitäisikö Zeusin salamaniskuoikeuksia rajoittaa?" --question-en "Should Zeus's lightning bolt privileges be restricted?"
python src/cli/manage_questions.py --add --category "Turvallisuus" --question-fi "Tulisiko jumalilla olla enemmän valtaa maan asioihin?" --question-en "Should gods have more power in earthly affairs?"
python src/cli/manage_questions.py --add --category "Yleinen" --question-fi "Kannatanko täyttä demokratiaa jumalallisella ohjauksella?" --question-en "Do I support full democracy with divine guidance?"

python src/cli/manage_candidates.py --add --name-fi "Zeus" --name-en "Zeus" --party "Olympolaiset" --domain "sky_thunder"
python src/cli/manage_candidates.py --add --name-fi "Athena" --name-en "Athena" --party "Olympolaiset" --domain "wisdom_warfare"
python src/cli/manage_candidates.py --add --name-fi "Hades" --name-en "Hades" --party "Olympolaiset" --domain "underworld"

# Lisää vastauksia
echo "📝 Lisätään vastauksia..."
# Zeusin vastaukset
python src/cli/manage_answers.py add --candidate-id $(python -c "from src.core.config_manager import CandidateManager; m = CandidateManager('Jumaltenvaalit2026'); print([c['id'] for c in m.list_candidates() if c['basic_info']['name']['fi'] == 'Zeus'][0])") --question-id q_1 --answer 5 --confidence 5 --explanation-fi "Jumalana pidän täyttä valtaa"
python src/cli/manage_answers.py add --candidate-id $(python -c "from src.core.config_manager import CandidateManager; m = CandidateManager('Jumaltenvaalit2026'); print([c['id'] for c in m.list_candidates() if c['basic_info']['name']['fi'] == 'Zeus'][0])") --question-id q_2 --answer 4 --confidence 5 --explanation-fi "Valtaa tarvitaan järjestyksen ylläpitoon"

# Athenan vastaukset
python src/cli/manage_answers.py add --candidate-id $(python -c "from src.core.config_manager import CandidateManager; m = CandidateManager('Jumaltenvaalit2026'); print([c['id'] for c in m.list_candidates() if c['basic_info']['name']['fi'] == 'Athena'][0])") --question-id q_1 --answer 3 --confidence 4 --explanation-fi "Viisaus ja valta tasapainoon"
python src/cli/manage_answers.py add --candidate-id $(python -c "from src.core.config_manager import CandidateManager; m = CandidateManager('Jumaltenvaalit2026'); print([c['id'] for c in m.list_candidates() if c['basic_info']['name']['fi'] == 'Athena'][0])") --question-id q_2 --answer 2 --confidence 4 --explanation-fi "Demokratia viisauden kanssa"

# Generoi analytics-raportti
echo "📊 Generoidaan analytics-raportti..."
python src/cli/analytics.py wrapper

echo ""
echo "✅ Jumaltenvaalit 2026 asennettu!"
echo ""
echo "🎯 JÄRJESTELMÄ VALMIS! CONFIG-JÄRJESTELMÄ MUISTAA VAAIN - EI TARVITSE --election PARAMETRIA!"
echo ""
echo "📋 KÄYTTÖKOMENNOT:"
echo "   source venv/bin/activate"
echo "   python src/cli/manage_questions.py --list                    # Listaa kysymykset"
echo "   python src/cli/manage_candidates.py --list                   # Listaa ehdokkaat"
echo "   python src/cli/manage_answers.py list                        # Listaa vastaukset"
echo "   python src/cli/voting_engine.py --start                      # Käynnistä vaalikone"
echo "   python src/cli/analytics.py wrapper                          # Analytics-raportti"
echo ""
echo "🆕 UUDET TOIMINNOT:"
echo "   python src/cli/manage_questions.py --remove 'q_1'            # Poista kysymys"
echo "   python src/cli/manage_candidates.py --update 'Zeus' --name-fi 'Zeus Olympios'  # Päivitä"
echo "   python src/cli/manage_answers.py remove --candidate-id cand_xxx --question-id q_1"
echo ""
echo "🌐 IPFS-CONFIG:"
echo "   Config julkaistu IPFS:ään - worker-nodet voivat bootstrappaa"
echo ""
echo "🏛️  May the gods be with you! 🚀"
