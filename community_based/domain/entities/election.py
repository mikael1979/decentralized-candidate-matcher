#!/usr/bin/env python3
"""
Election Entity - Domain model for elections
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

# KORJATTU: Oikea import-polku
from ..value_objects import (
    ElectionId, MultilingualText, CreationTimestamps, ElectionStatus
)

@dataclass
class ElectionPhase:
    name: MultilingualText
    start_date: datetime
    end_date: datetime
    description: Optional[MultilingualText] = None
    
    def is_active(self, when: Optional[datetime] = None) -> bool:
        check_time = when or datetime.now()
        return self.start_date <= check_time <= self.end_date

@dataclass
class Election:
    """Election entity with business logic"""
    
    id: ElectionId
    name: MultilingualText
    type: str
    phases: List[ElectionPhase]
    status: ElectionStatus
    timestamps: CreationTimestamps
    description: Optional[MultilingualText] = None
    config: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        name: MultilingualText,
        election_type: str,
        phases: List[ElectionPhase],
        description: Optional[MultilingualText] = None
    ) -> 'Election':
        """Factory method for creating new elections"""
        election_id = ElectionId(f"election_{name.fi.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}")
        
        return cls(
            id=election_id,
            name=name,
            type=election_type,
            phases=phases,
            status=ElectionStatus.DRAFT,
            timestamps=CreationTimestamps.now(),
            description=description,
            config={
                "timelock_enabled": True,
                "grace_period_hours": 48,
                "community_managed": True
            }
        )
    
    def activate(self) -> None:
        """Activate the election"""
        if self.status != ElectionStatus.DRAFT:
            raise ValueError("Only draft elections can be activated")
        
        # Validate that we have at least one active phase
        active_phases = [phase for phase in self.phases if phase.is_active()]
        if not active_phases:
            raise ValueError("Cannot activate election without active phases")
        
        self.status = ElectionStatus.ACTIVE
        self.timestamps = self.timestamps.with_modified_update()
    
    def complete(self) -> None:
        """Mark election as completed"""
        if self.status != ElectionStatus.ACTIVE:
            raise ValueError("Only active elections can be completed")
        
        self.status = ElectionStatus.COMPLETED
        self.timestamps = self.timestamps.with_modified_update()
    
    def get_current_phase(self) -> Optional[ElectionPhase]:
        """Get the currently active phase"""
        for phase in self.phases:
            if phase.is_active():
                return phase
        return None
    
    def is_accepting_questions(self) -> bool:
        """Check if election is currently accepting new questions"""
        if self.status != ElectionStatus.ACTIVE:
            return False
        
        current_phase = self.get_current_phase()
        if not current_phase:
            return False
        
        # Business rule: Only accept questions in specific phases
        # This could be configurable per election type
        return "submission" in current_phase.name.fi.lower()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for persistence"""
        return {
            "election_id": self.id.value,
            "name": {
                "fi": self.name.fi,
                "en": self.name.en,
                "sv": self.name.sv
            },
            "type": self.type,
            "status": self.status.value,
            "description": {
                "fi": self.description.fi if self.description else "",
                "en": self.description.en if self.description else "", 
                "sv": self.description.sv if self.description else ""
            } if self.description else None,
            "dates": [
                {
                    "phase": {
                        "fi": phase.name.fi,
                        "en": phase.name.en,
                        "sv": phase.name.sv
                    },
                    "start": phase.start_date.isoformat(),
                    "end": phase.end_date.isoformat()
                }
                for phase in self.phases
            ],
            "config": self.config,
            "metadata": self.metadata,
            "created": self.timestamps.created.isoformat(),
            "last_updated": self.timestamps.modified.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Election':
        """Create Election from dictionary"""
        name = MultilingualText(
            fi=data["name"]["fi"],
            en=data["name"]["en"],
            sv=data["name"]["sv"]
        )
        
        description = None
        if data.get("description"):
            description = MultilingualText(
                fi=data["description"]["fi"],
                en=data["description"]["en"],
                sv=data["description"]["sv"]
            )
        
        phases = []
        for phase_data in data["dates"]:
            phase = ElectionPhase(
                name=MultilingualText(
                    fi=phase_data["phase"]["fi"],
                    en=phase_data["phase"]["en"],
                    sv=phase_data["phase"]["sv"]
                ),
                start_date=datetime.fromisoformat(phase_data["start"].replace('Z', '+00:00')),
                end_date=datetime.fromisoformat(phase_data["end"].replace('Z', '+00:00'))
            )
            phases.append(phase)
        
        timestamps = CreationTimestamps(
            created=datetime.fromisoformat(data["created"].replace('Z', '+00:00')),
            modified=datetime.fromisoformat(data["last_updated"].replace('Z', '+00:00'))
        )
        
        return cls(
            id=ElectionId(data["election_id"]),
            name=name,
            type=data["type"],
            phases=phases,
            status=ElectionStatus(data["status"]),
            timestamps=timestamps,
            description=description,
            config=data.get("config", {}),
            metadata=data.get("metadata", {})
        )
