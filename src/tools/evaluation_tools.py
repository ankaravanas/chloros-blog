"""
Phase 3 evaluation tools for quality assessment.
Implements comprehensive article evaluation with 4-category scoring system.
"""

import logging
from typing import Dict, Any, Optional
from fastmcp import FastMCP

from ..services.openrouter_service import OpenRouterService
from ..utils.scoring_engine import ScoringEngine
from ..utils.content_validator import ContentValidator
from ..models.patterns import Pattern, AntiPattern

logger = logging.getLogger(__name__)

# Service instance
openrouter_service = OpenRouterService()


async def register_evaluation_tools(mcp: FastMCP):
    """Register all Phase 3 evaluation tools with the MCP server."""
    
    @mcp.tool()
    async def evaluate_article_quality(
        complete_article: str,
        topic: str,
        word_count_target: int,
        patterns: Dict[str, Any],
        scoring_matrix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of article quality using the 4-category scoring system.
        
        Args:
            complete_article: The complete article to evaluate
            topic: Article topic for context
            word_count_target: Target word count
            patterns: Pattern validation data from Google Sheets
            scoring_matrix: Scoring criteria and weights
            
        Returns:
            Complete evaluation results with scores and recommendations
        """
        try:
            logger.info(f"Starting article quality evaluation for topic: {topic}")
            
            # Use OpenRouter for AI-powered evaluation
            evaluation = await openrouter_service.evaluate_article_quality(
                complete_article=complete_article,
                topic=topic,
                word_count_target=word_count_target,
                patterns=patterns,
                scoring_matrix=scoring_matrix
            )
            
            # Convert to dictionary for MCP return
            evaluation_dict = {
                "total_score": evaluation.total_score,
                "score_breakdown": {
                    "voice_consistency": evaluation.score_breakdown.voice_consistency,
                    "structure_quality": evaluation.score_breakdown.structure_quality,
                    "medical_accuracy": evaluation.score_breakdown.medical_accuracy,
                    "seo_technical": evaluation.score_breakdown.seo_technical
                },
                "word_count_actual": evaluation.word_count_actual,
                "word_count_target": evaluation.word_count_target,
                "word_count_deviation_percent": evaluation.word_count_deviation_percent,
                "critical_issues": evaluation.critical_issues,
                "improvements_needed": evaluation.improvements_needed,
                "passes_quality_gate": evaluation.passes_quality_gate,
                "retry_count": evaluation.retry_count,
                "voice_analysis": evaluation.voice_analysis,
                "structure_analysis": evaluation.structure_analysis,
                "medical_analysis": evaluation.medical_analysis,
                "seo_analysis": evaluation.seo_analysis
            }
            
            logger.info(f"Article evaluation completed: {evaluation.total_score}/100")
            return evaluation_dict
            
        except Exception as e:
            logger.error(f"Error evaluating article quality: {e}")
            raise
    
    @mcp.tool()
    async def evaluate_with_local_scoring(
        complete_article: str,
        topic: str,
        word_count_target: int,
        patterns: Dict[str, Any],
        scoring_matrix: Dict[str, Any],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Evaluate article using local scoring engine (faster, more deterministic).
        
        Args:
            complete_article: Article content to evaluate
            topic: Article topic
            word_count_target: Target word count
            patterns: Pattern data
            scoring_matrix: Scoring criteria
            retry_count: Current retry count
            
        Returns:
            Evaluation results using local scoring
        """
        try:
            logger.info(f"Starting local scoring evaluation for: {topic}")
            
            # Initialize local scoring engine
            scoring_engine = ScoringEngine(scoring_matrix)
            
            # Perform evaluation
            evaluation = scoring_engine.evaluate_article(
                article_content=complete_article,
                target_word_count=word_count_target,
                topic=topic,
                retry_count=retry_count
            )
            
            # Convert to dictionary
            evaluation_dict = {
                "total_score": evaluation.total_score,
                "score_breakdown": {
                    "voice_consistency": evaluation.score_breakdown.voice_consistency,
                    "structure_quality": evaluation.score_breakdown.structure_quality,
                    "medical_accuracy": evaluation.score_breakdown.medical_accuracy,
                    "seo_technical": evaluation.score_breakdown.seo_technical
                },
                "word_count_actual": evaluation.word_count_actual,
                "word_count_target": evaluation.word_count_target,
                "word_count_deviation_percent": evaluation.word_count_deviation_percent,
                "critical_issues": evaluation.critical_issues,
                "improvements_needed": evaluation.improvements_needed,
                "passes_quality_gate": evaluation.passes_quality_gate,
                "retry_count": evaluation.retry_count,
                "evaluation_method": "local_scoring"
            }
            
            logger.info(f"Local evaluation completed: {evaluation.total_score}/100")
            return evaluation_dict
            
        except Exception as e:
            logger.error(f"Error in local scoring evaluation: {e}")
            raise
    
    @mcp.tool()
    async def validate_content_patterns(
        article_content: str,
        patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate article content against approved patterns and anti-patterns.
        
        Args:
            article_content: Content to validate
            patterns: Pattern data from Google Sheets
            
        Returns:
            Pattern validation results
        """
        try:
            logger.info("Starting content pattern validation")
            
            # Convert pattern data to objects
            approved_patterns = []
            for pattern_data in patterns.get('approved_patterns', []):
                pattern = Pattern(
                    id=pattern_data.get('id', ''),
                    name=pattern_data.get('name', ''),
                    description=pattern_data.get('description', ''),
                    pattern_type=pattern_data.get('pattern_type', 'voice'),
                    examples=pattern_data.get('examples', []),
                    weight=pattern_data.get('weight', 1)
                )
                approved_patterns.append(pattern)
            
            forbidden_patterns = []
            for anti_pattern_data in patterns.get('forbidden_patterns', []):
                anti_pattern = AntiPattern(
                    id=anti_pattern_data.get('id', ''),
                    name=anti_pattern_data.get('name', ''),
                    description=anti_pattern_data.get('description', ''),
                    pattern_type=anti_pattern_data.get('pattern_type', 'voice'),
                    examples=anti_pattern_data.get('examples', []),
                    penalty_points=anti_pattern_data.get('penalty_points', 0),
                    auto_fail=anti_pattern_data.get('auto_fail', False)
                )
                forbidden_patterns.append(anti_pattern)
            
            # Initialize validator
            validator = ContentValidator(approved_patterns, forbidden_patterns)
            
            # Validate content
            validation_result = validator.validate_content(article_content)
            
            # Convert to dictionary
            result_dict = {
                "is_valid": validation_result.is_valid,
                "matched_patterns": validation_result.matched_patterns,
                "violated_antipatterns": validation_result.violated_antipatterns,
                "suggested_fixes": validation_result.suggested_fixes,
                "validation_score": validation_result.validation_score,
                "detailed_feedback": validation_result.detailed_feedback
            }
            
            logger.info(f"Pattern validation completed: {'VALID' if validation_result.is_valid else 'INVALID'}")
            return result_dict
            
        except Exception as e:
            logger.error(f"Error validating content patterns: {e}")
            raise
    
    @mcp.tool()
    async def comprehensive_evaluation(
        complete_article: str,
        topic: str,
        word_count_target: int,
        patterns: Dict[str, Any],
        scoring_matrix: Dict[str, Any],
        use_ai_evaluation: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation combining AI scoring and pattern validation.
        
        Args:
            complete_article: Article to evaluate
            topic: Article topic
            word_count_target: Target word count
            patterns: Pattern data
            scoring_matrix: Scoring criteria
            use_ai_evaluation: Whether to use AI evaluation (vs local only)
            
        Returns:
            Combined evaluation results
        """
        try:
            logger.info(f"Starting comprehensive evaluation for: {topic}")
            
            # Perform both evaluations in parallel
            if use_ai_evaluation:
                ai_eval_task = evaluate_article_quality(
                    complete_article, topic, word_count_target, patterns, scoring_matrix
                )
            else:
                ai_eval_task = evaluate_with_local_scoring(
                    complete_article, topic, word_count_target, patterns, scoring_matrix
                )
            
            pattern_validation_task = validate_content_patterns(complete_article, patterns)
            
            # Wait for both to complete
            import asyncio
            ai_evaluation, pattern_validation = await asyncio.gather(
                ai_eval_task,
                pattern_validation_task,
                return_exceptions=True
            )
            
            # Check for exceptions
            if isinstance(ai_evaluation, Exception):
                raise ai_evaluation
            if isinstance(pattern_validation, Exception):
                raise pattern_validation
            
            # Combine results
            combined_evaluation = {
                "ai_evaluation": ai_evaluation,
                "pattern_validation": pattern_validation,
                "combined_score": _calculate_combined_score(ai_evaluation, pattern_validation),
                "final_recommendation": _generate_final_recommendation(ai_evaluation, pattern_validation),
                "evaluation_summary": {
                    "ai_score": ai_evaluation["total_score"],
                    "pattern_score": pattern_validation["validation_score"],
                    "passes_ai_gate": ai_evaluation["passes_quality_gate"],
                    "passes_pattern_validation": pattern_validation["is_valid"],
                    "critical_issues_count": len(ai_evaluation["critical_issues"]),
                    "pattern_violations_count": len(pattern_validation["violated_antipatterns"])
                }
            }
            
            logger.info("Comprehensive evaluation completed")
            return combined_evaluation
            
        except Exception as e:
            logger.error(f"Error in comprehensive evaluation: {e}")
            raise
    
    @mcp.tool()
    async def quick_quality_check(
        article_content: str,
        target_word_count: int
    ) -> Dict[str, Any]:
        """
        Perform quick quality checks without full evaluation (for rapid feedback).
        
        Args:
            article_content: Article content
            target_word_count: Target word count
            
        Returns:
            Quick quality assessment
        """
        try:
            logger.info("Performing quick quality check")
            
            # Basic metrics
            actual_word_count = len(article_content.split())
            word_count_deviation = ((actual_word_count - target_word_count) / target_word_count) * 100
            
            # Quick checks
            issues = []
            warnings = []
            
            # Word count check
            if word_count_deviation < -15:
                issues.append("Word count critically low")
            elif word_count_deviation < -5:
                warnings.append("Word count below target")
            
            # Structure check
            if not article_content.startswith('#'):
                issues.append("Missing H1 header")
            
            h2_count = article_content.count('\n##')
            if h2_count < 3:
                warnings.append("Few sections detected")
            
            # Voice check
            first_person_indicators = [' εγώ ', ' με ', ' μου ']
            if any(indicator in article_content.lower() for indicator in first_person_indicators):
                issues.append("First person usage detected")
            
            # Signature check
            if "Δρ. Γεώργιος Χλωρός" not in article_content:
                issues.append("Missing required signature")
            
            # Calculate quick score
            base_score = 100
            base_score -= len(issues) * 15  # Major penalty for issues
            base_score -= len(warnings) * 5  # Minor penalty for warnings
            quick_score = max(0, base_score)
            
            result = {
                "quick_score": quick_score,
                "word_count_actual": actual_word_count,
                "word_count_deviation": word_count_deviation,
                "issues": issues,
                "warnings": warnings,
                "passes_quick_check": len(issues) == 0,
                "structure_metrics": {
                    "h1_count": 1 if article_content.startswith('#') else 0,
                    "h2_count": h2_count,
                    "paragraph_count": len(article_content.split('\n\n'))
                }
            }
            
            logger.info(f"Quick quality check completed: {quick_score}/100")
            return result
            
        except Exception as e:
            logger.error(f"Error in quick quality check: {e}")
            raise
    
    logger.info("Phase 3 evaluation tools registered successfully")


def _calculate_combined_score(ai_evaluation: Dict[str, Any], pattern_validation: Dict[str, Any]) -> int:
    """Calculate combined score from AI evaluation and pattern validation."""
    ai_score = ai_evaluation["total_score"]
    pattern_score = pattern_validation["validation_score"]
    
    # Weighted combination (70% AI, 30% patterns)
    combined_score = int(ai_score * 0.7 + pattern_score * 0.3)
    
    # Apply penalties for critical violations
    if not pattern_validation["is_valid"]:
        combined_score = max(0, combined_score - 10)
    
    return min(100, combined_score)


def _generate_final_recommendation(ai_evaluation: Dict[str, Any], pattern_validation: Dict[str, Any]) -> str:
    """Generate final recommendation based on both evaluations."""
    ai_passes = ai_evaluation["passes_quality_gate"]
    pattern_passes = pattern_validation["is_valid"]
    ai_score = ai_evaluation["total_score"]
    
    if ai_passes and pattern_passes:
        return "PUBLISH - Article meets all quality standards"
    elif ai_score >= 70 and pattern_passes:
        return "REVIEW - Good quality but minor improvements recommended"
    elif ai_score >= 60:
        return "RETRY - Significant improvements needed"
    else:
        return "MAJOR_REVISION - Substantial rewrite required"
