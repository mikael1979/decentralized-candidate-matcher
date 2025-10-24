"""
Utils-moduuli hajautetulle vaalikoneelle
Turvallisuusfunktiot, apufunktiot ja yhteiset utilitieet
"""
import json
import os
import hashlib
from datetime import datetime
import re
from typing import Dict, Any, List, Optional

# === TURVALLISUUSKONFIGURAATIO ===
MAX_QUESTION_LENGTH = 500
MIN_QUESTION_LENGTH = 10
MAX_TAG_LENGTH = 50
MAX_TAGS_PER_QUESTION = 10

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
    """
    Poistaa potentiaalisesti vaarallisia merkkejä syötteistä - ULTRA-TURVALLINEN VERSIO
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # 1. Dekoodaa HTML-entityt AGRESSIIVISESTI
    import html
    text = html.unescape(text)
    
    # 2. Poista HTML/JavaScript tagit EXTRA-AGRESSIIVISESTI
    text = re.sub(r'<[^>]*>', '', text)  # Poista kaikki HTML tagit
    text = re.sub(r'</[^>]*>', '', text)  # Poista sulkevat tagit
    
    # 3. Poista JavaScript-yritykset KOKONAAN
    js_patterns = [
        r'javascript:', r'vbscript:', r'data:', r'about:',
        r'on\w+\s*=', r'on\w+\s*\(', r'on\w+\s*\[',
        r'alert\(', r'prompt\(', r'confirm\(', r'console\.',
        r'document\.', r'window\.', r'location\.', r'history\.',
        r'localStorage', r'sessionStorage', r'cookie',
        r'eval\(', r'exec\(', r'execScript\(', r'setTimeout\(',
        r'setInterval\(', r'Function\(', r'expression\('
    ]
    for pattern in js_patterns:
        text = re.sub(pattern, '[REMOVED]', text, flags=re.IGNORECASE)
    
    # 4. Poista SQL-injektiot KOKONAAN
    sql_patterns = [
        r'\bDROP\s+TABLE\b', r'\bDELETE\s+FROM\b', r'\bINSERT\s+INTO\b',
        r'\bSELECT\s+\*', r'\bUNION\s+SELECT\b', r'\bOR\s+1=1\b',
        r'\bEXEC\b', r'\bEXECUTE\b', r'\bTRUNCATE\b', r'\bCREATE\b',
        r'\bALTER\b', r'\bDROP\b', r'\bSHUTDOWN\b', r'\bUPDATE\b',
        r'\bDELETE\b', r'\bINSERT\b', r'\bFROM\b\s+\w+\s+WHERE',
        r';', r'--', r'/\*', r'\*/'
    ]
    for pattern in sql_patterns:
        text = re.sub(pattern, '[REMOVED]', text, flags=re.IGNORECASE)
    
    # 5. Poista directory traversal KOKONAAN
    traversal_patterns = [
        r'\.\./', r'\.\.\\', r'\.\.', r'\./', r'\.\\',
        r'etc/passwd', r'etc/shadow', r'etc/hosts',
        r'windows/system32', r'winnt/system32',
        r'../', r'..\\'
    ]
    for pattern in traversal_patterns:
        text = re.sub(pattern, '[REMOVED]', text, flags=re.IGNORECASE)
    
    # 6. Poista vaaralliset funktiokutsut KOKONAAN
    dangerous_functions = [
        'eval', 'exec', 'system', 'import', 'os.', 'subprocess', 
        'compile', 'input', 'open', 'file', 'execfile', 'reload',
        '__import__', 'getattr', 'setattr', 'delattr', 'hasattr',
        'apply', 'globals', 'locals', 'vars', 'dir', 'type',
        'input', 'raw_input', 'compile', 'memoryview', 'buffer',
        'help', 'breakpoint', 'copyright', 'credits', 'license'
    ]
    for func in dangerous_functions:
        text = re.sub(func, '[REMOVED]', text, flags=re.IGNORECASE)
    
    # 7. Poista erikoismerkit TÄYSIN
    dangerous_chars = [';', '--', '/*', '*/', '%27', '%22', '%3C', '%3E']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # 8. Poista komentorivin merkit TÄYSIN
    cmd_chars = ['|', '&', '`', '$', '(', ')', '{', '}', '[', ']', '<', '>']
    for char in cmd_chars:
        text = text.replace(char, '')
    
    # 9. Poista ylimääräiset välilyönnit ja palauta
    text = ' '.join(text.split())
    
    # 10. Jos teksti on tyhjä kaikkien poistojen jälkeen, palauta tyhjä
    if not text.strip():
        return "[EMPTY_AFTER_SANITIZATION]"
    
    return text.strip()

def sanitize_question_data(question_data):
    """Sanitoi kysymysdatan - PARANNELTU TURVALLINEN VERSIO"""
    if not isinstance(question_data, dict):
        return question_data
    
    sanitized = {}
    
    for key, value in question_data.items():
        if key == 'question' and isinstance(value, dict):
            # Sanitoi kaikki kieliversiot
            sanitized[key] = {}
            for lang, text in value.items():
                if isinstance(text, str):
                    sanitized[key][lang] = sanitize_input(text)
                else:
                    sanitized[key][lang] = str(text)
        
        elif key == 'tags' and isinstance(value, list):
            # Sanitoi tagit
            sanitized_tags = []
            for tag in value:
                if isinstance(tag, str):
                    sanitized_tag = sanitize_input(tag)
                    if sanitized_tag:  # Älä lisää tyhjiä tageja
                        sanitized_tags.append(sanitized_tag)
            sanitized[key] = sanitized_tags[:MAX_TAGS_PER_QUESTION]  # Rajaa tagien määrä
        
        elif key == 'category' and isinstance(value, str):
            sanitized[key] = sanitize_input(value)
        
        elif key == 'category' and isinstance(value, dict):
            # Sanitoi kategorian kieliversiot
            sanitized[key] = {}
            for lang, text in value.items():
                if isinstance(text, str):
                    sanitized[key][lang] = sanitize_input(text)
                else:
                    sanitized[key][lang] = str(text)
        
        else:
            # Säilytä muut kentät ennallaan (ei sanitoitavia merkkijonoja)
            sanitized[key] = value
    
    return sanitized

def sanitize_candidate_data(candidate_data):
    """Sanitoi ehdokasdatan - PARANNELTU TURVALLINEN VERSIO"""
    if not isinstance(candidate_data, dict):
        return candidate_data
    
    sanitized = candidate_data.copy()
    
    # Sanitoi perustiedot
    if 'name' in sanitized and isinstance(sanitized['name'], str):
        sanitized['name'] = sanitize_input(sanitized['name'])
    
    if 'party' in sanitized and isinstance(sanitized['party'], str):
        sanitized['party'] = sanitize_input(sanitized['party'])
    
    if 'district' in sanitized and isinstance(sanitized['district'], str):
        sanitized['district'] = sanitize_input(sanitized['district'])
    
    # Sanitoi vastaukset
    if 'answers' in sanitized and isinstance(sanitized['answers'], list):
        for answer in sanitized['answers']:
            if isinstance(answer, dict):
                if 'justification' in answer and isinstance(answer['justification'], dict):
                    sanitized_justification = {}
                    for lang, text in answer['justification'].items():
                        if isinstance(text, str):
                            sanitized_justification[lang] = sanitize_input(text)
                        else:
                            sanitized_justification[lang] = str(text)
                    answer['justification'] = sanitized_justification
    
    return sanitized

def validate_question_structure(question_data):
    """Validoi kysymyksen rakenteen - PARANNELTU TURVALLINEN VERSIO"""
    errors = []
    
    if not isinstance(question_data, dict):
        errors.append('Kysymysdatan tulee olla objekti')
        return errors
    
    # Tarkista pakolliset kentät
    if not question_data.get('question'):
        errors.append('Kysymys teksti puuttuu')
    elif not isinstance(question_data['question'], dict):
        errors.append('Kysymys kentän tulee olla objekti')
    else:
        fi_question = question_data['question'].get('fi', '')
        
        # TARKEMPI TURVALLISUUSVALIDAATIO
        # Estä tyhjät kysymykset
        if not fi_question or not fi_question.strip():
            errors.append('Kysymys suomeksi on pakollinen eikä saa olla tyhjä')
        
        # Estä XSS-tyyliset sisällöt
        xss_patterns = [
            r'<script', r'javascript:', r'vbscript:', r'on\w+\s*=',
            r'alert\(', r'prompt\(', r'confirm\(', r'document\.',
            r'window\.', r'location\.', r'cookie', r'localStorage',
            r'sessionStorage', r'eval\(', r'exec\(', r'expression\('
        ]
        for pattern in xss_patterns:
            if re.search(pattern, fi_question, re.IGNORECASE):
                errors.append('Kysymys sisältää kiellettyjä JavaScript-komentoja')
                break
        
        # Estä SQL-injektio yritykset
        sql_patterns = [
            r'drop\s+table', r'insert\s+into', r'delete\s+from', 
            r'truncate\s+table', r'update\s+\w+\s+set', 
            r'create\s+table', r'alter\s+table', r'union\s+select',
            r'or\s+1=1', r';\s*--', r'/\*.*\*/'
        ]
        for pattern in sql_patterns:
            if re.search(pattern, fi_question, re.IGNORECASE):
                errors.append('Kysymys sisältää SQL-injektio yrityksiä')
                break
        
        # Estä directory traversal
        traversal_patterns = [r'\.\./', r'\.\.\\', r'\.\.', r'etc/passwd', r'etc/shadow']
        for pattern in traversal_patterns:
            if re.search(pattern, fi_question, re.IGNORECASE):
                errors.append('Kysymys sisältää kiellettyjä polkumalleja')
                break
        
        # Pituusrajat
        if len(fi_question) < MIN_QUESTION_LENGTH:
            errors.append(f'Kysymyksen tulee olla vähintään {MIN_QUESTION_LENGTH} merkkiä pitkä')
        elif len(fi_question) > MAX_QUESTION_LENGTH:
            errors.append(f'Kysymys saa olla enintään {MAX_QUESTION_LENGTH} merkkiä pitkä')
    
    # Tarkista kategoria
    if not question_data.get('category'):
        errors.append('Kategoria puuttuu')
    
    # Tarkista tagit
    tags = question_data.get('tags', [])
    if not tags:
        errors.append('Vähintään yksi tagi on pakollinen')
    elif not isinstance(tags, list):
        errors.append('Tagien tulee olla lista')
    else:
        if len(tags) > MAX_TAGS_PER_QUESTION:
            errors.append(f'Kysymyksessä saa olla enintään {MAX_TAGS_PER_QUESTION} tagia')
        
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                errors.append(f'Tagi {i+1} ei ole merkkijono')
                continue
            
            if len(tag) > MAX_TAG_LENGTH:
                errors.append(f'Tagi "{tag[:20]}..." on liian pitkä (max {MAX_TAG_LENGTH} merkkiä)')
            
            # Tarkista ettei tagi sisällä vaarallisia merkkejä
            if re.search(r'[<>]', tag):
                errors.append(f'Tagi "{tag}" sisältää kiellettyjä merkkejä')
            
            # Tarkista ettei tagi ole tyhjä
            if not tag.strip():
                errors.append('Tagit eivät saa olla tyhjiä')
    
    # Tarkista scale-objekti
    scale = question_data.get('scale', {})
    if not isinstance(scale, dict):
        errors.append('Scale-kentän tulee olla objekti')
    else:
        if scale.get('min') != -5 or scale.get('max') != 5:
            errors.append('Scale-kentän tulee olla välillä -5 - 5')
    
    return errors

def validate_candidate_structure(candidate_data):
    """Validoi ehdokkaan rakenteen - PARANNELTU TURVALLINEN VERSIO"""
    errors = []
    
    if not isinstance(candidate_data, dict):
        errors.append('Ehdokasdatan tulee olla objekti')
        return errors
    
    # Tarkista pakolliset kentät
    if not candidate_data.get('name'):
        errors.append('Nimi on pakollinen')
    elif not isinstance(candidate_data['name'], str):
        errors.append('Nimen tulee olla merkkijono')
    elif len(candidate_data['name']) < 2:
        errors.append('Nimen tulee olla vähintään 2 merkkiä pitkä')
    elif len(candidate_data['name']) > 100:
        errors.append('Nimi saa olla enintään 100 merkkiä pitkä')
    
    if not candidate_data.get('party'):
        errors.append('Puolue on pakollinen')
    elif not isinstance(candidate_data['party'], str):
        errors.append('Puolueen tulee olla merkkijono')
    
    # Tarkista district
    if 'district' in candidate_data and candidate_data['district']:
        if not isinstance(candidate_data['district'], str):
            errors.append('Districtin tulee olla merkkijono')
    
    # Tarkista vastaukset
    answers = candidate_data.get('answers', [])
    if not isinstance(answers, list):
        errors.append('Answers-kentän tulee olla lista')
    else:
        for i, answer in enumerate(answers):
            if not isinstance(answer, dict):
                errors.append(f'Vastaus {i+1}: värrä muoto')
                continue
            
            if 'question_id' not in answer:
                errors.append(f'Vastaus {i+1}: question_id puuttuu')
            elif not isinstance(answer['question_id'], (int, str)):
                errors.append(f'Vastaus {i+1}: question_id ei ole numero tai merkkijono')
            
            if 'answer' not in answer:
                errors.append(f'Vastaus {i+1}: answer puuttuu')
            elif not isinstance(answer['answer'], (int, float)):
                errors.append(f'Vastaus {i+1}: answer ei ole numero')
            elif not (-5 <= answer['answer'] <= 5):
                errors.append(f'Vastaus {i+1}: answer tulee olla välillä -5 - 5')
            
            # Tarkista confidence
            if 'confidence' in answer:
                if not isinstance(answer['confidence'], (int, float)):
                    errors.append(f'Vastaus {i+1}: confidence ei ole numero')
                elif not (0.0 <= answer['confidence'] <= 1.0):
                    errors.append(f'Vastaus {i+1}: confidence tulee olla välillä 0.0 - 1.0')
            
            # Tarkista justification
            if 'justification' in answer:
                if not isinstance(answer['justification'], dict):
                    errors.append(f'Vastaus {i+1}: justification ei ole objekti')
    
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
    """Lokiturvallisuustapahtuma - PARANNELTU VERSIO"""
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

def security_headers(response):
    """Lisää turvallisuusheaderit HTTP-vastauksiin"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'"
    return response

def validate_session(session_data):
    """Validoi sessiodatan turvallisuus"""
    if not session_data:
        return False
    
    # Tarkista että sessio ei ole vanhentunut
    login_time = session_data.get('admin_login_time')
    if not login_time:
        return False
    
    try:
        login_dt = datetime.fromisoformat(login_time.replace('Z', '+00:00'))
        session_age = (datetime.now() - login_dt).total_seconds()
        
        # Sessio vanhenee 8 tunnin jälkeen
        if session_age > 8 * 3600:
            return False
    except:
        return False
    
    return session_data.get('admin_authenticated', False)

# === TESTIFUNKTIOT ===
def test_sanitization():
    """Testaa sanitointifunktioita"""
    print("🧪 TESTI: Sanitointifunktiot")
    
    test_cases = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../etc/passwd",
        "{{7*7}}",
        "javascript:alert('xss')",
        "onclick=alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "eval('malicious code')",
        "normal safe text"
    ]
    
    for test_input in test_cases:
        output = sanitize_input(test_input)
        print(f"Input: {test_input[:30]}... -> Output: {output}")
    
    return True

if __name__ == '__main__':
    test_sanitization()