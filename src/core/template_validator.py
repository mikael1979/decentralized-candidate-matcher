# src/core/template_validator.py
class TemplateValidator:
    def validate_template_directory(self, base_dir: Path) -> Dict:
        """Validoi koko template-hakemisto"""
        results = {
            "valid_templates": [],
            "invalid_templates": [],
            "quality_scores": {},
            "recommendations": []
        }
        
        for template_file in base_dir.rglob("*.base.json"):
            validation_result = self.validate_single_template(template_file)
            
            if validation_result["is_valid"]:
                results["valid_templates"].append(str(template_file))
            else:
                results["invalid_templates"].append({
                    "file": str(template_file),
                    "errors": validation_result["errors"]
                })
            
            results["quality_scores"][str(template_file)] = validation_result["quality_score"]
        
        return results
    
    def validate_single_template(self, template_path: Path) -> Dict:
        """Validoi yksittäinen template"""
        errors = []
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # Tarkista perusrakenteet
            if "metadata" not in template_data:
                errors.append("Puuttuva metadata-osio")
            
            if "schema" not in template_data and not self._has_placeholder_structure(template_data):
                errors.append("Ei template-rakennetta (placeholder tai schema)")
            
            # Tarkista placeholderit
            placeholder_count = self._count_placeholders(template_data)
            if placeholder_count == 0:
                errors.append("Ei placeholder-rakennetta")
            
            # Laske laatu pistemäärä
            quality_score = self._calculate_quality_score(template_data, placeholder_count)
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "quality_score": quality_score,
                "placeholder_count": placeholder_count
            }
            
        except json.JSONDecodeError as e:
            return {
                "is_valid": False,
                "errors": [f"Virheellinen JSON: {e}"],
                "quality_score": 0,
                "placeholder_count": 0
            }
