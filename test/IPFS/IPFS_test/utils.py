import json
import os
import hashlib
from datetime import datetime

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
