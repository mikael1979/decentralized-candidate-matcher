# src/templates/template_generator.py
class TemplateGenerator:
    def create_runtime_from_base(self, base_template_path: Path, election_id: str) -> Dict:
        """Luo runtime-instanssin base-templatesta"""
        base_data = self._load_base_template(base_template_path)
        runtime_data = self._transform_to_runtime(base_data, election_id)
        
        # Validoi ennen palautusta
        if not self._validate_runtime_data(runtime_data):
            raise TemplateError(f"Virheellinen runtime-data templatesta {base_template_path}")
        
        return runtime_data
    
    def _transform_to_runtime(self, base_data: Dict, election_id: str) -> Dict:
        """Muunna base-template runtime-muotoon"""
        import copy
        import re
        
        runtime_data = copy.deepcopy(base_data)
        
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str):
                # Korvaa placeholdereit
                obj = re.sub(r'\{\{ELECTION_ID\}\}', election_id, obj)
                obj = re.sub(r'\{\{TIMESTAMP\}\}', datetime.now().isoformat(), obj)
                obj = re.sub(r'\{\{UNIQUE_QUESTION_ID\}\}', f"q_{int(datetime.now().timestamp())}", obj)
                return obj
            else:
                return obj
        
        return replace_placeholders(runtime_data)
