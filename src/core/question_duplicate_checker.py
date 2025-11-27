#!/usr/bin/env python3
"""
Kysymysten duplikaattien tarkistus - estää samanlaisten kysymysten lisäämisen
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher


class QuestionDuplicateChecker:
    """Tarkistaa ja estää duplikaattikysymykset"""
    
    def __init__(self, election_id: str = None):
        self.election_id = election_id
        self.questions_data = None
        
    def load_questions(self) -> Dict:
        """Lataa nykyiset kysymykset suoraan tiedostosta"""
        if self.questions_data is not None:
            return self.questions_data
            
        questions_data = {}
        
        # Lataa suoraan tiedostosta
        data_path = Path("data/elections")
        if self.election_id and data_path.exists():
            election_path = data_path / self.election_id / "questions.json"
            if election_path.exists():
                try:
                    with open(election_path, 'r', encoding='utf-8') as f:
                        file_content = f.read().strip()
                        if not file_content:
                            print("⚠️  Kysymystiedosto on tyhjä")
                            return {}
                        
                        data = json.loads(file_content)
                        
                        # DEBUG: Tulosta data rakenne
                        print(f"🔍 LADATUN DATAN RAKENNE: {type(data)}")
                        
                        # Käsittele eri data-formaatteja
                        if isinstance(data, list):
                            print(f"📋 Data on lista, pituus: {len(data)}")
                            
                            # Tapaus 1: Lista suoria kysymyksiä
                            if data and isinstance(data[0], dict) and 'question_fi' in data[0]:
                                print("✅ Lista suoria kysymyksiä")
                                for i, item in enumerate(data):
                                    if isinstance(item, dict) and 'id' in item:
                                        questions_data[item['id']] = item
                                print(f"✅ Muunnettiin {len(questions_data)} kysymystä listasta")
                            
                            # Tapaus 2: Lista, jossa on yksi alkio joka sisältää 'questions' kentän
                            elif data and isinstance(data[0], dict) and 'questions' in data[0]:
                                print("✅ Lista, jossa 'questions' kenttä")
                                questions_list = data[0]['questions']
                                if isinstance(questions_list, list):
                                    for item in questions_list:
                                        if isinstance(item, dict) and 'id' in item:
                                            questions_data[item['id']] = item
                                    print(f"✅ Ladattiin {len(questions_data)} kysymystä 'questions' kentästä")
                            
                            else:
                                print(f"❌ Tuntematon lista-formaatti")
                                for i, item in enumerate(data[:2]):
                                    print(f"   Alkio {i}: {type(item)} - {item}")
                        
                        elif isinstance(data, dict):
                            print(f"📋 Data on dictionary, avaimia: {len(data)}")
                            
                            # Tapaus 3: Dictionary suorilla kysymyksillä
                            if 'question_fi' in list(data.values())[0] if data else False:
                                questions_data = data
                                print(f"✅ Ladattiin {len(questions_data)} kysymystä dictionarysta")
                            
                            # Tapaus 4: Dictionary, jossa on 'questions' kenttä
                            elif 'questions' in data:
                                questions_list = data['questions']
                                if isinstance(questions_list, list):
                                    for item in questions_list:
                                        if isinstance(item, dict) and 'id' in item:
                                            questions_data[item['id']] = item
                                    print(f"✅ Ladattiin {len(questions_data)} kysymystä 'questions' kentästä")
                            
                            else:
                                print(f"❌ Tuntematon dictionary-formaatti")
                                for key, value in list(data.items())[:2]:
                                    print(f"   Avain {key}: {type(value)}")
                        
                        else:
                            print(f"❌ Tuntematon data-tyyppi: {type(data)}")
                            
                    self.questions_data = questions_data
                    return questions_data
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON virhe kysymysten latauksessa: {e}")
                    print(f"📄 Tiedoston sisältö: {file_content[:200]}...")
                except Exception as e:
                    print(f"⚠️  Kysymysten lataus tiedostosta epäonnistui: {e}")
        
        print(f"⚠️  Ei kysymyksiä ladattu - tiedostoa ei löydy tai tyhjä")
        return {}
    
    def normalize_text(self, text: str) -> str:
        """Normalisoi teksti vertailua varten"""
        if not text:
            return ""
        
        # Muunna pieniksi kirjaimiksi
        text = text.lower()
        
        # Poista ylimääräiset välilyönnit
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Poista yleiset välimerkit (säilytä sisältö)
        text = re.sub(r'[.,!?;:()\-"]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Laskee kahden tekstin samankaltaisuuden 0-1 asteikolla"""
        normalized1 = self.normalize_text(text1)
        normalized2 = self.normalize_text(text2)
        
        if not normalized1 or not normalized2:
            return 0.0
        
        similarity = SequenceMatcher(None, normalized1, normalized2).ratio()
        return similarity
    
    def find_similar_questions(self, new_question: str, threshold: float = 0.7) -> List[Dict]:
        """Etsii samankaltaisia kysymyksiä"""
        questions = self.load_questions()
        similar_questions = []
        
        print(f"   🔍 Etsitään samankaltaisia kysymyksiä ({len(questions)} kysymystä)...")
        
        for q_id, q_data in questions.items():
            if not isinstance(q_data, dict):
                continue
                
            # Tarkista suomenkielinen teksti
            fi_text = q_data.get('question_fi', '')
            if not fi_text:
                continue
                
            similarity = self.calculate_similarity(new_question, fi_text)
            
            if similarity >= threshold:
                similar_questions.append({
                    'id': q_id,
                    'question_fi': fi_text,
                    'question_en': q_data.get('question_en', ''),
                    'category': q_data.get('category', ''),
                    'similarity': round(similarity, 3),
                    'similarity_percent': int(similarity * 100)
                })
        
        # Lajittele samankaltaisuuden mukaan (korkein ensin)
        similar_questions.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_questions
    
    def check_duplicate(self, question_fi: str, question_en: str = "", category: str = "") -> Dict:
        """Tarkistaa onko kysymys duplikaatti ja palauttaa tulokset"""
        results = {
            'is_duplicate': False,
            'similar_questions': [],
            'highest_similarity': 0.0,
            'suggestion': None
        }
        
        print(f"   🔍 Tarkistetaan: '{question_fi}'")
        
        # Etsi samankaltaisia kysymyksiä
        similar_fi = self.find_similar_questions(question_fi)
        
        if similar_fi:
            results['similar_questions'] = similar_fi
            results['highest_similarity'] = similar_fi[0]['similarity']
            results['is_duplicate'] = similar_fi[0]['similarity'] > 0.85
            
            if results['is_duplicate']:
                results['suggestion'] = f"KYSYMYS ON LIKI IDENTTINEN OLEMASSA OLEVAAN ({(similar_fi[0]['similarity_percent'])}% samankaltainen)"
            else:
                results['suggestion'] = f"Löytyi {len(similar_fi)} samankalaista kysymystä"
        
        return results
    
    def format_comparison(self, new_question: str, similar_questions: List[Dict]) -> str:
        """Muotoilee vertailun tulostusta varten"""
        if not similar_questions:
            return "✅ Ei samankaltaisia kysymyksiä löytynyt"
        
        output = ["🔍 LÖYDETTY SAMANKALTAISIA KYSYMYKSIÄ:"]
        output.append("=" * 50)
        
        for i, similar in enumerate(similar_questions[:3], 1):  # Näytä max 3
            output.append(f"{i}. 📋 ID: {similar['id']}")
            output.append(f"   📁 Kategoria: {similar['category']}")
            output.append(f"   🔍 Samankaltaisuus: {similar['similarity_percent']}%")
            output.append(f"   ❓ Olemassa: {similar['question_fi']}")
            output.append(f"   🆕 Uusi: {new_question}")
            output.append("   " + "-" * 40)
        
        if len(similar_questions) > 3:
            output.append(f"   ... ja {len(similar_questions) - 3} muuta samankalaista")
        
        return "\n".join(output)
    
    def save_to_new_questions(self, question_data: Dict, force: bool = False) -> bool:
        """Tallentaa kysymyksen new_questions.json tiedostoon"""
        try:
            data_path = Path("data/elections")
            if self.election_id and data_path.exists():
                election_path = data_path / self.election_id
                new_questions_file = election_path / "new_questions.json"
                
                # Lataa nykyiset new_questions
                new_questions = []
                if new_questions_file.exists():
                    try:
                        with open(new_questions_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                new_questions = json.loads(content)
                    except:
                        new_questions = []
                
                # Lisää uusi kysymys
                question_data['checked_for_duplicates'] = True
                question_data['duplicate_check_timestamp'] = self._get_timestamp()
                new_questions.append(question_data)
                
                # Tallenna
                with open(new_questions_file, 'w', encoding='utf-8') as f:
                    json.dump(new_questions, f, ensure_ascii=False, indent=2)
                
                return True
        except Exception as e:
            print(f"❌ Virhe tallennettaessa new_questions.json: {e}")
        
        return False
    
    def _get_timestamp(self) -> str:
        """Palauttaa aikaleiman"""
        from datetime import datetime
        return datetime.now().isoformat()
