# src/templates/candidate_templates.py (LAAJENNETTU)
#!/usr/bin/env python3
"""
Ehdokasprofiilien HTML-pohjat
"""
import json
from datetime import datetime
from typing import Dict

from .css_generator import CSSGenerator, PARTY_COLOR_THEMES


class CandidateTemplates:
    """Ehdokasprofiilien HTML-pohjat"""
    
    @staticmethod
    def generate_candidate_html(*args, **kwargs) -> str:
        """Generoi HTML-profiilisivun ehdokkaalle"""
        candidate_data = args[0] if args else kwargs.get('candidate_data', {})
        party_data = args[1] if len(args) > 1 else kwargs.get('party_data')
        colors = args[2] if len(args) > 2 else kwargs.get('colors', PARTY_COLOR_THEMES["default"])
        election_id = args[3] if len(args) > 3 else kwargs.get('election_id', "Jumaltenvaalit2026")
        questions = args[4] if len(args) > 4 else kwargs.get('questions')
        ipfs_cids = args[5] if len(args) > 5 else kwargs.get('ipfs_cids')
        
        answers = candidate_data.get("answers", [])
        page_id = f"candidate_{candidate_data['candidate_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Käytä annettuja IPFS-CID:itä tai hae ne
        if ipfs_cids is None:
            ipfs_cids = CandidateTemplates._get_ipfs_cids()
        
        # Täydellinen HTML-generointi koodi
        html = f"""
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{candidate_data['basic_info']['name']['fi']} - Jumaltenvaalit 2026</title>
    <meta name="profile-id" content="{page_id}">
    <meta name="profile-type" content="candidate">
    <meta name="candidate-id" content="{candidate_data['candidate_id']}">
    <meta name="election-id" content="{election_id}">
    <meta name="generated-at" content="{datetime.now().isoformat()}">
    <style>
        {CSSGenerator.get_base_css()}
        
        :root {{
            --primary-color: {colors['primary']};
            --secondary-color: {colors['secondary']};
            --accent-color: {colors['accent']};
            --background-color: {colors['background']};
        }}
    </style>
</head>
<body>
    <header class="profile-header">
        <div class="container">
            <h1>{candidate_data['basic_info']['name']['fi']}</h1>
            <p class="profile-subtitle">{candidate_data['basic_info'].get('party', 'Sitoutumaton')}</p>
            {f'<p class="profile-subtitle">{party_data["name"]["fi"]}</p>' if party_data else ''}
            <div class="profile-meta">
                <small>Profiili ID: {page_id} | Ehdokas ID: {candidate_data['candidate_id']}</small>
            </div>
        </div>
    </header>

    <nav class="profile-nav">
        <div class="container">
            <ul class="nav-links">
                <li><a href="#tietoa">Tietoa Ehdokkaasta</a></li>
                <li><a href="#vastaukset">Vastaukset</a></li>
                <li><a href="#data">Data & IPFS</a></li>
                <li><a href="#yhteys">Yhteys</a></li>
            </ul>
        </div>
    </nav>

    <main class="profile-content">
        <div class="container">
            <!-- Tietoa Ehdokkaasta -->
            <section id="tietoa" class="section">
                <h2>Tietoa Ehdokkaasta</h2>
                <p><strong>Puolue:</strong> {candidate_data['basic_info'].get('party', 'Sitoutumaton')}</p>
                <p><strong>Alue:</strong> {candidate_data['basic_info'].get('domain', 'Ei määritelty')}</p>
            </section>

            <!-- Vastaukset -->
            <section id="vastaukset" class="section">
                <h2>Vastaukset Kysymyksiin ({len(answers)})</h2>
                <div class="answers-grid">
                    {CandidateTemplates._generate_answer_cards(answers)}
                </div>
            </section>

            <!-- Data & IPFS -->
            <section id="data" class="section">
                <h2>Data & IPFS Linkit</h2>
                <div class="data-links">
                    <h3>Hajautetut Resurssit</h3>
                    
                    <div class="link-grid">
                        <a href="https://ipfs.io/ipfs/{ipfs_cids.get('candidates', '')}" class="data-link" target="_blank">
                            👑 Ehdokkaat IPFS:ässä
                        </a>
                        <a href="https://ipfs.io/ipfs/{ipfs_cids.get('parties', '')}" class="data-link" target="_blank">
                            📄 Puolueet IPFS:ässä
                        </a>
                        <a href="https://ipfs.io/ipfs/{ipfs_cids.get('questions', '')}" class="data-link" target="_blank">
                            ❓ Kysymykset IPFS:ässä
                        </a>
                    </div>
                    
                    <h3>Ehdokkaan Tiedot</h3>
                    <ul>
                        <li><strong>Profiili ID:</strong> {page_id}</li>
                        <li><strong>Ehdokas ID:</strong> {candidate_data['candidate_id']}</li>
                        <li><strong>Vaali ID:</strong> {election_id}</li>
                        <li><strong>Generoitu:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')}</li>
                        <li><strong>Vastauksia:</strong> {len(answers)}</li>
                    </ul>
                </div>
            </section>
        </div>
    </main>

    <footer class="profile-footer">
        <div class="container">
            <p>&copy; 2026 {candidate_data['basic_info']['name']['fi']} - Jumaltenvaalit</p>
            <p>Sivu generoitu {datetime.now().strftime('%d.%m.%Y %H:%M')} | Profiili ID: {page_id}</p>
            <p>📦 Tämä sivu on tallennettu hajautettuun IPFS-verkkoon</p>
        </div>
    </footer>

    <!-- Piilotettu data JSON-muodossa -->
    <script type="application/json" id="candidate-data">
        {json.dumps({
            "profile_id": page_id,
            "profile_type": "candidate", 
            "candidate_data": candidate_data,
            "party_data": party_data,
            "generated_at": datetime.now().isoformat(),
            "election_id": election_id,
            "color_theme": colors,
            "answer_count": len(answers),
            "ipfs_cids": ipfs_cids
        }, ensure_ascii=False)}
    </script>
</body>
</html>
        """
        
        return html

    @staticmethod
    def _generate_answer_cards(answers: list) -> str:
        """Generoi vastauskortit"""
        if not answers:
            return '<p class="text-center">Ei vastauksia</p>'
        
        # Lataa kysymykset nimeä varten
        questions = CandidateTemplates._load_questions()
        question_map = {q["local_id"]: q["content"]["question"]["fi"] for q in questions}
        
        answer_cards = []
        for answer in answers:
            question_text = question_map.get(answer["question_id"], answer["question_id"])
            explanation = answer.get("explanation", {}).get("fi", "")
            confidence = answer.get("confidence", 3)
            
            card = f"""
            <div class="answer-item">
                <div class="answer-value">{answer['answer_value']}/5</div>
                <div class="answer-question">{question_text}</div>
                {f'<div class="answer-explanation">{explanation}</div>' if explanation else ''}
                <div class="confidence">Varmuus: {confidence}/5</div>
            </div>
            """
            answer_cards.append(card)
        
        return '\n'.join(answer_cards)

    @staticmethod
    def _load_questions() -> list:
        """Lataa kysymykset"""
        import json
        from pathlib import Path
        
        questions_file = Path("data/runtime/questions.json")
        if questions_file.exists():
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("questions", [])
        return []

    @staticmethod
    def _get_ipfs_cids() -> Dict:
        """Hae IPFS-CID:t datatiedostoille"""
        import json
        from pathlib import Path
        
        ipfs_sync_file = Path("data/runtime/ipfs_sync.json")
        if ipfs_sync_file.exists():
            with open(ipfs_sync_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("ipfs_cids", {})
        return {}
