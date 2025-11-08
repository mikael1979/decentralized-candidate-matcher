#!/usr/bin/env python3
"""
Question Entity - Domain model for questions
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

# KORJATTU: Oikea import-polku - value_objects on domain-hakemiston tasolla
from ..value_objects import (
    QuestionId, MultilingualText, Category, Scale, 
    Rating, CreationTimestamps, ActiveQuestionRules
)

@dataclass
class Question:
    """Question entity with business logic"""
    
    id: QuestionId
    content: MultilingualText
    category: Category
    scale: Scale
    rating: Rating
    timestamps: CreationTimestamps
    ipfs_cid: Optional[str] = None
    source: str = "local"
    tags: List[str] = field(default_factory=list)
    comparison_count: int = 0
    vote_count: int = 0
    up_votes: int = 0
    down_votes: int = 0
    metadata: dict = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        content: MultilingualText,
        category: Category,
        scale: Scale,
        submitted_by: str,
        tags: Optional[List[str]] = None
    ) -> 'Question':
        """Factory method for creating new questions"""
        question_id = QuestionId.generate()
        
        return cls(
            id=question_id,
            content=content,
            category=category,
            scale=scale,
            rating=Rating(1000),
            timestamps=CreationTimestamps.now(),
            tags=tags or [],
            metadata={
                "submitted_by": submitted_by,
                "status": "pending"
            }
        )
    
    def update_rating(self, delta: int, rating_type: str = "comparison") -> None:
        """Update question rating with domain logic"""
        new_rating = self.rating.adjust(delta)
        
        # Update specific delta based on type
        if rating_type == "comparison":
            self.rating = Rating(
                value=new_rating.value,
                comparison_delta=self.rating.comparison_delta + delta,
                vote_delta=self.rating.vote_delta
            )
            self.comparison_count += 1
        elif rating_type == "vote":
            self.rating = Rating(
                value=new_rating.value,
                comparison_delta=self.rating.comparison_delta,
                vote_delta=self.rating.vote_delta + delta
            )
            self.vote_count += 1
        
        self.timestamps = self.timestamps.with_modified_update()
    
    def add_vote(self, vote_type: str, confidence: int = 3) -> None:
        """Add vote with domain validation"""
        if vote_type not in ["upvote", "downvote"]:
            raise ValueError("Vote type must be 'upvote' or 'downvote'")
        
        if not 1 <= confidence <= 5:
            raise ValueError("Confidence must be between 1 and 5")
        
        # Calculate vote impact (simplified for now)
        impact = 1 if vote_type == "upvote" else -1
        confidence_multiplier = confidence / 3.0  # Normalize to ~0.33-1.67
        
        total_impact = int(impact * confidence_multiplier)
        
        self.update_rating(total_impact, "vote")
        
        if vote_type == "upvote":
            self.up_votes += 1
        else:
            self.down_votes += 1
    
    def is_eligible_for_active(self, rules: ActiveQuestionRules) -> bool:
        """Check if question meets criteria for active questions list"""
        return rules.is_satisfied_by(self)
    
    def should_be_blocked(self) -> bool:
        """Domain logic for automatic question blocking"""
        return (
            self.rating.value <= 0 and
            self.rating.comparison_delta < 0 and
            self.rating.vote_delta < 0
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for persistence"""
        return {
            "local_id": self.id.value,
            "ipfs_cid": self.ipfs_cid,
            "source": self.source,
            "content": {
                "category": {
                    "fi": self.category.name.fi,
                    "en": self.category.name.en,
                    "sv": self.category.name.sv
                },
                "question": {
                    "fi": self.content.fi,
                    "en": self.content.en, 
                    "sv": self.content.sv
                },
                "tags": self.tags,
                "scale": {
                    "min": self.scale.min,
                    "max": self.scale.max,
                    "labels": self.scale.labels
                }
            },
            "elo_rating": {
                "base_rating": 1000,
                "current_rating": self.rating.value,
                "comparison_delta": self.rating.comparison_delta,
                "vote_delta": self.rating.vote_delta,
                "total_comparisons": self.comparison_count,
                "total_votes": self.vote_count,
                "up_votes": self.up_votes,
                "down_votes": self.down_votes
            },
            "timestamps": {
                "created_local": self.timestamps.created.isoformat(),
                "modified_local": self.timestamps.modified.isoformat()
            },
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        """Create Question from dictionary"""
        content = MultilingualText(
            fi=data["content"]["question"]["fi"],
            en=data["content"]["question"]["en"],
            sv=data["content"]["question"]["sv"]
        )
        
        category = Category(
            name=MultilingualText(
                fi=data["content"]["category"]["fi"],
                en=data["content"]["category"]["en"],
                sv=data["content"]["category"]["sv"]
            )
        )
        
        scale_data = data["content"]["scale"]
        scale = Scale(
            min=scale_data["min"],
            max=scale_data["max"],
            labels=scale_data.get("labels", {})
        )
        
        rating_data = data["elo_rating"]
        rating = Rating(
            value=rating_data["current_rating"],
            comparison_delta=rating_data.get("comparison_delta", 0),
            vote_delta=rating_data.get("vote_delta", 0)
        )
        
        timestamps = CreationTimestamps(
            created=datetime.fromisoformat(data["timestamps"]["created_local"].replace('Z', '+00:00')),
            modified=datetime.fromisoformat(data["timestamps"]["modified_local"].replace('Z', '+00:00'))
        )
        
        return cls(
            id=QuestionId(data["local_id"]),
            content=content,
            category=category,
            scale=scale,
            rating=rating,
            timestamps=timestamps,
            ipfs_cid=data.get("ipfs_cid"),
            source=data.get("source", "local"),
            tags=data["content"].get("tags", []),
            comparison_count=rating_data.get("total_comparisons", 0),
            vote_count=rating_data.get("total_votes", 0),
            up_votes=rating_data.get("up_votes", 0),
            down_votes=rating_data.get("down_votes", 0),
            metadata=data.get("metadata", {})
        )
