# test_api_sanitization.py
import requests
import json

def test_api_sanitization():
    """Testaa API:n sanitointia suoraan"""
    base_url = 'http://localhost:5000'
    
    test_cases = [
        {"question": {"fi": "<script>alert('xss')</script>"}, "category": "Testi", "tags": ["testi"]},
        {"question": {"fi": "'; DROP TABLE users; --"}, "category": "Testi", "tags": ["testi"]},
        {"question": {"fi": "../../etc/passwd"}, "category": "Testi", "tags": ["testi"]},
        {"question": {"fi": "{{7*7}}"}, "category": "Testi", "tags": ["testi"]},
        {"question": {"fi": "normaali turvallinen teksti"}, "category": "Testi", "tags": ["testi"]}
    ]
    
    print("🧪 API-TASON SANITOINTITESTI")
    print("=" * 50)
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\nTesti {i}: {test_data['question']['fi'][:30]}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/submit_question",
                json=test_data,
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            print(f"Vastaus: {response.json()}")
            
            # Tarkista tallennettu data
            if response.status_code == 200:
                questions_response = requests.get(f"{base_url}/api/questions")
                if questions_response.status_code == 200:
                    questions = questions_response.json()
                    if questions:
                        latest_question = questions[-1]
                        fi_text = latest_question.get('question', {}).get('fi', '')
                        print(f"Tallennettu teksti: {fi_text}")
                        print(f"🚨 HAITALLINEN SISÄLTÖ TALLENNETTU: {'<script>' in fi_text or 'DROP TABLE' in fi_text}")
            
        except Exception as e:
            print(f"❌ Virhe: {e}")

if __name__ == '__main__':
    test_api_sanitization()
