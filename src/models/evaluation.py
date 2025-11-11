"""
Evaluation and scoring models for quality assessment.
"""

from typing import Optional, Dict, Any
from typing import List  # Separate import for Railway compatibility
from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of quality scores."""
    voice_consistency: int = Field(..., ge=0, le=25, description="Voice consistency score (0-25)")
    structure_quality: int = Field(..., ge=0, le=25, description="Structure quality score (0-25)")
    medical_accuracy: int = Field(..., ge=0, le=30, description="Medical accuracy score (0-30)")
    seo_technical: int = Field(..., ge=0, le=20, description="SEO and technical score (0-20)")
    
    def calculate_total(self) -> int:
        """Calculate total score from all categories."""
        return self.voice_consistency + self.structure_quality + self.medical_accuracy + self.seo_technical


class Evaluation(BaseModel):
    """Complete evaluation results for an article."""
    total_score: int = Field(..., ge=0, le=100, description="Total quality score (0-100)")
    score_breakdown: ScoreBreakdown = Field(..., description="Detailed score breakdown")
    
    # Word count analysis
    word_count_actual: int = Field(..., description="Actual word count of the article")
    word_count_target: int = Field(..., description="Target word count")
    word_count_deviation_percent: float = Field(..., description="Percentage deviation from target")
    
    # Quality assessment
    critical_issues: List[str] = Field(..., description="Critical issues found in the article")
    improvements_needed: List[str] = Field(..., description="Specific improvements needed")
    passes_quality_gate: bool = Field(..., description="Whether article passes the quality gate")
    
    # Detailed analysis
    voice_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed voice analysis")
    structure_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed structure analysis")
    medical_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed medical accuracy analysis")
    seo_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed SEO analysis")
    
    # Retry information
    retry_count: int = Field(default=0, description="Number of retry attempts")
    previous_scores: Optional[List[int]] = Field(None, description="Previous attempt scores")
    
    def calculate_word_count_deviation(self) -> float:
        """Calculate word count deviation percentage."""
        if self.word_count_target == 0:
            return 0.0
        deviation = ((self.word_count_actual - self.word_count_target) / self.word_count_target) * 100
        self.word_count_deviation_percent = deviation
        return deviation
    
    def determine_pass_status(self, pass_threshold: int = 80, word_count_fail_threshold: float = -15.0) -> bool:
        """Determine if article passes quality gate."""
        score_passes = self.total_score >= pass_threshold
        word_count_passes = self.word_count_deviation_percent > word_count_fail_threshold
        
        self.passes_quality_gate = score_passes and word_count_passes
        return self.passes_quality_gate
    
    def get_retry_feedback(self) -> Dict[str, Any]:
        """Generate feedback for retry attempts."""
        return {
            "previous_score": self.total_score,
            "critical_issues": self.critical_issues,
            "improvements_needed": self.improvements_needed,
            "score_breakdown": self.score_breakdown.dict(),
            "word_count_issue": self.word_count_deviation_percent < -15.0,
            "retry_count": self.retry_count
        }
