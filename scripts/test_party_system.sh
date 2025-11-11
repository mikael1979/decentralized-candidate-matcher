#!/bin/bash

echo "🏛️  TESTATAAN PUOLUEJÄRJESTELMÄÄ"
echo "================================"

# Varmista että olet virtuaaliympäristössä
if [ ! -d "venv" ]; then
    echo "❌ Aktivoi virtuaaliympäristö: source venv/bin/activate"
    exit 1
fi

# 1. Ehdotta Olympolaisten puoluetta
echo ""
echo "🎯 1. Ehdotetaan Olympolaisten puoluetta..."
python src/cli/manage_parties.py propose --election Jumaltenvaalit2026 \
  --name-fi "Olympolaiset" \
  --name-en "Olympians" \
  --name-sv "Olympierna" \
  --description-fi "Perinteiset kreikkalaiset jumalat Olympos-vuorella" \
  --email "zeus@olympos.gr" \
  --website "https://olympos.gr"

# 2. Ehdotta meren jumalien puoluetta
echo ""
echo "🎯 2. Ehdotetaan Meren Jumalien puoluetta..."
python src/cli/manage_parties.py propose --election Jumaltenvaalit2026 \
  --name-fi "Meren Jumalat" \
  --name-en "Sea Gods" \
  --description-fi "Merten ja vesien jumalat" \
  --email "poseidon@seagods.gr"

# 3. Listaa puolueet
echo ""
echo "📋 3. Listataan puolueet..."
python src/cli/manage_parties.py list --election Jumaltenvaalit2026

# 4. Vahvista Olympolaiset (tarvitaan 3/3 vahvistusta)
echo ""
echo "✅ 4. Vahvistetaan Olympolaiset (1/3)..."
python src/cli/manage_parties.py verify --election Jumaltenvaalit2026 --party-id party_001 --verify --reason "Perinteinen puolue"

echo ""
echo "✅ 5. Vahvistetaan Olympolaiset (2/3)..."
python src/cli/manage_parties.py verify --election Jumaltenvaalit2026 --party-id party_001 --verify --reason "Laaja kannatus"

echo ""
echo "✅ 6. Vahvistetaan Olympolaiset (3/3 - KVOOORUMI!)..."
python src/cli/manage_parties.py verify --election Jumaltenvaalit2026 --party-id party_001 --verify --reason "Täysi kvoorumi saavutettu"

# 5. Hylkää Meren Jumalat
echo ""
echo "❌ 7. Hylätään Meren Jumalat..."
python src/cli/manage_parties.py verify --election Jumaltenvaalit2026 --party-id party_002 --reject --reason "Liian kapea kannatus"

# 6. Lopullinen lista
echo ""
echo "🏁 LOPPUTILA:"
python src/cli/manage_parties.py list --election Jumaltenvaalit2026

echo ""
echo "📊 PUOLUESTATISTIIKAT:"
python -c "
import json
import os

parties_file = 'data/runtime/parties.json'
if os.path.exists(parties_file):
    with open(parties_file, 'r') as f:
        data = json.load(f)
    
    total = len(data['parties'])
    verified = len([p for p in data['parties'] if p['registration']['verification_status'] == 'verified'])
    pending = len([p for p in data['parties'] if p['registration']['verification_status'] == 'pending'])
    rejected = len([p for p in data['parties'] if p['registration']['verification_status'] == 'rejected'])
    
    print(f'Puolueita yhteensä: {total}')
    print(f'Vahvistettuja: {verified}')
    print(f'Odottaa vahvistusta: {pending}') 
    print(f'Hylättyjä: {rejected}')
    
    # Näytä vahvistushistoria
    print()
    print('📜 VIIMEISIMmÄT TAPAHTUMAT:')
    for event in data['verification_history'][-5:]:
        print(f'  {event[\"timestamp\"][11:19]} - {event[\"party_id\"]}: {event[\"action\"]}')
else:
    print('Puoluerekisteriä ei löydy')
"
