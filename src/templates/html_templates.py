#!/usr/bin/env python3
"""
HTML-pohjat ja CSS-tyylit profiilisivuille
"""
import json
from datetime import datetime
from typing import Dict

# Esimääritellyt väriteemat eri puolueille
PARTY_COLOR_THEMES = {
    "default": {
        "primary": "#2c3e50",
        "secondary": "#3498db", 
        "accent": "#e74c3c",
        "background": "#ecf0f1"
    },
    "blue_theme": {
        "primary": "#1a5276",
        "secondary": "#3498db",
        "accent": "#2980b9", 
        "background": "#ebf5fb"
    },
    "green_theme": {
        "primary": "#186a3b",
        "secondary": "#27ae60",
        "accent": "#229954",
        "background": "#eafaf1"
    },
    "red_theme": {
        "primary": "#922b21", 
        "secondary": "#e74c3c",
        "accent": "#cb4335",
        "background": "#fdedec"
    },
    "purple_theme": {
        "primary": "#4a235a",
        "secondary": "#8e44ad",
        "accent": "#7d3c98",
        "background": "#f4ecf7"
    }
}

class HTMLTemplates:
    """HTML-pohjat profiilisivuille"""
    
    @staticmethod
    def get_base_css() -> str:
        """Hae perus-CSS tyylit"""
        return """
        /* Perustyylit */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: var(--background-color, #f8f9fa);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
        .profile-header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 2rem 0;
            text-align: center;
        }
        
        .profile-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .profile-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 1rem;
        }
        
        .profile-meta {
            font-size: 0.9rem;
            opacity: 0.7;
        }
        
        /* Navigation */
        .profile-nav {
            background-color: var(--primary-color);
            padding: 1rem 0;
        }
        
        .nav-links {
            list-style: none;
            display: flex;
            justify-content: center;
            gap: 2rem;
        }
        
        .nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        
        .nav-links a:hover {
            background-color: var(--accent-color);
        }
        
        /* Content */
        .profile-content {
            padding: 2rem 0;
        }
        
        .section {
            margin-bottom: 3rem;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: var(--primary-color);
            margin-bottom: 1rem;
            border-bottom: 2px solid var(--secondary-color);
            padding-bottom: 0.5rem;
        }
        
        /* Color swatches */
        .color-swatches {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .color-swatch {
            padding: 0.5rem 1rem;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        
        /* Members grid */
        .members-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .member-card {
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            text-align: center;
        }
        
        .member-name {
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .member-domain {
            color: #666;
            font-size: 0.9rem;
        }
        
        /* Answers grid */
        .answers-grid {
            display: grid;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .answer-item {
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            border-left: 4px solid var(--accent-color);
        }
        
        .answer-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .answer-question {
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .answer-explanation {
            color: #666;
            font-style: italic;
            margin-bottom: 0.5rem;
        }
        
        .confidence {
            font-size: 0.9rem;
            color: #888;
        }
        
        /* Data links */
        .data-links {
            margin-top: 1rem;
        }
        
        .link-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .data-link {
            display: block;
            padding: 1rem;
            background: var(--secondary-color);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            text-align: center;
            transition: background-color 0.3s;
        }
        
        .data-link:hover {
            background: var(--accent-color);
        }
        
        /* Footer */
        .profile-footer {
            background-color: var(--primary-color);
            color: white;
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        .profile-footer p {
            margin-bottom: 0.5rem;
        }
        
        /* Utility classes */
        .text-center {
            text-align: center;
        }
        
        .mt-2 {
            margin-top: 2rem;
        }
        """
    
    @staticmethod
    def generate_party_html(party_data: Dict, colors: Dict, page_id: str, 
                          candidate_cards: str, ipfs_cids: Dict, election_id: str) -> str:
        """Generoi HTML puolueprofiilille"""
        return f"""<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{party_data['name']['fi']} - Jumaltenvaalit 2026</title>
    <meta name="profile-id" content="{page_id}">
    <meta name="profile-type" content="party">
    <meta name="party-id" content="{party_data['party_id']}">
    <meta name="election-id" content="{election_id}">
    <meta name="generated-at" content="{datetime.now().isoformat()}">
    <style>
        /* Perustyylit */
        {HTMLTemplates.get_base_css()}
        
        /* Puoluekohtaiset värit */
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
            <h1>{party_data['name']['fi']}</h1>
            <p class="profile-subtitle">{party_data['description']['fi']}</p>
            <div class="profile-meta">
                <small>Profiili ID: {page_id} | Puolue ID: {party_data['party_id']}</small>
            </div>
        </div>
    </header>

    <nav class="profile-nav">
        <div class="container">
            <ul class="nav-links">
                <li><a href="#tietoa">Tietoa Puolueesta</a></li>
                <li><a href="#ehdokkaat">Ehdokkaat</a></li>
                <li><a href="#data">Data & IPFS</a></li>
                <li><a href="#yhteys">Yhteystiedot</a></li>
            </ul>
        </div>
    </nav>

    <main class="profile-content">
        <div class="container">
            <!-- Tietoa Puolueesta -->
            <section id="tietoa" class="section">
                <h2>Tietoa Puolueesta</h2>
                <p><strong>Perustamisvuosi:</strong> {party_data['metadata'].get('founding_year', 'Ei määritelty')}</p>
                <p><strong>Sähköposti:</strong> {party_data['metadata'].get('contact_email', 'Ei määritelty')}</p>
                <p><strong>Verkkosivu:</strong> {party_data['metadata'].get('website', 'Ei määritelty')}</p>
                
                <div class="color-swatches mt-2">
                    <div class="color-swatch" style="background-color: {colors['primary']}">Pääväri</div>
                    <div class="color-swatch" style="background-color: {colors['secondary']}">Toissijainen</div>
                    <div class="color-swatch" style="background-color: {colors['accent']}">Korostus</div>
                </div>
            </section>

            <!-- Ehdokkaat -->
            <section id="ehdokkaat" class="section">
                <h2>Ehdokkaat</h2>
                <div class="members-grid">
                    {candidate_cards}
                </div>
            </section>

            <!-- Data & IPFS -->
            <section id="data" class="section">
                <h2>Data & IPFS Linkit</h2>
                <div class="data-links">
                    <h3>Hajautetut Resurssit</h3>
                    
                    <div class="link-grid">
                        <a href="https://ipfs.io/ipfs/{ipfs_cids.get('parties', '')}" class="data-link" target="_blank">
                            📄 Puolueet IPFS:ässä
                        </a>
                        <a href="https://ipfs.io/ipfs/{ipfs_cids.get('candidates', '')}" class="data-link" target="_blank">
                            👑 Ehdokkaat IPFS:ässä
                        </a>
                        <a href="https://ipfs.io/ipfs/{ipfs_cids.get('questions', '')}" class="data-link" target="_blank">
                            ❓ Kysymykset IPFS:ässä
                        </a>
                    </div>
                    
                    <h3>Paikalliset Resurssit</h3>
                    <ul>
                        <li><strong>Profiili ID:</strong> {page_id}</li>
                        <li><strong>Puolue ID:</strong> {party_data['party_id']}</li>
                        <li><strong>Vaali ID:</strong> {election_id}</li>
                        <li><strong>Generoitu:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')}</li>
                    </ul>
                </div>
            </section>

            <!-- Yhteys -->
            <section id="yhteys" class="section">
                <h2>Yhteystiedot</h2>
                <p>Ota meihin yhteyttä, jos haluat lisätietoja puolueestamme tai ehdottaa yhteistyötä!</p>
            </section>
        </div>
    </main>

    <footer class="profile-footer">
        <div class="container">
            <p>&copy; 2026 {party_data['name']['fi']} - Jumaltenvaalit</p>
            <p>Sivu generoitu {datetime.now().strftime('%d.%m.%Y %H:%M')} | Profiili ID: {page_id}</p>
            <p>📦 Tämä sivu on tallennettu hajautettuun IPFS-verkkoon</p>
        </div>
    </footer>

    <!-- Piilotettu data JSON-muodossa -->
    <script type="application/json" id="party-data">
        {json.dumps({
            "profile_id": page_id,
            "profile_type": "party",
            "party_data": party_data,
            "generated_at": datetime.now().isoformat(),
            "election_id": election_id,
            "color_theme": colors,
            "ipfs_cids": ipfs_cids
        }, ensure_ascii=False)}
    </script>
</body>
</html>"""
    
    @staticmethod
    def generate_candidate_html(candidate_data: Dict, party_data: Dict, colors: Dict, 
                              page_id: str, answer_cards: str, ipfs_cids: Dict, election_id: str) -> str:
        """Generoi HTML ehdokasprofiilille"""
        return f"""<!DOCTYPE html>
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
        {HTMLTemplates.get_base_css()}
        
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
                <h2>Vastaukset Kysymyksiin</h2>
                <div class="answers-grid">
                    {answer_cards}
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
                        <li><strong>Vastauksia:</strong> {len(candidate_data.get('answers', []))}</li>
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
            "answer_count": len(candidate_data.get('answers', [])),
            "ipfs_cids": ipfs_cids
        }, ensure_ascii=False)}
    </script>
</body>
</html>"""
