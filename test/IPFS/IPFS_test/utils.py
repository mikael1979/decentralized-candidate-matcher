import json
import os
import hashlib
from datetime import datetime
import re

def calculate_percentage_level(percentage):
    """Muuntaa prosenttiluvun sanalliseksi tasoksi"""
    if percentage >= 90:
        return "erinomainen"
    elif percentage >= 80:
        return "hyvä"
    elif percentage >= 70:
        return "tyydyttävä"
    elif percentage >= 60:
        return "kohtalainen"
    elif percentage >= 50:
        return "heikko"
    else:
        return "erittäin heikko"

def calculate_similarity(text1, text2):
    """Laskee kahden tekstin samankaltaisuuden (0-1 välillä)"""
    if not text1 or not text2:
        return 0.0
    # Yksinkertainen samankaltaisuus: jaettu levenshtein-etäisyys
    def levenshtein(s1, s2):
        if len(s1) < len(s2):
            return levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]
    
    max_len = max(len(text1), len(text2))
    if max_len == 0:
        return 1.0
    distance = levenshtein(text1.lower(), text2.lower())
    return 1.0 - (distance / max_len)

def generate_next_id(items):
    """Luo seuraavan ID:n listalle"""
    if not items:
        return 1
    existing_ids = [item.get('id', 0) for item in items if isinstance(item.get('id'), int)]
    return max(existing_ids) + 1 if existing_ids else 1

def calculate_hash(data):
    """Laskee SHA256 hash datalle"""
    # Poista integrity ja metadata ennen hashin laskemista
    data_copy = data.copy()
    data_copy.pop('integrity', None)
    data_copy.pop('metadata', None)
    json_str = json.dumps(data_copy, sort_keys=True, ensure_ascii=False)
    return f"sha256:{hashlib.sha256(json_str.encode('utf-8')).hexdigest()}"

def sanitize_input(text):
    """Poistaa potentiaalisesti vaarallisia merkkejä syötteistä"""
    if not isinstance(text, str):
        return text
    
    # Poista HTML/JavaScript tagit
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text)  # Poista kaikki HTML tagit
    
    # Poista SQL-injection -tyyliset merkit
    text = text.replace("'", "''")  # Escape single quotes
    text = text.replace(";", "")    # Poista semikolonit
    text = text.replace("--", "")   # Poista SQL kommentit
    
    # Poista directory traversal -merkit
    text = text.replace("../", "")
    text = text.replace("..\\", "")
    
    # Poista potentiaalisesti vaaralliset funktiokutsut
    text = text.replace("eval(", "")
    text = text.replace("exec(", "")
    text = text.replace("system(", "")
    
    return text.strip()

def sanitize_question_data(question_data):
    """Sanitoi kysymysdatan"""
    if isinstance(question_data, dict):
        sanitized = {}
        for key, value in question_data.items():
            if key == 'question' and isinstance(value, dict):
                # Sanitoi kaikki kieliversiot
                sanitized[key] = {lang: sanitize_input(text) for lang, text in value.items()}
            elif key == 'tags' and isinstance(value, list):
                sanitized[key] = [sanitize_input(tag) for tag in value]
            elif key == 'category' and isinstance(value, str):
                sanitized[key] = sanitize_input(value)
            elif key == 'category' and isinstance(value, dict):
                # Sanitoi kategorian kieliversiot
                sanitized[key] = {lang: sanitize_input(text) for lang, text in value.items()}
            else:
                sanitized[key] = value
        return sanitized
    return question_data

def sanitize_candidate_data(candidate_data):
    """Sanitoi ehdokasdatan"""
    if isinstance(candidate_data, dict):
        sanitized = candidate_data.copy()
        
        # Sanitoi perustiedot
        if 'name' in sanitized:
            sanitized['name'] = sanitize_input(sanitized['name'])
        if 'party' in sanitized:
            sanitized['party'] = sanitize_input(sanitized['party'])
        if 'district' in sanitized:
            sanitized['district'] = sanitize_input(sanitized['district'])
        
        # Sanitoi vastaukset
        if 'answers' in sanitized and isinstance(sanitized['answers'], list):
            for answer in sanitized['answers']:
                if isinstance(answer, dict):
                    if 'justification' in answer and isinstance(answer['justification'], dict):
                        answer['justification'] = {
                            lang: sanitize_input(text) 
                            for lang, text in answer['justification'].items()
                        }
        
        return sanitized
    return candidate_data

def validate_question_structure(question_data):
    """Validoi kysymyksen rakenteen"""
    errors = []
    
    # Tarkista pakolliset kentät
    if not question_data.get('question'):
        errors.append('Kysymys teksti puuttuu')
    elif not isinstance(question_data['question'], dict):
        errors.append('Kysymys kentän tulee olla objekti')
    elif not question_data['question'].get('fi'):
        errors.append('Kysymys suomeksi on pakollinen')
    
    if not question_data.get('category'):
        errors.append('Kategoria puuttuu')
    
    # Tarkista kysymyksen pituus
    fi_question = question_data.get('question', {}).get('fi', '')
    if len(fi_question) < 10:
        errors.append('Kysymyksen tulee olla vähintään 10 merkkiä pitkä')
    elif len(fi_question) > 500:
        errors.append('Kysymys saa olla enintään 500 merkkiä pitkä')
    
    # Tarkista tagit
    tags = question_data.get('tags', [])
    if not tags:
        errors.append('Vähintään yksi tagi on pakollinen')
    elif len(tags) > 10:
        errors.append('Kysymyksessä saa olla enintään 10 tagia')
    elif any(len(tag) > 50 for tag in tags):
        errors.append('Tagien maksimipituus on 50 merkkiä')
    
    return errors

def validate_candidate_structure(candidate_data):
    """Validoi ehdokkaan rakenteen"""
    errors = []
    
    # Tarkista pakolliset kentät
    if not candidate_data.get('name'):
        errors.append('Nimi on pakollinen')
    elif len(candidate_data['name']) < 2:
        errors.append('Nimen tulee olla vähintään 2 merkkiä pitkä')
    
    if not candidate_data.get('party'):
        errors.append('Puolue on pakollinen')
    
    # Tarkista vastaukset
    answers = candidate_data.get('answers', [])
    for i, answer in enumerate(answers):
        if not isinstance(answer, dict):
            errors.append(f'Vastaus {i+1}: väärä muoto')
            continue
            
        if 'question_id' not in answer:
            errors.append(f'Vastaus {i+1}: question_id puuttuu')
        
        if 'answer' not in answer:
            errors.append(f'Vastaus {i+1}: answer puuttuu')
        elif not isinstance(answer['answer'], (int, float)):
            errors.append(f'Vastaus {i+1}: answer ei ole numero')
        elif not (-5 <= answer['answer'] <= 5):
            errors.append(f'Vastaus {i+1}: answer tulee olla välillä -5 - 5')
    
    return errors

class ConfigLoader:
    """Lataa konfiguraatiotiedostot"""
    def __init__(self, config_dir='config'):
        self.config_dir = config_dir
    
    def load_config(self, filename):
        """Lataa konfiguraatiotiedoston"""
        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Virhe luettaessa {filepath}: {e}")
            # Palauta tyhjä rakenne
            if 'questions' in filename:
                return {"default_questions": []}
            elif 'candidates' in filename:
                return {"default_candidates": []}
            elif 'meta' in filename:
                return {"default_meta": {}}
            elif 'admins' in filename:
                return {"super_admins": [], "party_admins": {}}
            return {}

def handle_api_errors(f):
    """API-virheenkäsittely dekoraattori"""
    from functools import wraps
    from flask import jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f"❌ API-virhe funktiossa {f.__name__}: {e}")
            return jsonify({
                'success': False,
                'error': 'Sisäinen virhe',
                'details': str(e) if False else None  # Älä paljasta virheitä tuotannossa
            }), 500
    return decorated_function

def log_security_event(event_type, description, user_id=None, ip_address=None):
    """Lokiturvallisuustapahtuma"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'description': description,
        'user_id': user_id,
        'ip_address': ip_address
    }
    
    # Yksinkertainen lokitus - tuotannossa käytä proper logging frameworkia
    security_log_path = 'security.log'
    try:
        with open(security_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"⚠️  Turvallisuuslokin kirjoitusvirhe: {e}")
