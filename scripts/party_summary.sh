#!/bin/bash

echo "🏛️  JUMALTENVAALIT 2026 - PUOLUERAportTI"
echo "========================================"

# Varmista että olet virtuaaliympäristössä
if [ ! -d "venv" ]; then
    echo "❌ Aktivoi virtuaaliympäristö: source venv/bin/activate"
    exit 1
fi

echo ""
echo "📈 PÄÄTILASTOT:"
python src/cli/manage_parties.py stats --election Jumaltenvaalit2026

echo ""
echo "✅ VAHVISTETUT PUOLUEET:"
python src/cli/manage_parties.py list --election Jumaltenvaalit2026

echo ""
echo "🔍 YKSITYISKOHDAT:"

# Käy läpi kaikki vahvistetut puolueet
python -c "
import json
import os

parties_file = 'data/runtime/parties.json'
candidates_file = 'data/runtime/candidates.json'

if os.path.exists(parties_file):
    with open(parties_file, 'r', encoding='utf-8') as f:
        parties_data = json.load(f)
    
    # Lataa ehdokkaat
    candidates_data = {}
    if os.path.exists(candidates_file):
        with open(candidates_file, 'r', encoding='utf-8') as f:
            candidates_data = json.load(f)
    
    verified_parties = [p for p in parties_data['parties'] if p['registration']['verification_status'] == 'verified']
    
    print('🎉 VAHVISTETUT PUOLUEET JA EHDOKKAAT:')
    print('=' * 50)
    
    for party in verified_parties:
        print(f'\\n🏛️  {party[\"name\"][\"fi\"]} ({party[\"party_id\"]})')
        print(f'   📧 {party[\"metadata\"].get(\"contact_email\", \"Ei sähköpostia\")}')
        print(f'   👑 Ehdokkaita: {len(party[\"candidates\"])}')
        
        # Näytä ehdokkaat
        if candidates_data and 'candidates' in candidates_data:
            party_candidates = [c for c in candidates_data['candidates'] if c['candidate_id'] in party['candidates']]
            for cand in party_candidates:
                print(f'     • {cand[\"basic_info\"][\"name\"][\"fi\"]} ({cand[\"candidate_id\"]})')
        
        print(f'   ✅ Vahvistajat: {\", \".join(party[\"registration\"][\"verified_by\"])}')
        print(f'   🕒 Vahvistettu: {party[\"registration\"][\"verification_timestamp\"][:16]}')
    
    # Näytä odottavat puolueet
    pending_parties = [p for p in parties_data['parties'] if p['registration']['verification_status'] == 'pending']
    if pending_parties:
        print(f'\\n⏳ ODOTTAA VAHVISTUSTA ({len(pending_parties)}):')
        for party in pending_parties:
            verified_count = len(party['registration']['verified_by'])
            needed = parties_data['quorum_config']['min_nodes_for_verification']
            print(f'   • {party[\"name\"][\"fi\"]}: {verified_count}/{needed} vahvistusta')
    
    # Näytä hylätyt puolueet
    rejected_parties = [p for p in parties_data['parties'] if p['registration']['verification_status'] == 'rejected']
    if rejected_parties:
        print(f'\\n❌ HYLÄTYT PUOLUEET ({len(rejected_parties)}):')
        for party in rejected_parties:
            print(f'   • {party[\"name\"][\"fi\"]}: {party[\"registration\"][\"rejection_reason\"]}')
else:
    print('❌ Puoluerekisteriä ei löydy')
"

echo ""
echo "🎯 SEURAAVAT VAIHEET:"
echo "   • Lisää ehdokkaita puolueisiin"
echo "   • Ehdokkaat vastaavat kysymyksiin" 
echo "   • Käynnistä vaalikone"
echo ""
echo "🏛️  Jumaltenvaalit 2026 on valmis puolueiden rekisteröintiin!"
