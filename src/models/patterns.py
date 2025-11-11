"""
Pattern and validation models for content quality control.
"""

from typing import Optional, Dict, Any, Union
from typing import List  # Separate import for Railway compatibility
from pydantic import BaseModel, Field
from enum import Enum


class PatternType(str, Enum):
    """Types of content patterns."""
    VOICE = "voice"
    STRUCTURE = "structure"
    MEDICAL = "medical"
    SEO = "seo"
    CULTURAL = "cultural"


class Pattern(BaseModel):
    """Approved content pattern."""
    id: str = Field(..., description="Unique pattern identifier")
    name: str = Field(..., description="Human-readable pattern name")
    description: str = Field(..., description="Pattern description")
    pattern_type: PatternType = Field(..., description="Type of pattern")
    examples: List[str] = Field(..., description="Examples of correct usage")
    weight: int = Field(default=1, description="Pattern importance weight")
    required: bool = Field(default=False, description="Whether pattern is required")


class AntiPattern(BaseModel):
    """Forbidden content pattern."""
    id: str = Field(..., description="Unique anti-pattern identifier")
    name: str = Field(..., description="Human-readable anti-pattern name")
    description: str = Field(..., description="What to avoid")
    pattern_type: PatternType = Field(..., description="Type of anti-pattern")
    examples: List[str] = Field(..., description="Examples of what NOT to do")
    penalty_points: int = Field(..., description="Points deducted if found")
    auto_fail: bool = Field(default=False, description="Whether this causes automatic failure")


class Structure(BaseModel):
    """Content structure guideline."""
    id: str = Field(..., description="Unique structure identifier")
    name: str = Field(..., description="Structure name")
    description: str = Field(..., description="Structure description")
    required_sections: List[str] = Field(..., description="Required section titles")
    optional_sections: List[str] = Field(default_factory=list, description="Optional section titles")
    section_order: List[str] = Field(..., description="Recommended section order")
    min_sections: int = Field(default=3, description="Minimum number of sections")
    max_sections: int = Field(default=8, description="Maximum number of sections")


class ScoringCriteria(BaseModel):
    """Individual scoring criterion."""
    name: str = Field(..., description="Criterion name")
    description: str = Field(..., description="What this criterion measures")
    max_points: int = Field(..., description="Maximum points for this criterion")
    evaluation_method: str = Field(..., description="How to evaluate this criterion")


class ScoringMatrix(BaseModel):
    """Complete scoring matrix for quality evaluation."""
    voice_consistency: List[ScoringCriteria] = Field(..., description="Voice consistency criteria")
    structure_quality: List[ScoringCriteria] = Field(..., description="Structure quality criteria")
    medical_accuracy: List[ScoringCriteria] = Field(..., description="Medical accuracy criteria")
    seo_technical: List[ScoringCriteria] = Field(..., description="SEO and technical criteria")
    
    total_possible_points: int = Field(default=100, description="Total possible points")
    pass_threshold: int = Field(default=80, description="Minimum score to pass")


class Fix(BaseModel):
    """Specific fix for common issues."""
    id: str = Field(..., description="Unique fix identifier")
    issue_description: str = Field(..., description="Description of the issue")
    fix_description: str = Field(..., description="How to fix the issue")
    pattern_type: PatternType = Field(..., description="Type of pattern this fix addresses")
    examples: Optional[List[Dict[str, str]]] = Field(None, description="Before/after examples")
    priority: int = Field(default=1, description="Fix priority (1=high, 3=low)")


class ValidationResult(BaseModel):
    """Result of pattern validation."""
    is_valid: bool = Field(..., description="Whether content passes validation")
    matched_patterns: List[str] = Field(..., description="IDs of matched approved patterns")
    violated_antipatterns: List[str] = Field(..., description="IDs of violated anti-patterns")
    suggested_fixes: List[str] = Field(..., description="IDs of suggested fixes")
    validation_score: int = Field(..., description="Validation score based on patterns")
    detailed_feedback: Dict[str, Any] = Field(..., description="Detailed validation feedback")
