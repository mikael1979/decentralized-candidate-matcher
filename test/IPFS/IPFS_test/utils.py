"""
Apufunktiot ja yhteiset utilitieet
"""
import hashlib
import json
from datetime import datetime


def calculate_percentage_level(percentage):
    """Yleinen prosenttitasojen laskenta"""
    if percentage >= 90:
        return "Erittäin korkea"
    elif percentage >= 75:
        return "Korkea"
    elif percentage >= 60:
        return "Kohtalainen"
    elif percentage >= 40:
        return "Matala"
    else:
        return "Erittäin matala"


def validate_text_length(text, min_len, max_len, field_name):
    """Validoi tekstin pituuden"""
    if not text or len(text.strip()) < min_len:
        return f"{field_name} on liian lyhyt (vähintään {min_len} merkkiä)"
    elif len(text) > max_len:
        return f"{field_name} on liian pitkä (enintään {max_len} merkkiä)"
    return None


def calculate_hash(data):
    """Laskee SHA256 hash datalle"""
    if isinstance(data, dict):
        # Poista integrity-kenttä ennen hashin laskemista
        data_without_integrity = data.copy()
        if 'integrity' in data_without_integrity:
            del data_without_integrity['integrity']
        
        # Muunna JSONiksi ja laske hash
        json_str = json.dumps(data_without_integrity, sort_keys=True, ensure_ascii=False)
        return f"sha256:{hashlib.sha256(json_str.encode('utf-8')).hexdigest()}"
    else:
        # Käsittele merkkijonot suoraan
        return f"sha256:{hashlib.sha256(str(data).encode('utf-8')).hexdigest()}"


def generate_next_id(items, default=0):
    """Generoi seuraavan ID:n itemeille"""
    if not items:
        return default + 1
    return max([item.get('id', default) for item in items], default=default) + 1


def calculate_similarity(text1, text2):
    """Laskee kahden tekstin välisen samankaltaisuuden (yksinkertaistettu)"""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def format_timestamp():
    """Palauttaa nykyisen aikaleiman ISO-muodossa"""
    return datetime.now().isoformat()


def handle_api_errors(func):
    """Decorator API-virheiden käsittelyyn"""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import traceback
            print(f"API Error in {func.__name__}: {str(e)}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': f'Operaatio epäonnistui: {str(e)}'
            }, 500
    return wrapper


class ConfigLoader:
    """Konfiguraatioiden lataamiseen"""
    
    @staticmethod
    def load_config(config_file):
        """Lataa konfiguraatiotiedoston"""
        try:
            with open(f'config/{config_file}', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Konfiguraatiotiedostoa ei löytynyt: {config_file}")
            return {}
        except Exception as e:
            print(f"❌ Virhe konfiguraation lataamisessa {config_file}: {e}")
            return {}
