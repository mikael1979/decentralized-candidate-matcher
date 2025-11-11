#!/bin/bash

echo "🧪 TESTATAAN ELO-LUOKITUSJÄRJESTELMÄÄ"
echo "======================================"

# Varmista että olet virtuaaliympäristössä
if [ ! -d "venv" ]; then
    echo "❌ Aktivoi virtuaaliympäristö: source venv/bin/activate"
    exit 1
fi

# Alusta testi
echo "📊 Alustetaan testi..."
python src/cli/elo_admin.py stats --election Jumaltenvaalit2026

echo ""
echo "🎲 Suoritetaan 10 satunnaista vertailua..."
echo "   (Käytetään automaattisia valintoja)"

# Tee 10 vertailua automaattisesti testataksemme järjestelmää
for i in {1..10}; do
    echo ""
    echo "--- Vertailu $i/10 ---"
    
    # Valitse satunnainen vastaus (a/b/t)
    choices=("a" "b" "t")
    random_choice=${choices[$RANDOM % ${#choices[@]}]}
    
    # Tallenna nykyinen tila ennen vertailua
    python -c "
import json
with open('data/runtime/questions.json', 'r') as f:
    data = json.load(f)
ratings = [q['elo_rating']['current_rating'] for q in data['questions']]
print(f'Tilanne ennen: {ratings}')
    " > /dev/null 2>&1
    
    # Suorita vertailu AUTOMAATTISELLA valinnalla
    python src/cli/compare_questions.py --election Jumaltenvaalit2026 --choice "$random_choice"
    
    # Näytä muutokset
    python -c "
import json
with open('data/runtime/questions.json', 'r') as f:
    data = json.load(f)
ratings = [q['elo_rating']['current_rating'] for q in data['questions']]
deltas = [q['elo_rating'].get('comparison_delta', 0) for q in data['questions']]
print(f'Tilanne jälkeen: {ratings}')
print(f'Muutokset: {deltas}')
    " > /dev/null 2>&1
    
    sleep 0.5  # Pieni tauko visualisoinnin vuoksi
done

echo ""
echo "✅ TESTI VALMIS!"
echo ""
echo "📈 LOPPUTILASTOT:"
python src/cli/elo_admin.py stats --election Jumaltenvaalit2026

echo ""
echo "🏆 LOPPURANKING:"
python src/cli/elo_admin.py leaderboard --election Jumaltenvaalit2026

echo ""
echo "🔍 ANALYYSI:"
python -c "
import json
with open('data/runtime/questions.json', 'r') as f:
    data = json.load(f)

questions = data['questions']
ratings = [q['elo_rating']['current_rating'] for q in questions]
deltas = [q['elo_rating'].get('comparison_delta', 0) for q in questions]

print(f'Korkein luokitus: {max(ratings)}')
print(f'Matalin luokitus: {min(ratings)}') 
print(f'Keskimääräinen muutos: {sum(deltas)/len(deltas):.1f}')
print(f'Suurin nousu: {max(deltas)}')
print(f'Suurin lasku: {min(deltas)}')

print()
print('Järjestelmä toimii korrektisti jos:')
print('✅ Luokitukset vaihtelevat (ei kaikki 1000)')
print('✅ Erot kysymysten välillä')
print('✅ Delta-arvojen jakauma on tasainen')

# Tarkista onko muutoksia tapahtunut
if max(ratings) != min(ratings) or any(d != 0 for d in deltas):
    print()
    print('🎉 ELO-JÄRJESTELMÄ TOIMII!')
    print('   Luokitukset muuttuvat vertailujen perusteella.')
else:
    print()
    print('❌ ELO-JÄRJESTELMÄ EI TOIMI')
    print('   Luokitukset eivät muutu. Tarkista compare_questions.py')
"
