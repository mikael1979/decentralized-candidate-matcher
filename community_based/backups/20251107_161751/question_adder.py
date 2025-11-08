# question_adder.py
#!/usr/bin/env python3
"""
Kysymysten lisäystyökalu - Estää duplikaatit ja auttaa tagien hallinnassa
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional

class QuestionAdder:
    """Kysymysten lisäystyökalu duplikaattien estolla"""
    
    def __init__(self, runtime_dir: str = "runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.questions_file = self.runtime_dir / "questions.json"
        self.tmp_questions_file = self.runtime_dir / "tmp_new_questions.json"
        self.tags_file = self.runtime_dir / "question_tags.json"
        
        self.existing_tags = self.load_existing_tags()
        self.all_questions = self.load_all_questions()
    
    def load_all_questions(self) -> List[Dict]:
        """Lataa kaikki kysymykset kaikista tiedostoista"""
        all_questions = []
        
        # Tiedostot joista kysymykset haetaan
        question_files = [
            self.questions_file,
            self.tmp_questions_file,
            self.runtime_dir / "new_questions.json",
            self.runtime_dir / "active_questions.json"
        ]
        
        for file_path in question_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_questions.extend(data.get('questions', []))
                except Exception as e:
                    print(f"⚠️  Virhe ladattaessa {file_path}: {e}")
        
        return all_questions
    
    def load_existing_tags(self) -> Set[str]:
        """Lataa olemassa olevat tagit"""
        if self.tags_file.exists():
            try:
                with open(self.tags_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('tags', []))
            except Exception as e:
                print(f"⚠️  Virhe ladattaessa tageja: {e}")
        
        # Jos tag-tiedostoa ei ole, luo se kysymyksistä
        return self.extract_tags_from_questions()
    
    def extract_tags_from_questions(self) -> Set[str]:
        """Poimi tagit olemassa olevista kysymyksistä"""
        tags = set()
        
        for question in self.all_questions:
            question_tags = question.get('content', {}).get('tags', [])
            tags.update(question_tags)
        
        # Tallenna tagit tiedostoon
        self.save_tags(tags)
        return tags
    
    def save_tags(self, tags: Set[str]):
        """Tallenna tagit tiedostoon"""
        tags_data = {
            "metadata": {
                "total_tags": len(tags),
                "last_updated": datetime.now().isoformat(),
                "source": "question_adder"
            },
            "tags": sorted(list(tags))
        }
        
        with open(self.tags_file, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, indent=2, ensure_ascii=False)
    
    def find_similar_questions(self, question_text: str, tags: List[str]) -> List[Dict]:
        """Etsi vastaavia kysymyksiä tekstin ja tagien perusteella"""
        similar_questions = []
        question_lower = question_text.lower()
        
        for question in self.all_questions:
            similarity_score = self.calculate_similarity(question, question_lower, tags)
            if similarity_score > 0.3:  # 30% samankaltaisuus kynnys
                question['similarity_score'] = similarity_score
                similar_questions.append(question)
        
        # Lajittele samankaltaisuuden mukaan
        return sorted(similar_questions, key=lambda x: x['similarity_score'], reverse=True)
    
    def calculate_similarity(self, question: Dict, new_question: str, new_tags: List[str]) -> float:
        """Laske kysymysten samankaltaisuus"""
        score = 0.0
        
        # 1. Tekstimäinen samankaltaisuus
        existing_question = question['content']['question']['fi'].lower()
        text_similarity = self.text_similarity(existing_question, new_question)
        score += text_similarity * 0.6  # 60% paino tekstille
        
        # 2. Tagien samankaltaisuus
        existing_tags = set(question['content'].get('tags', []))
        new_tags_set = set(new_tags)
        
        if existing_tags and new_tags_set:
            tag_overlap = len(existing_tags.intersection(new_tags_set)) / len(existing_tags.union(new_tags_set))
            score += tag_overlap * 0.4  # 40% paino tageille
        
        return score
    
    def text_similarity(self, text1: str, text2: str) -> float:
        """Yksinkertainen tekstinsamankaltaisuus"""
        words1 = set(re.findall(r'\w+', text1))
        words2 = set(re.findall(r'\w+', text2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def suggest_tags(self, question_text: str) -> List[str]:
        """Ehdota tageja kysymyksen perusteella"""
        suggested_tags = set()
        words = re.findall(r'\w+', question_text.lower())
        
        # Tunnista avainsanoja ja ehdota vastaavia tageja
        keyword_to_tags = {
            'maksu': ['talous', 'maksut', 'rahallinen'],
            'vero': ['talous', 'verotus', 'valtio'],
            'koulu': ['koulutus', 'opetus', 'opiskelu'],
            'terveys': ['terveydenhoito', 'sairaus', 'lääkäri'],
            'ympäristö': ['luonto', 'saastuminen', 'kestävä'],
            'työ': ['työllisyys', 'palkka', 'työpaikka'],
            'asuminen': ['asunto', 'vuokra', 'omistus'],
            'liikenne': ['auto', 'julkinen', 'tiet'],
            'energia': ['sähkö', 'öljy', 'uusiutuva'],
            'turvallisuus': ['poliisi', 'rikollisuus', 'sotilaallinen']
        }
        
        for word in words:
            if word in keyword_to_tags:
                suggested_tags.update(keyword_to_tags[word])
        
        # Ehdota myös olemassa olevista tageista
        for tag in self.existing_tags:
            if any(word in tag for word in words):
                suggested_tags.add(tag)
        
        return sorted(list(suggested_tags))
    
    def add_question_to_tmp(self, question_data: Dict) -> bool:
        """Lisää kysymys tmp_new_questions.json tiedostoon"""
        
        # Lataa nykyiset tmp-kysymykset
        tmp_questions = []
        if self.tmp_questions_file.exists():
            try:
                with open(self.tmp_questions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    tmp_questions = data.get('questions', [])
            except Exception as e:
                print(f"⚠️  Virhe ladattaessa tmp-kysymyksiä: {e}")
                return False
        
        # Lisää uusi kysymys
        tmp_questions.append(question_data)
        
        # Tallenna
        tmp_data = {
            "metadata": {
                "version": "2.0.0",
                "created": datetime.now().isoformat(),
                "total_questions": len(tmp_questions),
                "source": "question_adder"
            },
            "questions": tmp_questions
        }
        
        try:
            with open(self.tmp_questions_file, 'w', encoding='utf-8') as f:
                json.dump(tmp_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Virhe tallentaessa kysymystä: {e}")
            return False
    
    def create_question_data(self, question_text: str, tags: List[str], category: str = "yleinen") -> Dict:
        """Luo kysymysdata JSON-muotoon"""
        
        # Generoi kysymys-ID
        import hashlib
        question_hash = hashlib.sha256(question_text.encode()).hexdigest()[:16]
        question_id = f"q{question_hash}"
        
        return {
            "local_id": question_id,
            "content": {
                "category": {
                    "fi": category,
                    "en": "general",
                    "sv": "allmän"
                },
                "question": {
                    "fi": question_text,
                    "en": question_text,  # Käännä tarvittaessa
                    "sv": question_text   # Käännä tarvittaessa
                },
                "tags": tags,
                "scale": {
                    "min": -5,
                    "max": 5,
                    "labels": {
                        "fi": {
                            "min": "Täysin eri mieltä",
                            "neutral": "Neutraali",
                            "max": "Täysin samaa mieltä"
                        },
                        "en": {
                            "min": "Strongly disagree",
                            "neutral": "Neutral",
                            "max": "Strongly agree"
                        },
                        "sv": {
                            "min": "Helt avig",
                            "neutral": "Neutral",
                            "max": "Helt enig"
                        }
                    }
                }
            },
            "elo_rating": {
                "base_rating": 1000,
                "current_rating": 1000,
                "comparison_delta": 0,
                "vote_delta": 0,
                "total_comparisons": 0,
                "total_votes": 0,
                "up_votes": 0,
                "down_votes": 0
            },
            "timestamps": {
                "created_local": datetime.now().isoformat(),
                "modified_local": datetime.now().isoformat()
            },
            "metadata": {
                "submitted_by": "question_adder",
                "status": "pending",
                "source": "manual_addition"
            }
        }

def main():
    """Pääohjelma kysymyksen lisäämiseen"""
    
    print("🎯 KYSYMYKSEN LISÄYSTYÖKALU")
    print("=" * 50)
    print("Tämä työkalu auttaa lisäämään uusia kysymyksiä ja estää duplikaatit.")
    print()
    
    adder = QuestionAdder()
    
    # 1. Kysy kysymys
    print("📝 SYÖTÄ UUSI KYSYMYS:")
    question_text = input("Kysymys (suomeksi): ").strip()
    
    if not question_text:
        print("❌ Kysymys ei voi olla tyhjä")
        return
    
    # 2. Ehdota tageja
    suggested_tags = adder.suggest_tags(question_text)
    if suggested_tags:
        print(f"\n🏷️  EHDOtETUT TAGIT: {', '.join(suggested_tags)}")
    
    # 3. Kysy tagit
    print("\n🏷️  LISÄÄ TAGEJA (erota pilkulla, tai jätä tyhjä):")
    tags_input = input("Tagit: ").strip()
    
    if tags_input:
        user_tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    else:
        user_tags = []
    
    # Yhdistä ehdotetut ja käyttäjän tagit
    all_tags = list(set(user_tags + suggested_tags))
    
    # 4. Etsi vastaavia kysymyksiä
    print(f"\n🔍 ETSITÄÄN VASTAAVIA KYSYMYKSIÄ...")
    similar_questions = adder.find_similar_questions(question_text, all_tags)
    
    if similar_questions:
        print(f"✅ LÖYDETTY {len(similar_questions)} VASTAAVAA KYSYMYSTÄ:")
        print("-" * 50)
        
        for i, similar in enumerate(similar_questions[:5], 1):  # Näytä max 5
            sim_question = similar['content']['question']['fi']
            sim_tags = similar['content'].get('tags', [])
            similarity = similar['similarity_score']
            
            print(f"{i}. {sim_question[:80]}...")
            print(f"   Tagit: {', '.join(sim_tags)}")
            print(f"   Samankaltaisuus: {similarity:.1%}")
            print()
        
        # Kysy haluaako käyttäjä jatkaa
        if len(similar_questions) > 3:  # Jos paljon vastaavia
            response = input("⏰ Löytyi useita vastaavia kysymyksiä. Haluatko jatkaa? (K/e): ").strip().lower()
            if response in ['e', 'ei', 'no']:
                print("❌ Kysymyksen lisäys peruttu")
                return
    
    else:
        print("✅ Ei löytynyt vastaavia kysymyksiä - voit turvallisesti lisätä uuden!")
    
    # 5. Kysy vahvistus
    print(f"\n📋 UUSI KYSYMYS:")
    print(f"   {question_text}")
    print(f"   Tagit: {', '.join(all_tags) if all_tags else 'ei tageja'}")
    print()
    
    confirmation = input("Haluatko tallentaa tämän kysymyksen? (K/e): ").strip().lower()
    
    if confirmation not in ['', 'k', 'kyllä', 'y', 'yes']:
        print("❌ Kysymyksen lisäys peruttu")
        return
    
    # 6. Luo ja tallenna kysymys
    question_data = adder.create_question_data(question_text, all_tags)
    
    if adder.add_question_to_tmp(question_data):
        print(f"✅ KYSYMYS TALLENNETTU ONNISTUNEESTI!")
        print(f"   📁 Tiedosto: {adder.tmp_questions_file}")
        print(f"   🆔 Kysymys ID: {question_data['local_id']}")
        print(f"   🏷️  Tagit: {', '.join(all_tags)}")
        print(f"   📊 Status: Odottaa synkronointia")
        
        # Päivitä tagit
        adder.existing_tags.update(all_tags)
        adder.save_tags(adder.existing_tags)
        print(f"   ✅ {len(all_tags)} tagia päivitetty tagikirjastoon")
        
        # Näytä seuraavat vaiheet
        print(f"\n📋 SEURAAVAT VAIHEET:")
        print("   1. Kysymys siirretään automaattisesti new_questions.json:iin")
        print("   2. Kysymys osallistuu vertailuihin ja saa ELO-luokituksen")
        print("   3. Parhaat kysymykset siirtyvät active_questions.json:iin")
        print(f"\n💡 Voit nyt synkronoida: python manage_questions.py sync")
        
    else:
        print("❌ Kysymyksen tallennus epäonnistui")

def batch_add_questions():
    """Lisää useita kysymyksiä kerralla tiedostosta"""
    
    print("📦 USEAN KYSYMYKSEN LISÄYS TIEDOSTOSTA")
    print("=" * 50)
    
    file_path = input("Syötä kysymystiedoston polku: ").strip()
    
    if not Path(file_path).exists():
        print("❌ Tiedostoa ei löydy")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                data = json.load(f)
                questions = data.get('questions', [])
            else:
                # Oleta tekstiedosto, yksi kysymys per rivi
                questions = [{"question": line.strip(), "tags": []} for line in f if line.strip()]
        
        adder = QuestionAdder()
        added_count = 0
        
        for i, q_data in enumerate(questions, 1):
            if isinstance(q_data, str):
                question_text = q_data
                tags = []
            else:
                question_text = q_data.get('question', '')
                tags = q_data.get('tags', [])
            
            if not question_text:
                continue
            
            print(f"\n[{i}/{len(questions)}] Käsitellään: {question_text[:60]}...")
            
            # Tarkista onko vastaavia
            similar = adder.find_similar_questions(question_text, tags)
            if similar and similar[0]['similarity_score'] > 0.7:
                print(f"   ⚠️  OHITETAAN - Löytyi vastaava: {similar[0]['content']['question']['fi'][:50]}...")
                continue
            
            # Lisää kysymys
            question_data = adder.create_question_data(question_text, tags)
            if adder.add_question_to_tmp(question_data):
                added_count += 1
                print(f"   ✅ LISÄTTY")
            
            # Päivitä tagit
            adder.existing_tags.update(tags)
        
        # Tallenna tagit
        adder.save_tags(adder.existing_tags)
        
        print(f"\n🎉 LISÄTTY {added_count}/{len(questions)} KYSYMYSTÄ!")
        print(f"💡 Synkronoi: python manage_questions.py sync")
        
    except Exception as e:
        print(f"❌ Virhe käsiteltäessä tiedostoa: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--batch':
        batch_add_questions()
    else:
        main()
