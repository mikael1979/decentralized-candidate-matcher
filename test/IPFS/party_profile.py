# party_profile.py
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter

class PartyProfile:
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.election_manager = election_manager
    
    def calculate_party_answers(self, party_name: str) -> Dict[str, Any]:
        """Laskee puolueen keskiarvovastaukset sen ehdokkaiden perusteella"""
        candidates_data = self.election_manager.get_election_data("candidates.json")
        if not candidates_data:
            return {}
        
        # Kerää puolueen ehdokkaiden vastaukset
        party_answers = {}
        answer_counts = {}
        candidate_count = 0
        
        for candidate in candidates_data.get("candidates", []):
            if candidate.get("party") != party_name:
                continue
            
            candidate_answers = self._get_candidate_answers(candidate)
            if not candidate_answers:
                continue
            
            candidate_count += 1
            
            for answer in candidate_answers.get("answers", []):
                q_id = str(answer.get("question_id"))
                value = answer.get("answer")
                confidence = answer.get("confidence", 1.0)
                
                if q_id not in party_answers:
                    party_answers[q_id] = 0.0
                    answer_counts[q_id] = 0.0
                
                # Painotettu keskiarvo luottamuksella
                party_answers[q_id] += value * confidence
                answer_counts[q_id] += confidence
        
        # Laske keskiarvot
        averaged_answers = {}
        for q_id, total in party_answers.items():
            count = answer_counts[q_id]
            if count > 0:
                averaged_answers[q_id] = {
                    "answer": round(total / count, 2),
                    "confidence": min(count / candidate_count, 1.0),  # Konsensus
                    "response_rate": count / candidate_count,
                    "candidate_count": candidate_count
                }
        
        return {
            "party_name": party_name,
            "averaged_answers": averaged_answers,
            "total_candidates": candidate_count,
            "calculated_at": datetime.now().isoformat()
        }
    
    def get_party_consensus(self, party_name: str) -> Dict[str, Any]:
        """Laskee puolueen konsensuksen (yhtenäisyyden)"""
        candidates_data = self.election_manager.get_election_data("candidates.json")
        if not candidates_data:
            return {}
        
        consensus_data = {}
        party_candidates = []
        
        # Kerää puolueen ehdokkaat
        for candidate in candidates_data.get("candidates", []):
            if candidate.get("party") == party_name:
                candidate_answers = self._get_candidate_answers(candidate)
                if candidate_answers:
                    party_candidates.append(candidate_answers)
        
        if not party_candidates:
            return {}
        
        # Laske konsensus kullekin kysymykselle
        for q_id in self._get_all_question_ids():
            answers = []
            for candidate_data in party_candidates:
                for answer in candidate_data.get("answers", []):
                    if str(answer.get("question_id")) == q_id:
                        answers.append(answer.get("answer"))
                        break
            
            if answers:
                consensus = self._calculate_consensus(answers)
                consensus_data[q_id] = {
                    "consensus_score": consensus,
                    "answer_variance": self._calculate_variance(answers),
                    "response_count": len(answers),
                    "average_answer": sum(answers) / len(answers)
                }
        
        return {
            "party_name": party_name,
            "consensus_data": consensus_data,
            "overall_consensus": self._calculate_overall_consensus(consensus_data),
            "calculated_at": datetime.now().isoformat()
        }
    
    def generate_party_profile_html(self, party_name: str) -> str:
        """Generoi puolueen verkkosivuprofiilin"""
        party_answers = self.calculate_party_answers(party_name)
        consensus_data = self.get_party_consensus(party_name)
        
        # Hae puolueen ehdokkaat
        candidates_data = self.election_manager.get_election_data("candidates.json")
        party_candidates = [c for c in candidates_data.get("candidates", []) 
                          if c.get("party") == party_name] if candidates_data else []
        
        # Generoi HTML
        html_template = f"""
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Puolueprofiili - {party_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ border-bottom: 3px solid #2c3e50; padding-bottom: 15px; margin-bottom: 20px; }}
        .party-info {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .answers {{ margin-top: 20px; }}
        .answer-item {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .consensus-bar {{ background: #e9ecef; height: 20px; border-radius: 10px; margin: 5px 0; }}
        .consensus-fill {{ background: linear-gradient(90deg, #e74c3c, #f39c12, #27ae60); height: 100%; border-radius: 10px; }}
        .candidate-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin-top: 15px; }}
        .candidate-item {{ background: white; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ Puolueprofiili - {party_name}</h1>
    </div>

    <div class="party-info">
        <h3>📊 Puoluetilastot</h3>
        <p><strong>Ehdokkaita:</strong> {len(party_candidates)}</p>
        <p><strong>Vastausten keskiarvoja:</strong> {len(party_answers.get('averaged_answers', {}))}</p>
        <p><strong>Kokonaiskonsensus:</strong> {consensus_data.get('overall_consensus', 0):.1f}%</p>
        <p><strong>Laskettu:</strong> {party_answers.get('calculated_at', '')}</p>
    </div>

    <div class="consensus">
        <h3>🎯 Puolueen Konsensus</h3>
        <p>Mittaa kuinka yhtenäisiä vastaukset ovat puolueen sisällä:</p>
        <div class="consensus-bar">
            <div class="consensus-fill" style="width: {consensus_data.get('overall_consensus', 0)}%"></div>
        </div>
        <p><small>0% = täysin erilaiset vastaukset, 100% = täysin samat vastaukset</small></p>
    </div>

    <div class="answers">
        <h3>📝 Puolueen Keskimääräiset Vastaukset</h3>
        {"".join(self._generate_answer_html(party_answers, consensus_data))}
    </div>

    <div class="candidates">
        <h3>👥 Puolueen Ehdokkaat</h3>
        <div class="candidate-list">
            {"".join(f'<div class="candidate-item">{candidate["name"]}</div>' for candidate in party_candidates[:10])}
        </div>
        {f'<p><em>+ {len(party_candidates) - 10} muuta ehdokasta...</em></p>' if len(party_candidates) > 10 else ''}
    </div>

    <footer style="margin-top: 40px; border-top: 1px solid #ddd; padding-top: 20px;">
        <p><small>Luotu hajautetulla vaalikonnejärjestelmällä - {datetime.now().strftime('%Y-%m-%d')}</small></p>
    </footer>
</body>
</html>
        """
        return html_template
    
    def _generate_answer_html(self, party_answers: Dict, consensus_data: Dict) -> List[str]:
        """Generoi HTML:n puolueen vastauksille"""
        html_parts = []
        
        for q_id, answer_data in party_answers.get("averaged_answers", {}).items():
            question_text = self._get_question_text(q_id)
            consensus = consensus_data.get("consensus_data", {}).get(q_id, {})
            
            answer_value = answer_data["answer"]
            confidence = answer_data["confidence"]
            response_rate = answer_data["response_rate"]
            consensus_score = consensus.get("consensus_score", 0)
            
            # Määritä väri vastauksen perusteella
            if answer_value >= 3:
                color = "#27ae60"  # Vihreä (myönteinen)
            elif answer_value <= -3:
                color = "#e74c3c"  # Punainen (kielteinen)
            else:
                color = "#f39c12"  # Oranssi (neutraali)
            
            html_parts.append(f"""
            <div class="answer-item">
                <div style="font-weight: bold; margin-bottom: 8px;">{question_text}</div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>Keskiarvo: <strong style="color: {color};">{answer_value}/5</strong></span>
                    <span>Vastausprosentti: {response_rate:.0%}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
                    <span>Konsensus: {consensus_score:.0%}</span>
                    <span>Luottamus: {confidence:.0%}</span>
                </div>
                <div class="consensus-bar">
                    <div class="consensus-fill" style="width: {consensus_score * 100}%"></div>
                </div>
            </div>
            """)
        
        return html_parts
    
    def _get_candidate_answers(self, candidate: Dict) -> Optional[Dict]:
        """Hakee ehdokkaan vastaukset"""
        if "answer_cid" not in candidate:
            return None
        return self.ipfs.get_json(candidate["answer_cid"])
    
    def _get_all_question_ids(self) -> List[str]:
        """Palauttaa kaikkien kysymysten ID:t"""
        questions = self.election_manager.get_all_questions()
        return [str(q.get("id")) for q in questions]
    
    def _get_question_text(self, question_id: str) -> str:
        """Hakee kysymystekstin"""
        questions = self.election_manager.get_all_questions()
        for q in questions:
            if str(q.get("id")) == question_id:
                return q.get("question", {}).get("fi", f"Kysymys {question_id}")
        return f"Kysymys {question_id}"
    
    def _calculate_consensus(self, answers: List[float]) -> float:
        """Laskee vastausten konsensuksen (1.0 = täysin samat, 0.0 = täysin erilaiset)"""
        if len(answers) <= 1:
            return 1.0
        
        # Konsensus perustuu vastausten varianssiin
        variance = self._calculate_variance(answers)
        max_variance = 20.0  # Maksimivarianssi -5...5 asteikolla
        return max(0.0, 1.0 - (variance / max_variance))
    
    def _calculate_variance(self, answers: List[float]) -> float:
        """Laskee vastausten varianssin"""
        if len(answers) <= 1:
            return 0.0
        mean = sum(answers) / len(answers)
        return sum((x - mean) ** 2 for x in answers) / len(answers)
    
    def _calculate_overall_consensus(self, consensus_data: Dict) -> float:
        """Laskee kokonaiskonsensuksen"""
        if not consensus_data:
            return 0.0
        scores = [data["consensus_score"] for data in consensus_data.values()]
        return sum(scores) / len(scores) * 100
    
    def publish_party_profile(self, party_name: str) -> str:
        """Julkaisee puolueen profiilin IPFS:ään"""
        print(f"🏛️ Julkaistaan puolueprofiilia: {party_name}")
        
        # Generoi profiili
        html_content = self.generate_party_profile_html(party_name)
        profile_data = {
            "party_name": party_name,
            "html_content": html_content,
            "generated_at": datetime.now().isoformat(),
            "election_id": "test_election"
        }
        
        # Tallenna IPFS:ään
        html_cid = self.ipfs.add_json({"html": html_content})["Hash"]
        profile_cid = self.ipfs.add_json(profile_data)["Hash"]
        
        print(f"✅ Puolueprofiili julkaistu - CID: {profile_cid}")
        print(f"🌐 HTML-sivu: https://ipfs.io/ipfs/{html_cid}")
        
        return profile_cid

class PartyComparison:
    """Puolueiden vertailutoiminnallisuus"""
    
    def __init__(self, ipfs, election_manager):
        self.ipfs = ipfs
        self.election_manager = election_manager
        self.party_profile = PartyProfile(ipfs, election_manager)
    
    def get_all_parties(self) -> List[str]:
        """Palauttaa kaikki puolueet"""
        candidates_data = self.election_manager.get_election_data("candidates.json")
        if not candidates_data:
            return []
        
        parties = set()
        for candidate in candidates_data.get("candidates", []):
            if candidate.get("party"):
                parties.add(candidate["party"])
        
        return sorted(list(parties))
    
    def compare_parties(self, user_answers: Dict[str, int]) -> List[Dict[str, Any]]:
        """Vertaa käyttäjän vastauksia puolueiden keskiarvoihin"""
        parties = self.get_all_parties()
        comparisons = []
        
        for party in parties:
            party_answers = self.party_profile.calculate_party_answers(party)
            match_result = self._calculate_party_match(user_answers, party_answers)
            
            comparisons.append({
                "party_name": party,
                "match_percentage": match_result["percentage"],
                "match_score": match_result["score"],
                "max_possible_score": match_result["max_possible_score"],
                "matched_questions": match_result["matched_questions"],
                "candidate_count": party_answers.get("total_candidates", 0),
                "overall_consensus": self.party_profile.get_party_consensus(party).get("overall_consensus", 0)
            })
        
        return sorted(comparisons, key=lambda x: x["match_percentage"], reverse=True)
    
    def _calculate_party_match(self, user_answers: Dict, party_answers: Dict) -> Dict[str, Any]:
        """Laskee käyttäjän ja puolueen välisten vastausten yhteensopivuuden"""
        total_score = 0
        max_possible_score = len(user_answers) * 5
        matched_questions = 0
        
        for q_id, user_answer in user_answers.items():
            party_answer_data = party_answers.get("averaged_answers", {}).get(q_id)
            
            if party_answer_data:
                party_answer = party_answer_data["answer"]
                distance = abs(party_answer - user_answer)
                similarity = 5 - distance
                score = max(0, similarity)
                
                total_score += score
                matched_questions += 1
        
        percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        return {
            "score": total_score,
            "max_possible_score": max_possible_score,
            "percentage": percentage,
            "matched_questions": matched_questions
        }
    
    def generate_comparison_html(self, user_answers: Dict[str, int]) -> str:
        """Generoi puoluevertailun HTML-sivun"""
        comparisons = self.compare_parties(user_answers)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Puoluevertailu</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        .comparison-item {{ border: 1px solid #ddd; padding: 20px; margin: 15px 0; border-radius: 10px; }}
        .match-bar {{ background: #e9ecef; height: 25px; border-radius: 12px; margin: 10px 0; }}
        .match-fill {{ background: linear-gradient(90deg, #e74c3c, #f39c12, #27ae60); height: 100%; border-radius: 12px; transition: width 0.5s; }}
        .consensus-bar {{ background: #f8f9fa; height: 15px; border-radius: 7px; margin: 5px 0; }}
        .consensus-fill {{ background: #3498db; height: 100%; border-radius: 7px; }}
    </style>
</head>
<body>
    <h1>🏛️ Puoluevertailu</h1>
    <p>Vertaa vastauksiasi puolueiden keskiarvoihin</p>
    
    <div class="comparisons">
        {"".join(self._generate_comparison_html(comparisons))}
    </div>
    
    <footer style="margin-top: 40px; border-top: 1px solid #ddd; padding-top: 20px;">
        <p><small>Luotu hajautetulla vaalikonnejärjestelmällä - {datetime.now().strftime('%Y-%m-%d')}</small></p>
    </footer>
</body>
</html>
        """
        return html_template
    
    def _generate_comparison_html(self, comparisons: List[Dict]) -> List[str]:
        """Generoi vertailu HTML:ää"""
        html_parts = []
        
        for comp in comparisons:
            match_pct = comp["match_percentage"]
            consensus = comp["overall_consensus"]
            candidate_count = comp["candidate_count"]
            
            html_parts.append(f"""
            <div class="comparison-item">
                <h3>{comp['party_name']}</h3>
                <div style="display: flex; justify-content: space-between;">
                    <span>Yhteensopivuus: <strong>{match_pct:.1f}%</strong></span>
                    <span>Ehdokkaita: {candidate_count}</span>
                </div>
                <div class="match-bar">
                    <div class="match-fill" style="width: {match_pct}%"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.9em;">
                    <span>Puolueen konsensus: {consensus:.1f}%</span>
                    <span>Vastattuja kysymyksiä: {comp['matched_questions']}</span>
                </div>
                <div class="consensus-bar">
                    <div class="consensus-fill" style="width: {consensus}%"></div>
                </div>
            </div>
            """)
        
        return html_parts
