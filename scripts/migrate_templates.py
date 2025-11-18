# scripts/migrate_templates.py
def migrate_legacy_templates():
    """Siirrä vanhat templatet uuteen formaattiin"""
    
    migrations = [
        {
            "from": "data/runtime/questions.json",
            "to": "templates/base/questions.base.json",
            "transformer": QuestionTemplateTransformer()
        },
        {
            "from": "src/templates/css_generator.py::PARTY_COLOR_THEMES", 
            "to": "config/system/color_themes.json",
            "transformer": ColorThemeTransformer()
        }
    ]
    
    for migration in migrations:
        migrate_single_template(migration)
