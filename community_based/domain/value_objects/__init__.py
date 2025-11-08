"""
Value Objects for domain - LOPULLINEN VERSIO
"""

from typing import Dict, Any, Optional

class QuestionContent:
    """Value object representing question content in multiple languages"""
    
    def __init__(self, question: Dict[str, str], category: Dict[str, str], 
                 tags: list = None, scale: Dict[str, Any] = None):
        self.question = question
        self.category = category
        self.tags = tags or []
        self.scale = scale or {
            'min': -5,
            'max': 5,
            'labels': {
                'fi': {'min': 'Täysin eri mieltä', 'neutral': 'Neutraali', 'max': 'Täysin samaa mieltä'},
                'en': {'min': 'Strongly disagree', 'neutral': 'Neutral', 'max': 'Strongly agree'},
                'sv': {'min': 'Helt avig', 'neutral': 'Neutral', 'max': 'Helt enig'}
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': self.question,
            'category': self.category,
            'tags': self.tags,
            'scale': self.scale
        }

class QuestionScale:
    """Value object representing question scale configuration"""
    
    def __init__(self, scale_type: str = "agree_disagree", min_value: int = -5, 
                 max_value: int = 5, labels: Dict[str, Dict[str, str]] = None):
        self.scale_type = scale_type
        self.min_value = min_value
        self.max_value = max_value
        self.labels = labels or {
            'fi': {'min': 'Täysin eri mieltä', 'neutral': 'Neutraali', 'max': 'Täysin samaa mieltä'},
            'en': {'min': 'Strongly disagree', 'neutral': 'Neutral', 'max': 'Strongly agree'},
            'sv': {'min': 'Helt avig', 'neutral': 'Neutral', 'max': 'Helt enig'}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'scale_type': self.scale_type,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'labels': self.labels
        }

class ElectionId:
    def __init__(self, value: str):
        self.value = value
    def __str__(self):
        return self.value

class ElectionName:
    def __init__(self, primary: str, translations: Dict[str, str] = None):
        self.primary = primary
        self.translations = translations or {}
    def to_dict(self) -> Dict[str, str]:
        return {'fi': self.primary, **self.translations}

class ElectionType:
    def __init__(self, value: str):
        self.value = value
    def __str__(self):
        return self.value

class QuestionId:
    def __init__(self, value: str):
        self.value = value
    def __str__(self):
        return self.value
    def __eq__(self, other):
        if isinstance(other, QuestionId):
            return self.value == other.value
        return False
    def __hash__(self):
        return hash(self.value)

class UserId:
    def __init__(self, value: str):
        self.value = value
    def __str__(self):
        return self.value

class MachineId:
    def __init__(self, value: str):
        self.value = value
    def __str__(self):
        return self.value

class CID:
    """Value object representing IPFS Content Identifier"""
    
    def __init__(self, value: str):
        # Sallitaan myös mock-CID:t testaamista varten
        if not (value.startswith('Qm') or value.startswith('Mock')):
            raise ValueError(f"Invalid CID format: {value}")
        self.value = value
    
    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        if isinstance(other, CID):
            return self.value == other.value
        return False
    
    def __hash__(self):
        return hash(self.value)

class Namespace:
    def __init__(self, value: str):
        self.value = value
    def __str__(self):
        return self.value

class BlockName:
    def __init__(self, value: str):
        self.value = value
    def __str__(self):
        return self.value

__all__ = [
    "QuestionContent",
    "QuestionScale", 
    "ElectionId",
    "ElectionName",
    "ElectionType",
    "QuestionId",
    "UserId",
    "MachineId",
    "CID",
    "Namespace",
    "BlockName"
]

class MultilingualText:
    """Value object representing text in multiple languages"""
    
    def __init__(self, fi: str = "", en: str = "", sv: str = ""):
        self.fi = fi
        self.en = en
        self.sv = sv
    
    def to_dict(self) -> Dict[str, str]:
        return {'fi': self.fi, 'en': self.en, 'sv': self.sv}
    
    def get(self, language: str = 'fi') -> str:
        return getattr(self, language, self.fi)

class Category:
    """Value object representing question category"""
    
    def __init__(self, name: MultilingualText, description: MultilingualText = None):
        self.name = name
        self.description = description or MultilingualText()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name.to_dict(),
            'description': self.description.to_dict()
        }

class Scale:
    """Value object representing question scale"""
    
    def __init__(self, min_value: int = -5, max_value: int = 5, 
                 labels: Dict[str, Dict[str, str]] = None):
        self.min_value = min_value
        self.max_value = max_value
        self.labels = labels or {
            'fi': {'min': 'Täysin eri mieltä', 'neutral': 'Neutraali', 'max': 'Täysin samaa mieltä'},
            'en': {'min': 'Strongly disagree', 'neutral': 'Neutral', 'max': 'Strongly agree'},
            'sv': {'min': 'Helt avig', 'neutral': 'Neutral', 'max': 'Helt enig'}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'min': self.min_value,
            'max': self.max_value,
            'labels': self.labels
        }

class Timestamp:
    """Value object representing timestamp"""
    
    def __init__(self, value: str = None):
        from datetime import datetime
        from datetime import timezone
        self.value = value or datetime.now(timezone.utc).isoformat()
    
    def __str__(self):
        return self.value

class RatingValue:
    """Value object representing ELO rating value"""
    
    def __init__(self, value: float = 1000.0):
        self.value = value
    
    def __float__(self):
        return self.value
    
    def __str__(self):
        return str(self.value)

__all__ = [
    "QuestionContent",
    "QuestionScale", 
    "ElectionId",
    "ElectionName",
    "ElectionType",
    "QuestionId",
    "UserId",
    "MachineId",
    "CID",
    "Namespace",
    "BlockName",
    "MultilingualText",  # LISÄTTY
    "Category",          # LISÄTTY
    "Scale",             # LISÄTTY
    "Timestamp",         # LISÄTTY
    "RatingValue"        # LISÄTTY
]

class CreationTimestamps:
    """Value object representing creation and modification timestamps"""
    
    def __init__(self, created: str = None, modified: str = None):
        from datetime import datetime
        from datetime import timezone
        
        now = datetime.now(timezone.utc).isoformat()
        self.created = created or now
        self.modified = modified or now
    
    def update_modified(self):
        """Update the modified timestamp to current time"""
        from datetime import datetime
        from datetime import timezone
        self.modified = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'created': self.created,
            'modified': self.modified
        }

class ConfigHash:
    """Value object representing configuration hash"""
    
    def __init__(self, value: str):
        self.value = value
    
    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        if isinstance(other, ConfigHash):
            return self.value == other.value
        return False

class NodeRole:
    """Value object representing node role in the system"""
    
    def __init__(self, value: str):
        valid_roles = ['master', 'worker', 'standalone']
        if value not in valid_roles:
            raise ValueError(f"Invalid node role: {value}. Must be one of {valid_roles}")
        self.value = value
    
    def __str__(self):
        return self.value

class SyncStatus:
    """Value object representing synchronization status"""
    
    def __init__(self, status: str, last_sync: str = None, next_sync: str = None):
        self.status = status  # 'synced', 'pending', 'error'
        self.last_sync = last_sync
        self.next_sync = next_sync
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status,
            'last_sync': self.last_sync,
            'next_sync': self.next_sync
        }

__all__ = [
    "QuestionContent",
    "QuestionScale", 
    "ElectionId",
    "ElectionName",
    "ElectionType",
    "QuestionId",
    "UserId",
    "MachineId",
    "CID",
    "Namespace",
    "BlockName",
    "MultilingualText",
    "Category",
    "Scale",
    "Timestamp",
    "RatingValue",
    "CreationTimestamps",  # LISÄTTY
    "ConfigHash",          # LISÄTTY
    "NodeRole",            # LISÄTTY
    "SyncStatus"           # LISÄTTY
]

class ElectionStatus:
    """Value object representing election status"""
    
    def __init__(self, value: str):
        valid_statuses = ['upcoming', 'active', 'completed', 'cancelled']
        if value not in valid_statuses:
            raise ValueError(f"Invalid election status: {value}. Must be one of {valid_statuses}")
        self.value = value
    
    def __str__(self):
        return self.value
    
    def is_active(self) -> bool:
        return self.value == 'active'
    
    def is_upcoming(self) -> bool:
        return self.value == 'upcoming'
    
    def is_completed(self) -> bool:
        return self.value == 'completed'

class ElectionPhase:
    """Value object representing election phase"""
    
    def __init__(self, phase_number: int, date: str, description: MultilingualText):
        self.phase_number = phase_number
        self.date = date
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'phase': self.phase_number,
            'date': self.date,
            'description': self.description.to_dict()
        }

class GovernanceModel:
    """Value object representing governance model"""
    
    def __init__(self, value: str):
        valid_models = ['community_driven', 'centralized', 'hybrid']
        if value not in valid_models:
            raise ValueError(f"Invalid governance model: {value}. Must be one of {valid_models}")
        self.value = value
    
    def __str__(self):
        return self.value

class TimelockConfig:
    """Value object representing timelock configuration"""
    
    def __init__(self, enabled: bool = True, edit_deadline: str = None, grace_period_hours: int = 48):
        self.enabled = enabled
        self.edit_deadline = edit_deadline
        self.grace_period_hours = grace_period_hours
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'enabled': self.enabled,
            'edit_deadline': self.edit_deadline,
            'grace_period_hours': self.grace_period_hours
        }

class CommunityConfig:
    """Value object representing community configuration"""
    
    def __init__(self, managed: bool = True, voting_enabled: bool = True, 
                 comparison_enabled: bool = True, submission_enabled: bool = True):
        self.managed = managed
        self.voting_enabled = voting_enabled
        self.comparison_enabled = comparison_enabled
        self.submission_enabled = submission_enabled
    
    def to_dict(self) -> Dict[str, bool]:
        return {
            'managed': self.managed,
            'voting_enabled': self.voting_enabled,
            'comparison_enabled': self.comparison_enabled,
            'submission_enabled': self.submission_enabled
        }

__all__ = [
    "QuestionContent",
    "QuestionScale", 
    "ElectionId",
    "ElectionName",
    "ElectionType",
    "QuestionId",
    "UserId",
    "MachineId",
    "CID",
    "Namespace",
    "BlockName",
    "MultilingualText",
    "Category",
    "Scale",
    "Timestamp",
    "RatingValue",
    "CreationTimestamps",
    "ConfigHash",
    "NodeRole",
    "SyncStatus",
    "ElectionStatus",    # LISÄTTY
    "ElectionPhase",     # LISÄTTY
    "GovernanceModel",   # LISÄTTY
    "TimelockConfig",    # LISÄTTY
    "CommunityConfig"    # LISÄTTY
]
