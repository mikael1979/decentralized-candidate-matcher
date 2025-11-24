# scripts/template_usage_guide.py
#!/usr/bin/env python3
"""
Template-käyttöohjeet kehittäjille
"""
print("""
🎯 TEMPLATE-KÄYTTÖOHJEET
=========================

1. 📁 TEMPLATE-RAKENNE:
   base_templates/
   ├── questions/           # Kysymysten templatet
   │   ├── questions.base.json
   │   └── active_questions.base.json
   ├── candidates/          # Ehdokkaiden templatet  
   │   ├── candidates.base.json
   │   └── candidate_profiles.base.json
   ├── governance/          # Hallinto & puolueet
   │   └── parties.base.json
   ├── elections/           # Vaalikonfiguraatiot
   │   ├── elections_list.base.json
   │   └── install_config.base.json
   ├── core/                # Ydindata
   │   └── meta.base.json
   └── system/              # Järjestelmätason data
       └── system_chain.base.json

2. 🔧 UUDET TEMPLATE-Ominaisuudet v2.1.0:
   ✅ Standardoitu metadata
   ✅ Placeholder-ohjeet 3 kielellä
   ✅ Timestamp-kentät
   ✅ Minimal working examples
   ✅ Schema-type määritelty

3. 🚀 Template-generointi:
   python src/cli/template_manager.py generate --election Jumaltenvaalit2026 --template-type questions

4. 📊 Template-laadun tarkistus:
   python scripts/final_template_report.py

5. 🔄 Template-päivitys:
   python scripts/enhance_all_templates.py
""")
