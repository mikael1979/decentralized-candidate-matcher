from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime

app = Flask(__name__)

# Reitti staattisille tiedostoille
@app.route('/styles.css')
def serve_css():
    return send_from_directory('.', 'styles.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

# Reitti static-kansion tiedostoille
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Ladataan data JSON-tiedostoista
def load_questions():
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('questions', [])
    except FileNotFoundError:
        # Palauta esimerkkikysymyksiä jos tiedostoa ei löydy
        return [
            {
                "id": 1,
                "category": {"fi": "Ympäristö", "en": "Environment"},
                "question": {
                    "fi": "Pitäisikö kaupungin vähentää hiilidioksidipäästöjä 50% vuoteen 2030 mennessä?",
                    "en": "Should the city reduce carbon dioxide emissions by 50% by 2030?"
                }
            },
            {
                "id": 2,
                "category": {"fi": "Liikenne", "en": "Transportation"},
                "question": {
                    "fi": "Pitäisikö julkisen liikenteen olla ilmaista opiskelijoille?",
                    "en": "Should public transport be free for students?"
                }
            },
            {
                "id": 3,
                "category": {"fi": "Koulutus", "en": "Education"},
                "question": {
                    "fi": "Pitäisikö kaupungin tarjota ilmaisia ohjelmointikursseja nuorille?",
                    "en": "Should the city offer free programming courses for youth?"
                }
            }
        ]

def load_candidates():
    try:
        with open('candidates.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('candidates', [])
    except FileNotFoundError:
        # Palauta esimerkkiehdokkaita jos tiedostoa ei löydy
        return [
            {
                "id": 1,
                "name": "Matti Meikäläinen",
                "party": "Test Puolue",
                "district": "Helsinki",
                "answers": [
                    {"question_id": 1, "answer": 4},
                    {"question_id": 2, "answer": 3},
                    {"question_id": 3, "answer": 5}
                ]
            },
            {
                "id": 2,
                "name": "Liisa Esimerkki",
                "party": "Toinen Puolue", 
                "district": "Espoo",
                "answers": [
                    {"question_id": 1, "answer": 2},
                    {"question_id": 2, "answer": 5},
                    {"question_id": 3, "answer": 1}
                ]
            },
            {
                "id": 3,
                "name": "Pekka Kokeilu",
                "party": "Kolmas Puolue",
                "district": "Vantaa", 
                "answers": [
                    {"question_id": 1, "answer": -3},
                    {"question_id": 2, "answer": -1},
                    {"question_id": 3, "answer": 4}
                ]
            }
        ]

def load_user_questions():
    try:
        with open('newquestions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('questions', [])
    except FileNotFoundError:
        return []

# Lasketaan yhteensopivuus
def calculate_match(user_answers, candidate):
    total_diff = 0
    max_possible_diff = 0
    answered_count = 0
    
    for answer in candidate.get('answers', []):
        question_id = str(answer['question_id'])
        if question_id in user_answers:
            user_answer = user_answers[question_id]
            candidate_answer = answer['answer']
            
            # Oletetaan asteikko -5 - +5
            diff = abs(user_answer - candidate_answer)
            total_diff += diff
            max_possible_diff += 10  # max ero -5 -> +5
            answered_count += 1
    
    if answered_count == 0:
        return 0
    
    match_percentage = 1 - (total_diff / max_possible_diff)
    return match_percentage

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/questions')
def get_questions():
    official_questions = load_questions()
    user_questions = load_user_questions()
    all_questions = official_questions + user_questions
    
    # Muunna ID:t stringeiksi selaimen kannalta
    for q in all_questions:
        q['id'] = str(q['id'])
    
    return jsonify(all_questions)

@app.route('/api/candidates')
def get_candidates():
    candidates = load_candidates()
    return jsonify(candidates)

@app.route('/api/search', methods=['POST'])
def search_candidates():
    try:
        user_answers = request.json
        
        candidates = load_candidates()
        results = []
        
        for candidate in candidates:
            match_percentage = calculate_match(user_answers, candidate)
            
            # Tarkista montako kysymystä vastattiin
            matched_questions = 0
            match_details = []
            
            for answer in candidate.get('answers', []):
                question_id = str(answer['question_id'])
                if question_id in user_answers:
                    matched_questions += 1
                    match_details.append({
                        'question_id': question_id,
                        'candidate_answer': answer['answer'],
                        'user_answer': user_answers[question_id]
                    })
            
            if matched_questions > 0:  # Näytetään vain ehdokkaat joilla on vastauksia
                results.append({
                    'candidate': candidate,
                    'match_percentage': match_percentage,
                    'matched_questions': matched_questions,
                    'match_details': match_details
                })
        
        # Järjestä parhaimman matchauksen mukaan
        results.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return jsonify({
            'success': True,
            'matches': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def get_status():
    questions = load_questions()
    user_questions = load_user_questions()
    candidates = load_candidates()
    
    return jsonify({
        'official_questions': len(questions),
        'user_questions': len(user_questions),
        'candidates': len(candidates),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Varmistetaan että templates kansio on olemassa
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🚀 Käynnistetään Hajautettu Vaalikone...")
    print("📊 Sovellus saatavilla: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
