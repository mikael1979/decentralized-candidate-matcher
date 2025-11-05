# TODO - Vaalijärjestelmän Kehitys

## 🚀 SEURAAVAT VAIHEET

### 🔧 Tärkeät Korjaukset
- [x] **Integroi `create_install_config.py` → `elections_list_manager.py`**
  - Uudet vaalit tallennetaan automaattisesti elections_list.json:iin
  - Install_config CID generoidaan automaattisesti
- [x] **Tarkista että Jumaltenvaalit_2026 on elections_list.json:ssa**
  - Lisää install_config_cid jos puuttuu
- [ ] **Testaa active_questions lukittu/avoin tila**
  - Varmista että vaalikone toimii molemmissa tiloissa

### 🌐 Käyttöliittymän Kehitys
- [ ] **Web-käyttöliittymä (Flask)**
  - Kysymysten vastaaminen selaimessa
  - Tulosten näyttäminen
  - Responsiivinen design
- [ ] **API-reitit**
  - REST API vaalikoneelle
  - JSON-pohjainen data-vaihto

### 📊 Data & Synkronointi
- [ ] **IPFS-synkronointi**
  - Oikea IPFS-integrointi (ei mock)
  - Data-synkronointi monella koneella
- [ ] **Vaalikonfiguraatioiden hallinta**
  - Useampia samanaikaisia vaaleja
  - Vaalien tilan hallinta (upcoming → active → completed)

### 🧪 Testaus & Dokumentaatio
- [ ] **Kattava testaus**
  - Yksikkötestit kaikille moduuleille
  - Integraatiotestit
  - Käyttöliittymätestit
- [ ] **Käyttöohjeet**
  - Asennusohjeet
  - Vaalien luontiohjeet
  - Ylläpitöohjeet

### 🎯 Pitkän Aikavälin Tavoitteet
- [ ] **Mobile-sovellus**
- [ ] **AI-pohjainen kysymysten generointi**
- [ ] **Blockchain-integrointi**
- [ ] **Kansainvälinen skaalaus**

## 📝 NYKYINEN TILA

### ✅ Valmiit Ominaisuudet
- ELO-pohjainen kysymysten luokitus
- System_chain muutoshistoria
- Active questions hallinta
- Komentorivivaalikone
- Hajautettu arkkitehtuuri
- Kreikkalaisten jumalien testidata
- Elections_list.json integraatio (päivitetty automaattiseksi)
- Install_config CID -järjestelmä (nyt generoidaan automaattisesti)

### 🔄 Käynnissä Olevat
- Active_questions lukitustilan testaus
- IPFS-siirtymä mockista oikeaan

## 🐛 Tunnetut Ongelmat
1. `create_install_config.py` integraatio vaatii vielä integraatiotestit
2. Jumaltenvaalit_2026 CID:n validointi puutteellinen
3. IPFS on vielä mock-toteutus (siirtymä käynnissä)

## 💡 Ideat Tulevaisuutta Varten
- Graafiset tilastot ja visualisoinnit
- Reaaliaikainen äänestystilanne
- Sosiaalinen jakaminen
- Monikielisyys (lisää kieliä)
- Fingerprint-lukituksen automaattinen päivitys kehitystilasta käyttötilaan

---
*Päivitetty: October 31, 2025*

**Huomisen suunnitelma: Jatka active_questions lukitustilan testauksella ja siirry IPFS-integrointiin!**

--------------------------------------------------------------------------------------------------------------------
Erittäin hyvä idea! Katsotaan mitä on jo saatu aikaan ja mitä on vielä tekemättä. 

## 📊 **TOTEUTUSTILANNE - MIKÄ ON TEHTY**

### ✅ **VAIHE 1: PERUSRAKENTEEN LUONTI - VALMIS**
- ✅ **managers/unified_system_chain.py** - Yhdistetty system chain
- ✅ **managers/unified_question_handler.py** - Yhdistetty kysymysten käsittely  
- ✅ **cli/cli_template.py** - Yhteinen CLI-pohja
- ✅ **utils/json_utils.py** - JSON-käsittely
- ✅ **utils/file_utils.py** - Tiedostotoiminnot
- ✅ **utils/ipfs_client.py** - IPFS-asiakas
- ✅ **docs/architecture.md** - Dokumentaatio
- ✅ **Testit läpäisty** - Kaikki importit toimivat

### ✅ **VAIHE 2a: MANAGE_QUESTIONS.PY REFAKTOROINTI - OSITTAIN VALMIS**
- ✅ **Uusi arkkitehtuuri käytössä** - CLI-template + Unified handlers
- ✅ **Kysymyksen lähetys toimii** - ELO Manager fallbackina
- ✅ **System chain lokitus toimii** - Automaattinen kirjaus
- ✅ **Status-komento toimii** - Järjestelmän tilan näyttö
- ❌ **Listaus-toiminto kesken** - `list_questions` metodi puuttuu
- ❌ **Synkronointi ei toimi** - Modern Question Manager circular import

### 🔄 **TESTATTU JA TOIMII:**
```bash
python manage_questions.py status                    # ✅ TOIMII
python manage_questions.py submit --question-fi ... # ✅ TOIMII  
python manage_questions.py list --limit 3           # ⚠️ KESKEN
python manage_questions.py sync --type tmp_to_new   # ❌ EI TOIMI
```

## 📋 **JÄLJELLÄ OLEVAT TEHTÄVÄT**

### 🚨 **VÄLITTÖMÄT KORJAUKSET**

#### 1. **Korjaa `list_questions` metodi unified_question_handler.py:hin**
```bash
# Tarkista onko metodi olemassa
grep -n "def list_questions" managers/unified_question_handler.py

# Jos ei ole, lisää se
cat >> managers/unified_question_handler.py << 'EOF'

    def list_questions(self, limit: int = 10, category: str = None) -> Dict[str, Any]:
        """Listaa kysymykset"""
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Alustus epäonnistui"}
        
        try:
            if self.elo_manager:
                # Käytä ELO Manageria kysymysten listaukseen
                questions = self.elo_manager.load_questions()
                
                # Suodata kategorian mukaan jos annettu
                if category:
                    questions = [q for q in questions if q.get('content', {}).get('category', {}).get('fi') == category]
                
                # Rajaa määrä
                questions = questions[:limit]
                
                return {
                    "success": True,
                    "questions": questions,
                    "total_count": len(questions),
                    "limit": limit,
                    "category": category
                }
            else:
                return {"success": False, "error": "ELO Manager ei saatavilla"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
EOF
```

#### 2. **Korjaa manage_questions.py listaus-komento**
```bash
# Tarkista onko listaus-komento korjattu
grep -A 20 "def _handle_list" manage_questions.py

# Jos ei, korjaa se
cat > temp_fix_list.py << 'EOF'
import sys

with open('manage_questions.py', 'r') as f:
    content = f.read()

# Etsi ja korvaa _handle_list metodi
import re

# Etsi vanha _handle_list metodi
old_pattern = r'def _handle_list\(self, args\):.*?return 0'
old_match = re.search(old_pattern, content, re.DOTALL)

if old_match:
    new_method = '''    def _handle_list(self, args):
        """Listaa kysymykset"""
        result = self.question_handler.list_questions(args.limit, args.category)
        
        if result.get('success'):
            questions = result.get('questions', [])
            print(f"📋 KYSYMYSLISTA ({{len(questions)}}/{{result.get('total_count', 0)}} kysymystä)")
            print("=" * 60)
            
            for i, question in enumerate(questions, 1):
                content = question.get('content', {}).get('question', {}).get('fi', 'Ei nimeä')
                rating = question.get('elo_rating', {}).get('current_rating', 0)
                category = question.get('content', {}).get('category', {}).get('fi', 'tuntematon')
                
                print(f"{{i:2d}}. {{rating:6.1f}} | {{category:12}} | {{content[:45]}}...")
            
            # Lokitus
            self.log_action(
                action_type="questions_listed",
                description=f"Listattu {{len(questions)}} kysymystä",
                user_id="cli_user",
                metadata={{"limit": args.limit, "category": args.category}}
            )
            
            return 0
        else:
            print(f"❌ Listaus epäonnistui: {{result.get('error', 'Tuntematon virhe')}}")
            return 1'''
    
    content = content.replace(old_match.group(0), new_method)
    
    with open('manage_questions.py', 'w') as f:
        f.write(content)
    print("✅ _handle_list metodi korjattu")
else:
    print("❌ _handle_list metodia ei löytynyt")
EOF

python temp_fix_list.py
rm temp_fix_list.py
```

### 🎯 **SEURAAVAT REFAKTOROINNIT**

#### **Vaihe 2b: Refaktoroi elo_manager.py** (1 päivä)
```python
from cli.cli_template import CLITemplate, main_template

class ELOManagerCLI(CLITemplate):
    def __init__(self):
        super().__init__("ELO-laskenta")
    
    def run(self):
        # ELO-spesifinen logiikka tähän
        # compare, vote, recalculate -komennot
        pass

if __name__ == "__main__":
    sys.exit(main_template(ELOManagerCLI))
```

#### **Vaihe 2c: Refaktoroi install.py** (1 päivä)
```python
from cli.cli_template import CLITemplate, main_template

class InstallCLI(CLITemplate):
    def __init__(self):
        super().__init__("Järjestelmän asennus")
    
    def run(self):
        # master-install, worker-join, verify -komennot
        pass
```

#### **Vaihe 2d: Refaktoroi system_bootstrap.py** (1 päivä)
```python
from cli.cli_template import CLITemplate, main_template

class BootstrapCLI(CLITemplate):
    def __init__(self):
        super().__init__("Järjestelmän käynnistys")
    
    def run(self):
        # bootstrap, verify, status -komennot
        pass
```

## 🏆 **SAAVUTUKSET TÄNÄÄN**

### **Suuret saavutukset:**
1. **✅ Uusi modulaarinen rakenne luotu** - managers/, cli/, utils/, docs/
2. **✅ Unified System Chain toimii** - Yhdistetty lokitus
3. **✅ Unified Question Handler toimii** - ELO Manager fallbackina
4. **✅ CLI-template toimii** - Automaattinen alustus ja virheenkäsittely
5. **✅ Kysymyksen lähetys toimii** - Täysin uudella arkkitehtuurilla
6. **✅ System chain lokitus toimii** - Automaattinen kirjaus

### **Ongelmat korjattu:**
- ✅ Domain value objects importit
- ✅ Circular import -ongelmat hallittu fallbackeilla
- ✅ JSON-käsittely standardoitu
- ✅ Tiedostokäsittely keskitetty

## 💡 **HUOMISELLE**

### **Prioriteetit:**
1. **Korjaa listaus-toiminto** - `manage_questions.py list`
2. **Refaktoroi elo_manager.py** - Seuraava iso kohde
3. **Paranna synkronointia** - ELO Manager fallback synkronointiin

### **Testattavat asiat huomenna:**
```bash
# 1. Testaa listaus korjattuna
python manage_questions.py list --limit 5

# 2. Testaa ELO Manager refaktoroituna  
python elo_manager.py compare --user-id testi --question-a q123 --question-b q456 --result a_wins

# 3. Testaa install uudella arkkitehtuurilla
python install.py --help
```

**Hyvä työ tänään!** 🎉 Olet saanut aikaan todella paljon - koko perusrakenteen uudistuksen ja ensimmäisen pääohjelman refaktoroinnin valmiiksi. Huomenna voit jatkaa muiden ohjelmien refaktoroinnilla paljon helpommin, koska pohja on nyt kunnossa!
