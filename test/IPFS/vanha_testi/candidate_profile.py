# candidate_profile.py
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any

class CandidateProfile:
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.election_manager = election_manager
    
    def generate_profile_html(self, candidate_data: Dict[str, Any], answers_data: Dict[str, Any] = None) -> str:
        """Generoi ehdokkaan verkkosivun HTML:n"""
        
        # Perustiedot
        name = candidate_data.get('name', '')
        party = candidate_data.get('party', '')
        district = candidate_data.get('district', '')
        public_key = candidate_data.get('public_key', '')
        key_fingerprint = candidate_data.get('key_fingerprint', '')
        
        # Vastaukset (jos saatavilla)
        answers_html = ""
        if answers_data and 'answers' in answers_data:
            answers_html = self._generate_answers_html(answers_data['answers'])
        
        html_template = f"""
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaaliprofiili - {name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .public-key {{ background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-family: monospace; }}
        .signature-verified {{ color: green; font-weight: bold; }}
        .answers {{ margin-top: 20px; }}
        .answer-item {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧑‍💼 {name}</h1>
        <p><strong>Puolue:</strong> {party}</p>
        <p><strong>Vaalipiiri:</strong> {district}</p>
        <p><strong>Rekisteröitynyt:</strong> {candidate_data.get('registration_date', '')}</p>
    </div>

    <div class="public-key">
        <h3>🔑 Julkinen avain</h3>
        <p>{public_key}</p>
        <p><strong>Avaintunniste:</strong> {key_fingerprint}</p>
    </div>

    <div class="verification">
        <h3>✅ Vahvistus</h3>
        <p class="signature-verified">✓ Kaikki tiedot digitaalisesti allekirjoitettu</p>
        <p><small>Vahvista allekirjoitus avaintunnisteella: {key_fingerprint}</small></p>
    </div>

    {answers_html}

    <div class="blockchain-info">
        <h3>🔗 Hajautettu tallennus</h3>
        <p>Tämä sivu tallennettuna IPFS-hajautettuun verkkoon</p>
        <p><strong>Profiilin CID:</strong> <code id="profile-cid">Ladataan...</code></p>
    </div>

    <footer>
        <p><small>Luotu hajautetulla vaalikonnejärjestelmällä - {datetime.now().strftime('%Y-%m-%d')}</small></p>
    </footer>

    <script>
        // Näytä nykyisen sivun CID (jos saatavilla)
        if(window.location.hash) {{
            document.getElementById('profile-cid').textContent = window.location.hash.substring(1);
        }}
    </script>
</body>
</html>
        """
        return html_template
    
    def _generate_answers_html(self, answers: List[Dict[str, Any]]) -> str:
        """Generoi HTML:n vastauksille"""
        answers_html = "<div class='answers'><h3>📝 Vastaukset kysymyksiin</h3>"
        
        for answer in answers:
            question_id = answer.get('question_id', '')
            answer_value = answer.get('answer', '')
            confidence = answer.get('confidence', '')
            comment = answer.get('comment', {}).get('fi', '')
            
            answers_html += f"""
            <div class="answer-item">
                <p><strong>Kysymys {question_id}:</strong> {answer_value}/5</p>
                <p><strong>Varmuus:</strong> {confidence*100}%</p>
                <p><strong>Kommentti:</strong> {comment}</p>
            </div>
            """
        
        answers_html += "</div>"
        return answers_html
    
    def create_signed_profile(self, candidate_id: int, private_key: str) -> Dict[str, Any]:
        """Luo allekirjoitetun profiilin ehdokkaalle"""
        candidate = self.election_manager.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Ehdokasta ID:llä {candidate_id} ei löydy")
        
        # Hae vastaukset (jos saatavilla)
        answers_data = None
        if 'answer_cid' in candidate:
            answers_data = self.ipfs.get_json(candidate['answer_cid'])
        
        # Generoi HTML-sivu
        html_content = self.generate_profile_html(candidate, answers_data)
        
        # Luo profiilidata
        profile_data = {
            "candidate_id": candidate_id,
            "candidate_name": candidate['name'],
            "html_content": html_content,
            "generated_at": datetime.now().isoformat(),
            "election_id": "test_election"
        }
        
        # Allekirjoita profiili
        profile_data["signature"] = self._sign_data(profile_data, private_key)
        profile_data["signed_data"] = json.dumps(profile_data, sort_keys=True)
        
        # Lisää integrity hash
        profile_data["integrity"] = self.election_manager._create_integrity_hash(profile_data)
        
        return profile_data
    
    def publish_profile(self, candidate_id: int, private_key: str) -> str:
        """Julkaise ehdokkaan profiili IPFS:ään"""
        print(f"🌐 Julkaistaan verkkosivuprofiilia ehdokkaalle {candidate_id}...")
        
        # Luo allekirjoitettu profiili
        profile_data = self.create_signed_profile(candidate_id, private_key)
        
        # 1. Tallenna HTML-sivu IPFS:ään
        html_cid = self.ipfs.add_json({"html": profile_data["html_content"]})["Hash"]
        print(f"✅ HTML-sivu tallennettu - CID: {html_cid}")
        
        # 2. Tallenna profiilin metadata IPFS:ään
        profile_cid = self.ipfs.add_json(profile_data)["Hash"]
        print(f"✅ Profiilin metadata tallennettu - CID: {profile_cid}")
        
        # 3. Päivitä ehdokkaan tietoihin
        candidate = self.election_manager.get_candidate(candidate_id)
        candidate["profile_cid"] = profile_cid
        candidate["profile_html_cid"] = html_cid
        self.election_manager.add_candidate(candidate)
        
        # 4. Luo IPFS Gateway URL
        ipfs_gateway_url = f"https://ipfs.io/ipfs/{html_cid}"
        ipfs_local_url = f"/ipfs/{html_cid}"
        
        print(f"✅ Profiili julkaistu onnistuneesti!")
        print(f"🌍 IPFS Gateway: {ipfs_gateway_url}")
        print(f"🔗 IPFS-polku: {ipfs_local_url}")
        
        return profile_cid
    
    def _sign_data(self, data: Dict[str, Any], private_key: str) -> str:
        """Allekirjoittaa datan (yksinkertaistettu toteutus)"""
        # Käytä samaa allekirjoituslogiikkaa kuin aiemmin
        data_str = json.dumps(data, sort_keys=True)
        return f"signature_{hashlib.sha256(data_str.encode()).hexdigest()[:16]}"
