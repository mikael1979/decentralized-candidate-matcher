# src/templates/__init__.py
"""
HTML-template moduuli profiilisivuille
"""

from .html_templates import HTMLTemplates
from .candidate_templates import CandidateTemplates
from .party_templates import PartyTemplates
from .css_generator import CSSGenerator
from .html_generator import HTMLProfileGenerator
from .profile_manager import ProfileManager
from .ipfs_publisher import IPFSPublisher
from .template_utils import TemplateUtils

__all__ = [
    'HTMLTemplates',
    'CandidateTemplates', 
    'PartyTemplates',
    'CSSGenerator',
    'HTMLProfileGenerator',
    'ProfileManager',
    'IPFSPublisher',
    'TemplateUtils'
]
