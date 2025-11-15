# src/templates/css_generator.py
#!/usr/bin/env python3
"""
CSS-tyylit ja väriteemat profiilisivuille
"""

# Esimääritellyt väriteemat eri puolueille
PARTY_COLOR_THEMES = {
    "default": {
        "primary": "#2c3e50",
        "secondary": "#3498db", 
        "accent": "#e74c3c",
        "background": "#ecf0f1"
    },
    "blue_theme": {
        "primary": "#1a5276",
        "secondary": "#3498db",
        "accent": "#2980b9", 
        "background": "#ebf5fb"
    },
    "green_theme": {
        "primary": "#186a3b",
        "secondary": "#27ae60",
        "accent": "#229954",
        "background": "#eafaf1"
    },
    "red_theme": {
        "primary": "#922b21", 
        "secondary": "#e74c3c",
        "accent": "#cb4335",
        "background": "#fdedec"
    },
    "purple_theme": {
        "primary": "#4a235a",
        "secondary": "#8e44ad",
        "accent": "#7d3c98",
        "background": "#f4ecf7"
    }
}

class CSSGenerator:
    """CSS-tyylien generointi"""
    
    @staticmethod
    def get_base_css() -> str:
        """Hae perus-CSS tyylit"""
        return """
/* Perustyylit */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: var(--background-color, #f8f9fa);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Profile Header */
.profile-header {
    background: linear-gradient(135deg, var(--primary-color, #2c3e50), var(--secondary-color, #3498db));
    color: white;
    padding: 3rem 0;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.profile-header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
}

.profile-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin-bottom: 1rem;
}

.profile-meta {
    font-size: 0.9rem;
    opacity: 0.7;
}

/* Navigation */
.profile-nav {
    background-color: var(--secondary-color, #3498db);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-links {
    display: flex;
    justify-content: center;
    list-style: none;
    gap: 2rem;
}

.nav-links a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s ease;
}

.nav-links a:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

/* Content Sections */
.profile-content {
    padding: 3rem 0;
}

.section {
    margin-bottom: 3rem;
    padding: 2rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section h2 {
    color: var(--primary-color, #2c3e50);
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--accent-color, #e74c3c);
}

/* Color Swatches */
.color-swatches {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.color-swatch {
    padding: 1rem;
    border-radius: 4px;
    color: white;
    font-weight: bold;
    text-align: center;
    min-width: 100px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Members Grid */
.members-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.member-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-left: 4px solid var(--accent-color, #e74c3c);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.member-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.member-name {
    font-weight: bold;
    color: var(--primary-color, #2c3e50);
    margin-bottom: 0.5rem;
}

.member-domain {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.member-answers {
    color: var(--secondary-color, #3498db);
    font-weight: 500;
}

/* Data Links */
.data-links {
    margin-top: 1.5rem;
}

.link-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.data-link {
    display: block;
    padding: 1rem;
    background: var(--secondary-color, #3498db);
    color: white;
    text-decoration: none;
    border-radius: 6px;
    text-align: center;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.data-link:hover {
    background: var(--primary-color, #2c3e50);
    transform: translateY(-1px);
}

/* Answers Grid */
.answers-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1.5rem;
}

.answer-item {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    border-left: 4px solid var(--accent-color, #e74c3c);
}

.answer-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--accent-color, #e74c3c);
    margin-bottom: 0.5rem;
}

.answer-question {
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: var(--primary-color, #2c3e50);
}

.answer-explanation {
    color: #666;
    font-style: italic;
    margin-bottom: 0.5rem;
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 4px;
}

.confidence {
    color: #888;
    font-size: 0.9rem;
}

/* Footer */
.profile-footer {
    background: var(--primary-color, #2c3e50);
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
}

.profile-footer p {
    margin-bottom: 0.5rem;
    opacity: 0.9;
}

/* Utility Classes */
.text-center {
    text-align: center;
}

.mt-2 {
    margin-top: 2rem;
}

.mb-1 {
    margin-bottom: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .profile-header h1 {
        font-size: 2rem;
    }
    
    .nav-links {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .members-grid {
        grid-template-columns: 1fr;
    }
    
    .link-grid {
        grid-template-columns: 1fr;
    }
    
    .container {
        padding: 0 15px;
    }
}

/* Animation for interactive elements */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.member-card, .answer-item, .data-link {
    animation: fadeIn 0.5s ease-out;
}

/* Print Styles */
@media print {
    .profile-nav, .data-link {
        display: none;
    }
    
    .profile-header {
        background: #2c3e50 !important;
        -webkit-print-color-adjust: exact;
    }
    
    .section {
        box-shadow: none;
        border: 1px solid #ddd;
    }
}
"""
