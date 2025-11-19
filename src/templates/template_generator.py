# src/templates/template_generator.py - LAJENNETTU
class TemplateGenerator:
    def create_runtime_from_base(self, base_template_path: Path, election_id: str) -> Dict:
        """Luo runtime-instanssin base-templatesta - LAJENNETTU VERSIO"""
        base_data = self._load_base_template(base_template_path)
        runtime_data = self._transform_to_runtime_extended(base_data, election_id)
        
        # Validoi ennen palautusta
        if not self._validate_runtime_data_extended(runtime_data):
            raise TemplateError(f"Virheellinen runtime-data templatesta {base_template_path}")
        
        return runtime_data
    
    def _transform_to_runtime_extended(self, base_data: Dict, election_id: str) -> Dict:
        """Muunna base-template runtime-muotoon - LAJENNETTU"""
        import copy
        import re
        from datetime import datetime
        
        runtime_data = copy.deepcopy(base_data)
        
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str):
                # Korvaa placeholdereit laajennetuilla arvoilla
                replacements = {
                    r'\{\{ELECTION_ID\}\}': election_id,
                    r'\{\{TIMESTAMP\}\}': datetime.now().isoformat(),
                    r'\{\{CANDIDATE_ID\}\}': f"cand_{int(datetime.now().timestamp())}",
                    r'\{\{FI_NAME\}\}': "Uusi Ehdokas",
                    r'\{\{EN_NAME\}\}': "New Candidate", 
                    r'\{\{SV_NAME\}\}': "Ny Kandidat",
                    r'\{\{PARTY\}\}': "sitoutumaton",
                    r'\{\{DOMAIN\}\}': "general",
                    r'\{\{FI_DESCRIPTION\}\}': "Ehdokkaan kuvaus suomeksi",
                    r'\{\{EN_DESCRIPTION\}\}': "Candidate description in English",
                    r'\{\{SV_DESCRIPTION\}\}': "Kandidatbeskrivning på svenska",
                    r'\{\{SYMBOL\}\}': "symboli",
                    r'\{\{POWER_LEVEL\}\}': "5",
                    r'\{\{ACTIVE_STATUS\}\}': "true",
                    r'\{\{VERIFIED_STATUS\}\}': "false",
                    r'\{\{CAMPAIGN_THEME\}\}': "Kampanjateema",
                    r'\{\{QUESTION_ID\}\}': f"q_{int(datetime.now().timestamp())}",
                    r'\{\{ANSWER_VALUE\}\}': "0",
                    r'\{\{CONFIDENCE\}\}': "3",
                    r'\{\{FI_EXPLANATION\}\}': "Vastauksen perustelu",
                    r'\{\{EN_EXPLANATION\}\}': "Answer explanation",
                    r'\{\{SV_EXPLANATION\}\}': "Svarförklaring"
                }
                
                result = obj
                for pattern, replacement in replacements.items():
                    result = re.sub(pattern, replacement, result)
                return result
            else:
                return obj
        
        return replace_placeholders(runtime_data)
    
    def _validate_runtime_data_extended(self, runtime_data: Dict) -> bool:
        """Validoi runtime-data laajennetulla logiikalla"""
        try:
            # Tarkista pakolliset kentät
            if "candidates" not in runtime_data:
                return False
                
            for candidate in runtime_data["candidates"]:
                # Pakolliset kentät
                if "candidate_id" not in candidate:
                    return False
                if "basic_info" not in candidate:
                    return False
                if "name" not in candidate["basic_info"]:
                    return False
                if "fi" not in candidate["basic_info"]["name"]:
                    return False
                    
                # Validoi vastaukset jos niitä on
                if "answers" in candidate:
                    for answer in candidate["answers"]:
                        if not (-5 <= answer.get("answer_value", 0) <= 5):
                            return False
                        if not (1 <= answer.get("confidence", 3) <= 5):
                            return False
            
            return True
            
        except Exception:
            return False
