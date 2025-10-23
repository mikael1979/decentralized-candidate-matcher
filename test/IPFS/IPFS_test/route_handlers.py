from utils import calculate_percentage_level, calculate_similarity, generate_next_id
from utils import sanitize_question_data, sanitize_candidate_data
from utils import validate_question_structure, validate_candidate_structure
from utils import log_security_event
import math

class RouteHandlers:
    def __init__(self, data_manager, debug=False):
        self.data_manager = data_manager
        self.debug = debug

    def calculate_match(self, user_answers, candidate):
        """Laskee yhteensopivuuden käyttäjän ja ehdokkaan välillä"""
        total_diff = 0
        max_possible_diff = 0
        answered_count = 0
        for answer in candidate.get('answers', []):
            question_id = str(answer['question_id'])
            if question_id in user_answers:
                user_answer = user_answers[question_id]
                candidate_answer = answer['answer']
                # Laske ero käyttäjän ja ehdokkaan vastauksen välillä
                diff = abs(user_answer - candidate_answer)
                total_diff += diff
                # Laske suurin mahdollinen ero tälle kysymykselle (-5 - +5 = 10)
                max_possible_diff += 10
                answered_count += 1
        if answered_count == 0:
            return 0
        # Laske yhteensopivuusprosentti
        match_percentage = 1 - (total_diff / max_possible_diff)
        return match_percentage

    def get_parties(self):
        """Hakee kaikki puolueet"""
        candidates = self.data_manager.get_candidates()
        parties = list(set(candidate.get('party', '') for candidate in candidates if candidate.get('party')))
        if self.debug:
            print(f"🔍 Löydetty {len(parties)} puoluetta: {parties}")
        return parties

    def get_party_profile(self, party_name):
        """Laskee puolueen profiilin ja konsensuksen"""
        if self.debug:
            print(f"🔍 Lasketaan profiilia puolueelle: {party_name}")
        candidates = self.data_manager.get_candidates()
        party_candidates = [c for c in candidates if c.get('party') == party_name]
        if not party_candidates:
            if self.debug:
                print(f"❌ Puoluetta '{party_name}' ei löytynyt")
            return {}, {}
        if self.debug:
            print(f"✅ Löydetty {len(party_candidates)} ehdokasta puolueelle {party_name}")
        # Laske keskiarvovastaukset
        answers_by_question = {}
        for candidate in party_candidates:
            for answer in candidate.get('answers', []):
                qid = answer['question_id']
                if qid not in answers_by_question:
                    answers_by_question[qid] = []
                answers_by_question[qid].append(answer['answer'])
        averaged_answers = {}
        for qid, answers in answers_by_question.items():
            averaged_answers[qid] = sum(answers) / len(answers)
        profile = {
            'party_name': party_name,
            'total_candidates': len(party_candidates),
            'averaged_answers': averaged_answers,
            'answer_count': len(averaged_answers)
        }
        # Laske puolueen sisäinen konsensus
        consensus = self._calculate_party_consensus(party_candidates)
        if self.debug:
            print(f"📊 Puolueprofiili luotu: {len(averaged_answers)} keskiarvovastausta, konsensus: {consensus.get('overall_consensus', 0):.1f}%")
        return profile, consensus

    def _calculate_party_consensus(self, party_candidates):
        """Laskee puolueen sisäisen konsensuksen"""
        if len(party_candidates) < 2:
            return {
                'overall_consensus': 100.0,
                'candidate_count': len(party_candidates),
                'note': 'Vain yksi ehdokas, täysi konsensus'
            }
        total_consensus = 0
        consensus_count = 0
        # Vertaile kaikkia ehdokaspareja keskenään
        for i, cand1 in enumerate(party_candidates):
            for j, cand2 in enumerate(party_candidates):
                if i >= j:  # Vältä duplikaatit ja vertailu itseen
                    continue
                common_answers = 0
                total_diff = 0
                # Vertaile vastauksia
                for ans1 in cand1.get('answers', []):
                    for ans2 in cand2.get('answers', []):
                        if ans1['question_id'] == ans2['question_id']:
                            common_answers += 1
                            total_diff += abs(ans1['answer'] - ans2['answer'])
                if common_answers > 0:
                    # Laske konsensus: 0-100 asteikko, jossa 100 = täysin samat vastaukset
                    avg_diff = total_diff / common_answers
                    consensus = max(0, 100 - (avg_diff * 10))  # 10 pisteen ero = 0% konsensus
                    total_consensus += consensus
                    consensus_count += 1
        overall_consensus = total_consensus / consensus_count if consensus_count > 0 else 100.0
        return {
            'overall_consensus': overall_consensus,
            'candidate_count': len(party_candidates),
            'comparison_pairs': consensus_count,
            'consensus_level': calculate_percentage_level(overall_consensus)
        }

    def search_questions(self, query="", tags=None, category=None):
        """Hakee kysymyksiä hakusanan, tagien ja kategorian perusteella"""
        questions = self.data_manager.get_questions()
        results = []
        if self.debug:
            print(f"🔍 Haetaan kysymyksiä: query='{query}', tags={tags}, category={category}")
        for question in questions:
            # Hae kysymysteksti
            question_text = question.get('question', {})
            if isinstance(question_text, dict):
                question_text = question_text.get('fi', '')
            # Tarkista vastaavuudet
            matches_query = not query or query.lower() in question_text.lower()
            matches_category = not category or question.get('category', {}).get('fi') == category
            matches_tags = not tags or any(tag in question.get('tags', []) for tag in tags)
            if matches_query and matches_category and matches_tags:
                # Laske relevanssipistemäärä
                relevance_score = self._calculate_relevance(question, query, tags, category)
                results.append({
                    'question': question,
                    'relevance_score': relevance_score,
                    'match_details': {
                        'query_match': matches_query,
                        'category_match': matches_category,
                        'tags_match': matches_tags
                    }
                })
        # Järjestä relevanssin mukaan
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        if self.debug:
            print(f"✅ Löydetty {len(results)} kysymystä haulle")
        return results

    def _calculate_relevance(self, question, query, tags, category):
        """Laskee kysymyksen relevanssipistemäärän"""
        score = 0.0
        # Query match
        if query:
            question_text = question.get('question', {})
            if isinstance(question_text, dict):
                question_text = question_text.get('fi', '')
            if query.lower() in question_text.lower():
                score += 0.5
            if query.lower() in str(question.get('tags', [])).lower():
                score += 0.3
        # Category match
        if category and question.get('category', {}).get('fi') == category:
            score += 0.3
        # Tags match
        if tags:
            matching_tags = set(tags) & set(question.get('tags', []))
            if matching_tags:
                score += len(matching_tags) * 0.1
        # Normalisoi 0-1 välille
        return min(1.0, score)

    def get_question_categories(self):
        """Hakee kaikki kysymyskategoriat"""
        questions = self.data_manager.get_questions()
        categories = list(set(q.get('category', {}).get('fi', '') for q in questions if q.get('category')))
        if self.debug:
            print(f"📂 Löydetty {len(categories)} kategoriaa: {categories}")
        return categories

    def generate_party_comparison(self, user_answers, party_name):
        """Luo yksityiskohtaisen vertailun käyttäjän ja puolueen välillä"""
        profile, consensus = self.get_party_profile(party_name)
        if not profile:
            return None
        comparison_details = []
        total_similarity = 0
        compared_questions = 0
        for qid, party_avg_answer in profile.get('averaged_answers', {}).items():
            if str(qid) in user_answers:
                user_answer = user_answers[str(qid)]
                difference = abs(user_answer - party_avg_answer)
                similarity = max(0, 100 - (difference * 10))  # 0-100 asteikko
                comparison_details.append({
                    'question_id': qid,
                    'user_answer': user_answer,
                    'party_avg_answer': round(party_avg_answer, 1),
                    'difference': round(difference, 1),
                    'similarity': round(similarity, 1),
                    'similarity_level': calculate_percentage_level(similarity)
                })
                total_similarity += similarity
                compared_questions += 1
        overall_similarity = total_similarity / compared_questions if compared_questions > 0 else 0
        return {
            'party_name': party_name,
            'overall_similarity': round(overall_similarity, 1),
            'compared_questions': compared_questions,
            'party_consensus': consensus.get('overall_consensus', 0),
            'candidate_count': profile.get('total_candidates', 0),
            'comparison_details': comparison_details,
            'summary': self._generate_comparison_summary(overall_similarity, consensus.get('overall_consensus', 0))
        }

    def _generate_comparison_summary(self, similarity, consensus):
        """Luo yhteenvedon vertailusta"""
        if similarity >= 80:
            base = "Sinun ja puolueen näkemykset ovat hyvin samankaltaisia."
        elif similarity >= 60:
            base = "Sinun ja puolueen näkemykset ovat melko samankaltaisia."
        elif similarity >= 40:
            base = "Sinun ja puolueen näkemyksissä on jonkin verran eroja."
        else:
            base = "Sinun ja puolueen näkemyksissä on suuria eroja."
        if consensus >= 80:
            base += " Puolueen ehdokkaat ovat hyvin yhtenäisiä."
        elif consensus >= 60:
            base += " Puolueen ehdokkaat ovat melko yhtenäisiä."
        else:
            base += " Puolueen ehdokkailla on erilaisia näkemyksiä."
        return base

    def validate_question_submission(self, question_data):
        """Validoi käyttäjän lähettämän kysymyksen"""
        errors = validate_question_structure(question_data)
        
        # Tarkista ettei ole duplikaatti
        if not errors:
            existing_questions = self.data_manager.get_questions()
            fi_text = question_data.get('question', {}).get('fi', '')
            for existing in existing_questions:
                existing_text = existing.get('question', {})
                if isinstance(existing_text, dict):
                    existing_text = existing_text.get('fi', '')
                # Yksinkertainen samankaltaisuustarkistus
                if fi_text.lower() in existing_text.lower() or existing_text.lower() in fi_text.lower():
                    similarity = calculate_similarity(fi_text, existing_text)
                    if similarity > 0.8:  # 80% samankaltaisuus
                        errors.append(f'Samankaltainen kysymys on jo olemassa (samankaltaisuus: {similarity:.0f}%)')
                        break
        
        return errors

    def get_system_stats(self):
        """Palauttaa järjestelmän tilastot"""
        questions = self.data_manager.get_questions()
        candidates = self.data_manager.get_candidates()
        parties = self.get_parties()
        # Laske vastausten määrä
        total_answers = sum(len(c.get('answers', [])) for c in candidates)
        # Laske keskimääräinen vastausten määrä per ehdokas
        avg_answers_per_candidate = total_answers / len(candidates) if candidates else 0
        # Laske kysymysten jakautuma kategorioittain
        categories = {}
        for question in questions:
            category = question.get('category', {}).get('fi', 'Määrittelemätön')
            categories[category] = categories.get(category, 0) + 1
        return {
            'total_questions': len(questions),
            'total_candidates': len(candidates),
            'total_parties': len(parties),
            'total_answers': total_answers,
            'avg_answers_per_candidate': round(avg_answers_per_candidate, 1),
            'categories': categories,
            'questions_per_category': categories,
            'system_health': 'good' if len(questions) > 0 and len(candidates) > 0 else 'needs_data'
        }

    # === UUDET MENETELMÄT ELO JA IPFS TUKEA VARTEN ===

    def calculate_elo_change(self, rating_a, rating_b, winner_is_a=True, k=32):
        """
        Laskee Elo-muutoksen kahden kysymyksen välisestä vertailusta.
        
        Args:
            rating_a: Kysymys A:n nykyinen Elo-arvo
            rating_b: Kysymys B:n nykyinen Elo-arvo
            winner_is_a: True jos A voitti, False jos B voitti
            k: K-kerroin (oletus 32)
            
        Returns:
            tuple: (delta_a, delta_b)
        """
        # Laske odotetut tulokset
        expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        expected_b = 1 - expected_a
        
        if winner_is_a:
            delta_a = k * (1 - expected_a)
            delta_b = k * (0 - expected_b)
        else:
            delta_a = k * (0 - expected_a)
            delta_b = k * (1 - expected_b)
            
        return delta_a, delta_b

    def select_questions_for_display(self, strategy="balanced", limit=30):
        """
        Valitsee kysymykset näytettäväksi eri strategioilla.
        
        Args:
            strategy: "top_elo", "diverse", "rising", "balanced", "random"
            limit: Palautettavien kysymysten maksimimäärä
            
        Returns:
            list: Valitut kysymykset
        """
        all_questions = self.data_manager.get_questions()
        
        if strategy == "top_elo":
            return sorted(all_questions, key=lambda q: q.get('elo', {}).get('current_rating', 1200), reverse=True)[:limit]
        
        elif strategy == "diverse":
            categories = {}
            for q in all_questions:
                cat = q.get('category', {}).get('fi', 'muu')
                categories.setdefault(cat, []).append(q)
            
            selected = []
            per_category = max(1, limit // len(categories))
            for cat_questions in categories.values():
                top_in_cat = sorted(cat_questions, key=lambda q: q.get('elo', {}).get('current_rating', 1200), reverse=True)
                selected.extend(top_in_cat[:per_category])
            return selected[:limit]
        
        elif strategy == "rising":
            # Tässä versiossa kaikki kysymykset ovat "uusia", joten käytetään vain Eloa
            return sorted(all_questions, key=lambda q: q.get('elo', {}).get('current_rating', 1200), reverse=True)[:limit]
        
        elif strategy == "balanced":
            top = self.select_questions_for_display("top_elo", int(limit * 0.6))
            diverse = self.select_questions_for_display("diverse", int(limit * 0.2))
            rising = self.select_questions_for_display("rising", int(limit * 0.2))
            
            # Yhdistä ja poista duplikaat
            seen = set()
            result = []
            for q in top + diverse + rising:
                if q['id'] not in seen:
                    result.append(q)
                    seen.add(q['id'])
            return result[:limit]
        
        else:  # random
            import random
            return random.sample(all_questions, min(limit, len(all_questions)))

    def fetch_ipfs_questions(self):
        """
        Hakee kysymykset IPFS:stä ja päivittää välimuistin.
        """
        if hasattr(self.data_manager, 'fetch_questions_from_ipfs'):
            return self.data_manager.fetch_questions_from_ipfs()
        return False

    def apply_elo_update(self, question_id, delta, user_id):
        """
        Päivittää kysymyksen Elo-arvoa.
        """
        if hasattr(self.data_manager, 'apply_elo_delta'):
            return self.data_manager.apply_elo_delta(question_id, delta, user_id)
        return False

    def submit_question(self, question_data):
        """Lisää uuden kysymyksen (sanitoidaan ensin)"""
        # Sanitoi data ennen käsittelyä
        sanitized_data = sanitize_question_data(question_data)
        
        # Validoi rakenne
        validation_errors = self.validate_question_submission(sanitized_data)
        if validation_errors:
            return {'success': False, 'errors': validation_errors}
        
        # Lisää kysymys
        cid = self.data_manager.add_question(sanitized_data)
        if cid:
            # Loki turvallisuustapahtuma
            log_security_event(
                'QUESTION_SUBMITTED',
                f'Kysymys lisätty: {sanitized_data.get("question", {}).get("fi", "")[:50]}...',
                user_id='anonymous'
            )
            return {'success': True, 'cid': cid}
        else:
            return {'success': False, 'errors': ['Tallennus epäonnistui']}

    def add_candidate(self, candidate_data):
        """Lisää uuden ehdokkaan (sanitoidaan ensin)"""
        # Sanitoi data ennen käsittelyä
        sanitized_data = sanitize_candidate_data(candidate_data)
        
        # Validoi rakenne
        validation_errors = validate_candidate_structure(sanitized_data)
        if validation_errors:
            return {'success': False, 'errors': validation_errors}
        
        # Lisää ehdokas
        candidate_id = self.data_manager.add_candidate(sanitized_data)
        if candidate_id:
            # Loki turvallisuustapahtuma
            log_security_event(
                'CANDIDATE_ADDED',
                f'Ehdokas lisätty: {sanitized_data.get("name", "Nimetön")}',
                user_id='admin'
            )
            return {'success': True, 'candidate_id': candidate_id}
        else:
            return {'success': False, 'errors': ['Ehdokkaan lisäys epäonnistui']}
