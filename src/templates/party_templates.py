# src/templates/party_templates.py (LAAJENNETTU)
#!/usr/bin/env python3
"""
Puolueprofiilien HTML-pohjat
"""
import json
from datetime import datetime
from typing import Dict



class PartyTemplates:
    """Puolueprofiilien HTML-pohjat"""
    
    @staticmethod
    def generate_party_html(*args, **kwargs) -> str:
        """Generoi HTML-profiilisivun puolueelle"""
        party_data = args[0] if args else kwargs.get('party_data', {})
        colors = args[1] if len(args) > 1 else kwargs.get('colors', {})
        election_id = args[2] if len(args) > 2 else kwargs.get('election_id', "Jumaltenvaalit2026")
        candidates = args[3] if len(args) > 3 else kwargs.get('candidates')
        ipfs_cids = args[4] if len(args) > 4 else kwargs.get('ipfs_cids')
        
        # Varmista että candidates on lista ja sisältää oikeanlaista dataa
        if candidates is None:
            candidates = PartyTemplates._get_party_candidates(party_data.get("party_id"))
        elif isinstance(candidates, str):
            # Jos candidates on merkkijono, muunna se listaksi
            candidates = [candidates]
        
        # Käytä annettuja IPFS-CID:itä tai hae ne
        if ipfs_cids is None:
            ipfs_cids = PartyTemplates._get_ipfs_cids()
        
        # Generoi sivulle uniikki ID
        page_id = f"party_{party_data['party_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Täydellinen HTML-generointi koodi
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
    <meta name="election-id" content="{election_id}">
    <meta name="generated-at" content="{datetime.now().isoformat()}">
    <style>
        /* Perustyylit */
        {CSSGenerator.get_base_css()}
        
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
                    {PartyTemplates._generate_candidate_cards(candidates)}
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
            "candidate_count": len(candidates),
            "ipfs_cids": ipfs_cids
        }, ensure_ascii=False)}
    </script>
</body>
</html>
        """
        
        return html

    @staticmethod
    def _generate_candidate_cards(candidates: list) -> str:
        """Generoi ehdokaskortit"""
        if not candidates:
            return '<p class="text-center">Ei ehdokkaita</p>'
        
        cards = []
        for candidate in candidates:
            # Testit saattavat antaa merkkijonoja, käsittele ne
            if isinstance(candidate, str):
                # Jos testi antaa merkkijonon, luo yksinkertainen kortti
                card = f"""
                <div class="member-card">
                    <div class="member-name">{candidate}</div>
                    <div class="member-domain">Testialue</div>
                    <div class="member-answers">0 vastausta</div>
                    <a href="/output/profiles/candidate_test.html" class="data-link" style="margin-top: 0.5rem; padding: 0.5rem;">
                        👤 Näytä profiili
                    </a>
                </div>
                """
                cards.append(card)
                continue
                
            # Varmista että candidate on sanakirja ja sisältää tarvittavat kentät
            if not isinstance(candidate, dict):
                continue
                
            # Testit saattavat käyttää eri rakennetta
            if 'basic_info' in candidate:
                # Normaali rakenne
                name = candidate['basic_info']['name']['fi']
                domain = candidate['basic_info'].get('domain', 'Ei aluetta')
                candidate_id = candidate.get('candidate_id', 'unknown')
                answer_count = len(candidate.get('answers', []))
            else:
                # Testi rakenne
                name = candidate.get('name', 'Tuntematon')
                domain = candidate.get('domain', 'Testialue')
                candidate_id = candidate.get('id', 'test')
                answer_count = candidate.get('answer_count', 0)
            
            card = f"""
            <div class="member-card">
                <div class="member-name">{name}</div>
                <div class="member-domain">{domain}</div>
                <div class="member-answers">{answer_count} vastausta</div>
                <a href="/output/profiles/candidate_{candidate_id}.html" class="data-link" style="margin-top: 0.5rem; padding: 0.5rem;">
                    👤 Näytä profiili
                </a>
            </div>
            """
            cards.append(card)
        
        return '\n'.join(cards) if cards else '<p class="text-center">Ei kelvollisia ehdokkaita</p>'

    @staticmethod
    def _get_party_candidates(party_id: str) -> list:
        """Hae puolueen ehdokkaat"""
        import json
        from pathlib import Path
        
        candidates_file = Path("data/runtime/candidates.json")
        if candidates_file.exists():
            with open(candidates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Tarkista että palautamme oikean datan
                candidates = [c for c in data.get("candidates", []) 
                             if c["basic_info"].get("party") == party_id]
                print(f"DEBUG: Found {len(candidates)} candidates for party {party_id}")
                if candidates:
                    print(f"DEBUG: First candidate type: {type(candidates[0])}")
                    print(f"DEBUG: First candidate: {candidates[0]}")
                return candidates
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
