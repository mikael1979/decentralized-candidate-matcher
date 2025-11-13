#!/usr/bin/env python3
"""
Staattisen HTML-profiilisivujen generaattori puolueille ja ehdokkaille
IPFS-tallennuksella
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

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

class HTMLProfileGenerator:
    def __init__(self, election_id: str = "Jumaltenvaalit2026"):
        self.election_id = election_id
        self.output_dir = Path("output/profiles")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = Path("data/runtime/profiles_metadata.json")
        
        # IPFS-client
        try:
            from src.core.ipfs_client import IPFSClient
            self.ipfs_client = IPFSClient.get_client(election_id)
            self.ipfs_available = True
        except Exception:
            self.ipfs_available = False
            print("🔶 IPFS ei saatavilla, käytetään paikallista tallennusta")
    
    def generate_and_publish_party_profile(self, party_data: Dict, custom_colors: Dict = None) -> Dict:
        """Generoi ja julkaise puolueen profiili IPFS:ään"""
        
        # 1. Generoi HTML
        html_content = self.generate_party_profile(party_data, custom_colors)
        
        # 2. Tallenna paikallisesti
        filename = f"party_{party_data['party_id']}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 3. Julkaise IPFS:ään
        ipfs_cid = None
        if self.ipfs_available:
            try:
                # Julkaise HTML-sivu IPFS:ään
                profile_data = {
                    "content": html_content,
                    "metadata": {
                        "type": "party_profile",
                        "party_id": party_data["party_id"],
                        "election_id": self.election_id,
                        "generated_at": datetime.now().isoformat(),
                        "filename": filename
                    }
                }
                ipfs_cid = self.ipfs_client.publish_election_data("party_profile", profile_data)
                print(f"🌐 Puolueen profiili julkaistu IPFS:ään: {ipfs_cid}")
            except Exception as e:
                print(f"❌ IPFS-julkaisu epäonnistui: {e}")
                ipfs_cid = f"mock_cid_party_{party_data['party_id']}"
        else:
            ipfs_cid = f"mock_cid_party_{party_data['party_id']}"
        
        # 4. Päivitä metadata
        profile_id = f"party_{party_data['party_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metadata = {
            "profile_id": profile_id,
            "entity_id": party_data["party_id"],
            "entity_type": "party",
            "entity_name": party_data["name"]["fi"],
            "filepath": str(filepath),
            "filename": filename,
            "ipfs_cid": ipfs_cid,
            "ipfs_gateway_url": f"https://ipfs.io/ipfs/{ipfs_cid}" if ipfs_cid and not ipfs_cid.startswith("mock_") else None,
            "generated_at": datetime.now().isoformat(),
            "election_id": self.election_id,
            "color_theme": custom_colors or PARTY_COLOR_THEMES["default"]
        }
        
        self._update_profile_metadata(metadata)
        
        print(f"✅ Puolueen profiili tallennettu: {filepath}")
        if ipfs_cid:
            print(f"🌐 IPFS-CID: {ipfs_cid}")
        
        return metadata
    
    def generate_and_publish_candidate_profile(self, candidate_data: Dict, party_data: Dict = None, 
                                             custom_colors: Dict = None) -> Dict:
        """Generoi ja julkaise ehdokkaan profiili IPFS:ään"""
        
        # 1. Generoi HTML
        html_content = self.generate_candidate_profile(candidate_data, party_data, custom_colors)
        
        # 2. Tallenna paikallisesti
        filename = f"candidate_{candidate_data['candidate_id']}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 3. Julkaise IPFS:ään
        ipfs_cid = None
        if self.ipfs_available:
            try:
                profile_data = {
                    "content": html_content,
                    "metadata": {
                        "type": "candidate_profile",
                        "candidate_id": candidate_data["candidate_id"],
                        "party_id": candidate_data["basic_info"].get("party"),
                        "election_id": self.election_id,
                        "generated_at": datetime.now().isoformat(),
                        "filename": filename
                    }
                }
                ipfs_cid = self.ipfs_client.publish_election_data("candidate_profile", profile_data)
                print(f"🌐 Ehdokkaan profiili julkaistu IPFS:ään: {ipfs_cid}")
            except Exception as e:
                print(f"❌ IPFS-julkaisu epäonnistui: {e}")
                ipfs_cid = f"mock_cid_candidate_{candidate_data['candidate_id']}"
        else:
            ipfs_cid = f"mock_cid_candidate_{candidate_data['candidate_id']}"
        
        # 4. Päivitä metadata
        profile_id = f"candidate_{candidate_data['candidate_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metadata = {
            "profile_id": profile_id,
            "entity_id": candidate_data["candidate_id"],
            "entity_type": "candidate",
            "entity_name": candidate_data["basic_info"]["name"]["fi"],
            "filepath": str(filepath),
            "filename": filename,
            "ipfs_cid": ipfs_cid,
            "ipfs_gateway_url": f"https://ipfs.io/ipfs/{ipfs_cid}" if ipfs_cid and not ipfs_cid.startswith("mock_") else None,
            "generated_at": datetime.now().isoformat(),
            "election_id": self.election_id,
            "party_id": candidate_data["basic_info"].get("party"),
            "color_theme": custom_colors or PARTY_COLOR_THEMES["default"]
        }
        
        self._update_profile_metadata(metadata)
        
        print(f"✅ Ehdokkaan profiili tallennettu: {filepath}")
        if ipfs_cid:
            print(f"🌐 IPFS-CID: {ipfs_cid}")
        
        return metadata

    def generate_party_profile(self, party_data: Dict, custom_colors: Dict = None) -> str:
        """Generoi HTML-profiilisivun puolueelle"""
        
        # Oletusvärit jos custom_colors ei annettu
        colors = custom_colors or PARTY_COLOR_THEMES["default"]
        
        # Hae puolueen ehdokkaat
        candidates = self._get_party_candidates(party_data.get("party_id"))
        
        # Generoi sivulle uniikki ID
        page_id = f"party_{party_data['party_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Hae IPFS-CID:t datatiedostoille
        ipfs_cids = self._get_ipfs_cids()
        
        html = f"""
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{party_data['name']['fi']} - Jumaltenvaalit 2026</title>
    <meta name="profile-id" content="{page_id}">
    <meta name="profile-type" content="party">
    <meta name="party-id" content="{party_data['party_id']}">
    <meta name="election-id" content="{self.election_id}">
    <meta name="generated-at" content="{datetime.now().isoformat()}">
    <style>
        /* Perustyylit */
        {self._get_base_css()}
        
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
                <h2>Ehdokkaat ({len(candidates)})</h2>
                <div class="members-grid">
                    {self._generate_candidate_cards(candidates)}
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
                        <li><strong>Vaali ID:</strong> {self.election_id}</li>
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
            "election_id": self.election_id,
            "color_theme": colors,
            "candidate_count": len(candidates),
            "ipfs_cids": ipfs_cids
        }, ensure_ascii=False)}
    </script>
</body>
</html>
        """
        
        return html
    
    def generate_candidate_profile(self, candidate_data: Dict, party_data: Dict = None, 
                                 custom_colors: Dict = None) -> str:
        """Generoi HTML-profiilisivun ehdokkaalle"""
        
        colors = custom_colors or PARTY_COLOR_THEMES["default"]
        answers = candidate_data.get("answers", [])
        page_id = f"candidate_{candidate_data['candidate_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ipfs_cids = self._get_ipfs_cids()
        
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
    <meta name="election-id" content="{self.election_id}">
    <meta name="generated-at" content="{datetime.now().isoformat()}">
    <style>
        {self._get_base_css()}
        
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
                    {self._generate_answer_cards(answers)}
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
                        <li><strong>Vaali ID:</strong> {self.election_id}</li>
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
            "election_id": self.election_id,
            "color_theme": colors,
            "answer_count": len(answers),
            "ipfs_cids": ipfs_cids
        }, ensure_ascii=False)}
    </script>
</body>
</html>
        """
        
        return html

    def _get_ipfs_cids(self) -> Dict:
        """Hae IPFS-CID:t datatiedostoille"""
        ipfs_sync_file = Path("data/runtime/ipfs_sync.json")
        if ipfs_sync_file.exists():
            with open(ipfs_sync_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("ipfs_cids", {})
        return {}
    
    def _update_profile_metadata(self, profile_metadata: Dict):
        """Päivitä profiilien metadatatiedosto"""
        metadata = self._load_metadata()
        
        profile_key = f"{profile_metadata['entity_type']}_{profile_metadata['entity_id']}"
        metadata["profiles"][profile_key] = profile_metadata
        metadata["last_updated"] = datetime.now().isoformat()
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _load_metadata(self) -> Dict:
        """Lataa profiilien metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Alusta uusi metadata
        return {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "election_id": self.election_id,
                "description": "Profiilisivujen metadata ja linkit"
            },
            "profiles": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def get_base_json(self) -> Dict:
        """Hae base.json data kaikista profiileista ja linkeistä"""
        metadata = self._load_metadata()
        
        # Lataa IPFS-synkronointitiedot
        ipfs_sync_file = Path("data/runtime/ipfs_sync.json")
        ipfs_cids = {}
        if ipfs_sync_file.exists():
            with open(ipfs_sync_file, 'r', encoding='utf-8') as f:
                ipfs_data = json.load(f)
                ipfs_cids = ipfs_data.get("ipfs_cids", {})
        
        base_data = {
            "metadata": {
                "election_id": self.election_id,
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "description": "Jumaltenvaalit 2026 - Base data kaikista resursseista"
            },
            "links": {
                "parties_json": "/data/runtime/parties.json",
                "candidates_json": "/data/runtime/candidates.json", 
                "questions_json": "/data/runtime/questions.json",
                "meta_json": "/data/runtime/meta.json",
                "ipfs_sync_json": "/data/runtime/ipfs_sync.json",
                "profiles_metadata": "/data/runtime/profiles_metadata.json"
            },
            "ipfs_cids": ipfs_cids,
            "profiles": metadata["profiles"],
            "statistics": {
                "total_profiles": len(metadata["profiles"]),
                "party_profiles": len([p for p in metadata["profiles"].values() if p["entity_type"] == "party"]),
                "candidate_profiles": len([p for p in metadata["profiles"].values() if p["entity_type"] == "candidate"])
            }
        }
        
        return base_data
    
    def save_base_json(self) -> str:
        """Tallenna base.json tiedosto"""
        base_data = self.get_base_json()
        base_file = Path("output/base.json")
        
        with open(base_file, 'w', encoding='utf-8') as f:
            json.dump(base_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ base.json tallennettu: {base_file}")
        return str(base_file)

    def _get_base_css(self) -> str:
        """Hae perus-CSS tyylit"""
        css_file = Path("src/templates/base_template.css")
        if css_file.exists():
            with open(css_file, 'r', encoding='utf-8') as f:
                return f.read()
        return "/* CSS tyylit */"
    
    def _get_party_candidates(self, party_id: str) -> List[Dict]:
        """Hae puolueen ehdokkaat"""
        candidates_file = Path("data/runtime/candidates.json")
        if candidates_file.exists():
            with open(candidates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [c for c in data.get("candidates", []) 
                       if c["basic_info"].get("party") == party_id]
        return []
    
    def _generate_candidate_cards(self, candidates: List[Dict]) -> str:
        """Generoi ehdokaskortit"""
        if not candidates:
            return '<p class="text-center">Ei ehdokkaita</p>'
        
        cards = []
        for candidate in candidates:
            card = f"""
            <div class="member-card">
                <div class="member-name">{candidate['basic_info']['name']['fi']}</div>
                <div class="member-domain">{candidate['basic_info'].get('domain', 'Ei aluetta')}</div>
                <div class="member-answers">{len(candidate.get('answers', []))} vastausta</div>
                <a href="/output/profiles/candidate_{candidate['candidate_id']}.html" class="data-link" style="margin-top: 0.5rem; padding: 0.5rem;">
                    👤 Näytä profiili
                </a>
            </div>
            """
            cards.append(card)
        
        return '\n'.join(cards)
    
    def _generate_answer_cards(self, answers: List[Dict]) -> str:
        """Generoi vastauskortit"""
        if not answers:
            return '<p class="text-center">Ei vastauksia</p>'
        
        # Lataa kysymykset nimeä varten
        questions = self._load_questions()
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
    
    def _load_questions(self) -> List[Dict]:
        """Lataa kysymykset"""
        questions_file = Path("data/runtime/questions.json")
        if questions_file.exists():
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("questions", [])
        return []
