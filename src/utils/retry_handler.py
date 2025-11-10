"""
Retry handling utilities for failed article generations.
Manages retry logic with feedback incorporation and exponential backoff.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from ..models.evaluation import Evaluation
from ..config import settings

logger = logging.getLogger(__name__)


class RetryHandler:
    """Handles retry logic for failed article generations with feedback incorporation."""
    
    def __init__(self, max_retries: int = None):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts (default from settings)
        """
        self.max_retries = max_retries or settings.max_retries
        self.retry_delays = [1, 2, 4]  # Exponential backoff in seconds
    
    async def execute_with_retry(
        self,
        operation: Callable[..., Awaitable[Any]],
        evaluation_func: Callable[[Any], Awaitable[Evaluation]],
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an operation with retry logic based on evaluation results.
        
        Args:
            operation: The async function to execute (e.g., article generation)
            evaluation_func: Function to evaluate the operation result
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Dictionary containing final result, evaluation, and retry metadata
        """
        retry_count = 0
        previous_evaluation = None
        retry_history = []
        
        while retry_count <= self.max_retries:
            try:
                logger.info(f"Attempt {retry_count + 1}/{self.max_retries + 1}")
                
                # Add retry context to kwargs if this is a retry
                if retry_count > 0 and previous_evaluation:
                    kwargs['retry_count'] = retry_count
                    kwargs['previous_evaluation'] = previous_evaluation
                
                # Execute the operation
                result = await operation(*args, **kwargs)
                
                # Evaluate the result
                evaluation = await evaluation_func(result)
                
                # Store retry history
                retry_history.append({
                    'attempt': retry_count + 1,
                    'score': evaluation.total_score,
                    'passes': evaluation.passes_quality_gate,
                    'critical_issues': evaluation.critical_issues.copy(),
                    'word_count': evaluation.word_count_actual
                })
                
                # Check if result passes quality gate
                if evaluation.passes_quality_gate:
                    logger.info(f"Operation succeeded on attempt {retry_count + 1}")
                    return {
                        'result': result,
                        'evaluation': evaluation,
                        'retry_count': retry_count,
                        'retry_history': retry_history,
                        'final_status': 'PASS'
                    }
                
                # If this was the last attempt, return failure
                if retry_count >= self.max_retries:
                    logger.warning(f"Operation failed after {self.max_retries + 1} attempts")
                    return {
                        'result': result,
                        'evaluation': evaluation,
                        'retry_count': retry_count,
                        'retry_history': retry_history,
                        'final_status': 'FAIL'
                    }
                
                # Prepare for retry
                previous_evaluation = evaluation
                retry_count += 1
                
                # Apply exponential backoff
                delay = self.retry_delays[min(retry_count - 1, len(self.retry_delays) - 1)]
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error in attempt {retry_count + 1}: {e}")
                
                # If this was the last attempt, raise the exception
                if retry_count >= self.max_retries:
                    raise
                
                # Otherwise, retry after delay
                retry_count += 1
                delay = self.retry_delays[min(retry_count - 1, len(self.retry_delays) - 1)]
                logger.info(f"Retrying after error in {delay} seconds...")
                await asyncio.sleep(delay)
        
        # This should never be reached, but just in case
        raise RuntimeError("Unexpected end of retry loop")
    
    def should_retry(self, evaluation: Evaluation) -> bool:
        """
        Determine if an operation should be retried based on evaluation.
        
        Args:
            evaluation: Evaluation results
            
        Returns:
            True if should retry, False otherwise
        """
        # Don't retry if already passing
        if evaluation.passes_quality_gate:
            return False
        
        # Don't retry if word count is critically low (usually unfixable)
        if evaluation.word_count_deviation_percent < -50:
            logger.info("Skipping retry due to critically low word count")
            return False
        
        # Don't retry if there are too many critical issues
        if len(evaluation.critical_issues) > 3:
            logger.info("Skipping retry due to too many critical issues")
            return False
        
        # Retry for other cases
        return True
    
    def generate_retry_feedback(self, evaluation: Evaluation) -> Dict[str, Any]:
        """
        Generate detailed feedback for retry attempts.
        
        Args:
            evaluation: Previous evaluation results
            
        Returns:
            Structured feedback for the retry attempt
        """
        feedback = {
            'previous_score': evaluation.total_score,
            'score_breakdown': {
                'voice_consistency': evaluation.score_breakdown.voice_consistency,
                'structure_quality': evaluation.score_breakdown.structure_quality,
                'medical_accuracy': evaluation.score_breakdown.medical_accuracy,
                'seo_technical': evaluation.score_breakdown.seo_technical
            },
            'critical_issues': evaluation.critical_issues.copy(),
            'improvements_needed': evaluation.improvements_needed.copy(),
            'word_count_issue': evaluation.word_count_deviation_percent < -15.0,
            'specific_instructions': self._generate_specific_instructions(evaluation)
        }
        
        return feedback
    
    def _generate_specific_instructions(self, evaluation: Evaluation) -> List[str]:
        """Generate specific instructions based on evaluation results."""
        instructions = []
        
        # Voice-specific instructions
        if evaluation.score_breakdown.voice_consistency < 20:
            instructions.append("CRITICAL: Use only Γ' ενικό (third person) - 'Ο Δρ. Χλωρός εφαρμόζει', never 'εγώ' or 'μου'")
            instructions.append("Mention credentials (VCU Medical Center, Leeds Hospital) only once in introduction")
        
        # Structure-specific instructions
        if evaluation.score_breakdown.structure_quality < 20:
            instructions.append("Follow logical flow: Ανατομία → Συμπτώματα → Διάγνωση → Θεραπεία → Αποκατάσταση")
            instructions.append("Keep paragraphs to 2-3 sentences maximum")
            instructions.append("Remove any repetitive content or redundant sections")
        
        # Medical accuracy instructions
        if evaluation.score_breakdown.medical_accuracy < 24:
            instructions.append("Use success rate RANGES (75-85%) not exact percentages (80%)")
            instructions.append("Include variability disclaimers: 'εξαρτάται από', 'διαφέρει ανάλογα με'")
            instructions.append("Explain Greek medical terms: 'χόνδρος (το προστατευτικό στρώμα)'")
        
        # SEO and technical instructions
        if evaluation.score_breakdown.seo_technical < 16:
            instructions.append("Ensure main keyword appears in H1 title and first paragraph")
            instructions.append("Use proper markdown: # for H1, ## for H2, **bold** for emphasis")
            instructions.append("Add bullet points and numbered lists where appropriate")
        
        # Word count instructions
        if evaluation.word_count_deviation_percent < -15.0:
            target_increase = abs(int(evaluation.word_count_deviation_percent * evaluation.word_count_target / 100))
            instructions.append(f"CRITICAL: Increase content by approximately {target_increase} words")
            instructions.append("Expand medical explanations, add more detail to treatment sections")
        
        # Critical issue instructions
        for issue in evaluation.critical_issues:
            if "Α' ενικό" in issue:
                instructions.append("ELIMINATE ALL first person references immediately")
            elif "Emotional stories" in issue:
                instructions.append("REMOVE all emotional content and personal stories")
            elif "variability disclaimers" in issue:
                instructions.append("ADD variability disclaimers to all success rates and outcomes")
        
        return instructions
    
    def analyze_retry_pattern(self, retry_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in retry attempts to identify persistent issues.
        
        Args:
            retry_history: List of retry attempt results
            
        Returns:
            Analysis of retry patterns and recommendations
        """
        if not retry_history:
            return {}
        
        # Track score progression
        scores = [attempt['score'] for attempt in retry_history]
        score_trend = 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable'
        
        # Identify persistent issues
        all_issues = []
        for attempt in retry_history:
            all_issues.extend(attempt.get('critical_issues', []))
        
        issue_frequency = {}
        for issue in all_issues:
            issue_frequency[issue] = issue_frequency.get(issue, 0) + 1
        
        persistent_issues = [issue for issue, count in issue_frequency.items() if count > 1]
        
        # Analyze word count progression
        word_counts = [attempt['word_count'] for attempt in retry_history]
        word_count_trend = 'increasing' if word_counts[-1] > word_counts[0] else 'decreasing' if word_counts[-1] < word_counts[0] else 'stable'
        
        return {
            'total_attempts': len(retry_history),
            'score_trend': score_trend,
            'score_range': (min(scores), max(scores)),
            'persistent_issues': persistent_issues,
            'word_count_trend': word_count_trend,
            'final_score': scores[-1] if scores else 0,
            'recommendation': self._get_retry_recommendation(score_trend, persistent_issues)
        }
    
    def _get_retry_recommendation(self, score_trend: str, persistent_issues: List[str]) -> str:
        """Get recommendation based on retry pattern analysis."""
        if score_trend == 'improving' and len(persistent_issues) <= 1:
            return "Continue with current approach - showing improvement"
        elif score_trend == 'stable' and persistent_issues:
            return f"Focus on resolving persistent issues: {', '.join(persistent_issues[:2])}"
        elif score_trend == 'declining':
            return "Consider fundamental approach change - quality declining"
        else:
            return "Standard retry approach - monitor for improvement"
