# src/templates/candidate_templates.py - KORJAA

class CandidateTemplates:
    @staticmethod
    def generate_candidate_html(*args, **kwargs) -> str:
        candidate_data = args[0] if args else kwargs.get('candidate_data', {})
        election_id = args[3] if len(args) > 3 else kwargs.get('election_id', "Jumaltenvaalit2026")
        
        # UUSI: Hae värit konfiguraatiosta
        colors = args[2] if len(args) > 2 else kwargs.get('colors')
        if colors is None:
            colors = CSSGenerator.get_color_themes(election_id).get("default", {})
