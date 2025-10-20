#!/usr/bin/env python3
"""
Data Integrity Hyökkäystestiskripti
Testaa kuinka järjestelmä reagoi luvattomiin muutoksiin
"""

import json
import os
import random
import hashlib
import subprocess
from datetime import datetime
import time

class SecurityTester:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Kirjaa testin tuloksen"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}: {message}")
        if details:
            print(f"   📝 {details}")
        print()
    
    def test_1_direct_file_modification(self):
        """Testaa suoraa tiedostomuutosta"""
        print("🔓 TESTI 1: Suora tiedostomuutos (questions.json)")
        
        try:
            # 1. Lue alkuperäinen tiedosto
            filepath = os.path.join(self.data_dir, 'questions.json')
            with open(filepath, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            # 2. Tee luvaton muutos
            modified_data = original_data.copy()
            if 'questions' in modified_data and len(modified_data['questions']) > 0:
                # Muuta ensimmäisen kysymyksen tekstiä
                original_question = modified_data['questions'][0]['question']['fi']
                modified_data['questions'][0]['question']['fi'] = "🚨 MUOKATTU: " + original_question
                
                # Kirjoita muokattu tiedosto
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(modified_data, f, indent=2, ensure_ascii=False)
                
                # 3. Odota ja tarkista havaitaanko muutos
                time.sleep(2)
                
                # 4. Tarkista API:n kautta integrity status
                import requests
                try:
                    response = requests.get('http://localhost:5000/api/data/verify', timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        issues_found = result.get('integrity_check', {}).get('issues_found', 0)
                        
                        if issues_found > 0:
                            self.log_test(
                                "Suora tiedostomuutos", 
                                True, 
                                "Muutos havaittu onnistuneesti", 
                                f"Löydetty {issues_found} ongelmaa"
                            )
                        else:
                            self.log_test(
                                "Suora tiedostomuutos", 
                                False, 
                                "Muutos EI havaittu", 
                                "Data integrity järjestelmä ei toimi odotetusti"
                            )
                    else:
                        self.log_test(
                            "Suora tiedostomuutos", 
                            False, 
                            "API-virhe", 
                            f"Status code: {response.status_code}"
                        )
                except Exception as e:
                    self.log_test(
                        "Suora tiedostomuutos", 
                        False, 
                        "Verkkovirhe", 
                        str(e)
                    )
                
                # 5. Palauta alkuperäinen tiedosto
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(original_data, f, indent=2, ensure_ascii=False)
                    
            else:
                self.log_test(
                    "Suora tiedostomuutos", 
                    False, 
                    "Testi epäonnistui", 
                    "Ei kysymyksiä saatavilla"
                )
                
        except Exception as e:
            self.log_test(
                "Suora tiedostomuutos", 
                False, 
                "Testi epäonnistui", 
                str(e)
            )
    
    def test_2_corrupt_json_file(self):
        """Testaa korruptoituneen JSON-tiedoston havaitsemista"""
        print("🔓 TESTI 2: Korruptoitunut JSON-tiedosto")
        
        try:
            filepath = os.path.join(self.data_dir, 'candidates.json')
            
            # 1. Lue alkuperäinen
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 2. Korruptoi tiedosto (poista sulkeva aaltosulje)
            corrupted_content = original_content.rstrip()[:-1]  # Poista viimeinen }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(corrupted_content)
            
            # 3. Tarkista havaitaanko korruptio
            time.sleep(2)
            
            import requests
            response = requests.get('http://localhost:5000/api/data/verify', timeout=10)
            if response.status_code == 200:
                result = response.json()
                issues = result.get('integrity_check', {}).get('issues', [])
                
                json_errors = [issue for issue in issues if 'JSON' in issue or 'corrupt' in issue.lower()]
                
                if json_errors:
                    self.log_test(
                        "Korruptoitunut JSON", 
                        True, 
                        "Korruptio havaittu", 
                        f"Löydetty: {json_errors[0]}"
                    )
                else:
                    self.log_test(
                        "Korruptoitunut JSON", 
                        False, 
                        "Korruptio EI havaittu", 
                        "JSON-virhe ei havaittu integrity-tarkistuksessa"
                    )
            else:
                self.log_test(
                    "Korruptoitunut JSON", 
                    False, 
                    "API-virhe", 
                    f"Status code: {response.status_code}"
                )
            
            # 4. Palauta alkuperäinen
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(original_content)
                
        except Exception as e:
            self.log_test(
                "Korruptoitunut JSON", 
                False, 
                "Testi epäonnistui", 
                str(e)
            )
    
    def test_3_missing_file(self):
        """Testaa puuttuvan tiedoston havaitsemista"""
        print("🔓 TESTI 3: Puuttuva tiedosto")
        
        try:
            filepath = os.path.join(self.data_dir, 'newquestions.json')
            backup_path = filepath + '.backup'
            
            # 1. Siirrä tiedosto väliaikaisesti
            if os.path.exists(filepath):
                os.rename(filepath, backup_path)
                
                # 2. Tarkista havaitaanko puuttuva tiedosto
                time.sleep(2)
                
                import requests
                response = requests.get('http://localhost:5000/api/data/verify', timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    issues = result.get('integrity_check', {}).get('issues', [])
                    
                    missing_errors = [issue for issue in issues if 'puuttuu' in issue.lower() or 'missing' in issue.lower()]
                    
                    if missing_errors:
                        self.log_test(
                            "Puuttuva tiedosto", 
                            True, 
                            "Puuttuva tiedosto havaittu", 
                            f"Löydetty: {missing_errors[0]}"
                        )
                    else:
                        self.log_test(
                            "Puuttuva tiedosto", 
                            False, 
                            "Puuttuva tiedosto EI havaittu", 
                            "Tiedoston puuttuminen ei havaittu"
                        )
                else:
                    self.log_test(
                        "Puuttuva tiedosto", 
                        False, 
                        "API-virhe", 
                        f"Status code: {response.status_code}"
                    )
                
                # 3. Palauta tiedosto
                os.rename(backup_path, filepath)
            else:
                self.log_test(
                    "Puuttuva tiedosto", 
                    False, 
                    "Testi epäonnistui", 
                    "Tiedostoa ei löydy"
                )
                
        except Exception as e:
            self.log_test(
                "Puuttuva tiedosto", 
                False, 
                "Testi epäonnistui", 
                str(e)
            )
    
    def test_4_hash_tampering(self):
        """Testaa hash-manipulaation havaitsemista"""
        print("🔓 TESTI 4: Hash-manipulaatio (meta.json)")
        
        try:
            filepath = os.path.join(self.data_dir, 'meta.json')
            
            # 1. Lue ja muokkaa meta.json hashia
            with open(filepath, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            
            original_hash = meta_data.get('integrity', {}).get('hash', '')
            
            # 2. Manipuloi hashia
            meta_data['integrity']['hash'] = 'sha256:fake_hash_1234567890'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, indent=2, ensure_ascii=False)
            
            # 3. Tarkista havaitaanko manipulaatio
            time.sleep(2)
            
            import requests
            response = requests.get('http://localhost:5000/api/data/verify', timeout=10)
            if response.status_code == 200:
                result = response.json()
                issues_found = result.get('integrity_check', {}).get('issues_found', 0)
                
                if issues_found > 0:
                    self.log_test(
                        "Hash-manipulaatio", 
                        True, 
                        "Hash-manipulaatio havaittu", 
                        f"Löydetty {issues_found} ongelmaa"
                    )
                else:
                    self.log_test(
                        "Hash-manipulaatio", 
                        False, 
                        "Hash-manipulaatio EI havaittu", 
                        "Väärä hash ei aiheuttanut hälytystä"
                    )
            else:
                self.log_test(
                    "Hash-manipulaatio", 
                    False, 
                    "API-virhe", 
                    f"Status code: {response.status_code}"
                )
            
            # 4. Palauta alkuperäinen hash
            meta_data['integrity']['hash'] = original_hash
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log_test(
                "Hash-manipulaatio", 
                False, 
                "Testi epäonnistui", 
                str(e)
            )
    
    def test_5_data_integrity_api(self):
        """Testaa data integrity API:n toimivuutta"""
        print("🔓 TESTI 5: Data Integrity API")
        
        try:
            import requests
            
            # Testaa eri API-endpointeja
            endpoints = [
                ('/api/data/status', 'Data status'),
                ('/api/data/verify', 'Data verify'),
                ('/api/data/files', 'Data files'),
                ('/api/version', 'Version info')
            ]
            
            all_success = True
            details = []
            
            for endpoint, name in endpoints:
                try:
                    response = requests.get(f'http://localhost:5000{endpoint}', timeout=10)
                    if response.status_code == 200:
                        details.append(f"{name}: ✅ ({response.status_code})")
                    else:
                        details.append(f"{name}: ❌ ({response.status_code})")
                        all_success = False
                except Exception as e:
                    details.append(f"{name}: ❌ ({str(e)})")
                    all_success = False
            
            self.log_test(
                "Data Integrity API", 
                all_success, 
                "API-testit suoritettu", 
                ", ".join(details)
            )
            
        except Exception as e:
            self.log_test(
                "Data Integrity API", 
                False, 
                "Testi epäonnistui", 
                str(e)
            )
    
    def run_all_tests(self):
        """Suorita kaikki testit"""
        print("🚀 KÄYNNISTETÄÄN DATA INTEGRITY HYÖKKÄYSTESTIT")
        print("=" * 60)
        print()
        
        # Tarkista että sovellus on käynnissä
        try:
            import requests
            response = requests.get('http://localhost:5000/api/status', timeout=5)
            if response.status_code != 200:
                print("❌ VASTAUS: Sovellus ei ole käynnissä localhost:5000")
                print("   Käynnistä ensin: python web_app.py")
                return
        except:
            print("❌ VASTAUS: Sovellus ei ole käynnissä localhost:5000")
            print("   Käynnistä ensin: python web_app.py")
            return
        
        print("✅ Sovellus on käynnissä, aloitetaan testit...")
        print()
        
        # Suorita testit
        self.test_1_direct_file_modification()
        self.test_2_corrupt_json_file() 
        self.test_3_missing_file()
        self.test_4_hash_tampering()
        self.test_5_data_integrity_api()
        
        # Tulosta yhteenveto
        self.print_summary()
    
    def print_summary(self):
        """Tulosta testien yhteenveto"""
        print()
        print("=" * 60)
        print("📊 TESTIYHTEENVETO")
        print("=" * 60)
        
        successful_tests = sum(1 for test in self.test_results if test['success'])
        total_tests = len(self.test_results)
        
        print(f"Suoritettu testejä: {total_tests}")
        print(f"Onnistuneita: {successful_tests}")
        print(f"Epäonnistuneita: {total_tests - successful_tests}")
        print()
        
        security_score = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"🔒 TURVALLISUUSPISTEET: {security_score:.1f}%")
        
        if security_score >= 80:
            print("🎉 ERINOMAISTA! Data integrity -järjestelmä toimii vahvasti.")
        elif security_score >= 60:
            print("⚠️  HYVÄ, mutta parannettavaa vielä.")
        else:
            print("🚨 HEIKKO! Data integrity -järjestelmä tarvitsee parannusta.")
        
        print()
        print("Yksityiskohdat:")
        for test in self.test_results:
            icon = "✅" if test['success'] else "❌"
            print(f"  {icon} {test['test']}")

if __name__ == "__main__":
    tester = SecurityTester()
    tester.run_all_tests()
