# src/templates/template_quality.py
class TemplateQualityMetrics:
    METRICS = {
        "placeholder_ratio": (0.05, 0.20),  # 5-20% placeholder
        "file_size_kb": (1, 50),           # 1KB - 50KB
        "structure_depth": (2, 4),         # 2-4 sisäkkäisyystasoa
        "documentation_score": (0.8, 1.0), # 80-100% dokumentoitu
        "example_count": (1, 3)            # 1-3 esimerkkiä
    }
    
    def calculate_quality_score(self, template_path: Path) -> float:
        """Laske template-laatu pistemäärä 0-100"""
        metrics = self._analyze_template(template_path)
        return sum(
            self._score_metric(metric, value) 
            for metric, value in metrics.items()
        )
