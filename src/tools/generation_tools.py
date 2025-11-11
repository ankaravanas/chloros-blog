"""
Phase 2 content generation tools.
Implements complete article generation with comprehensive Greek prompts.
"""

import logging
from typing import Dict, Any, Optional
from typing import List  # Separate import for Railway compatibility
from fastmcp import FastMCP

from ..services.openrouter_service import OpenRouterService
from ..models.content import ContentStrategy, Article
from ..models.evaluation import Evaluation

logger = logging.getLogger(__name__)

# Service instance
openrouter_service = OpenRouterService()


async def register_generation_tools(mcp: FastMCP):
    """Register all Phase 2 generation tools with the MCP server."""
    
    @mcp.tool()
    async def generate_complete_article(
        strategy: Dict[str, Any],
        medical_facts: str,
        cultural_context: str,
        patterns: Dict[str, Any],
        retry_count: int = 0,
        previous_evaluation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete article using OpenRouter and the content strategy.
        
        Args:
            strategy: Content strategy dictionary from Phase 1
            medical_facts: Medical research facts from Pinecone
            cultural_context: Cultural context from Perplexity
            patterns: Blog patterns from Google Sheets
            retry_count: Current retry attempt number
            previous_evaluation: Previous evaluation results if retrying
            
        Returns:
            Complete generated article with metadata
        """
        try:
            logger.info(f"Starting article generation (attempt {retry_count + 1})")
            
            # Convert strategy dictionary back to ContentStrategy object
            content_strategy = _dict_to_content_strategy(strategy)
            
            # Convert previous evaluation if provided
            prev_eval = None
            if previous_evaluation:
                prev_eval = _dict_to_evaluation(previous_evaluation)
            
            # Generate the article
            article = await openrouter_service.generate_complete_article(
                strategy=content_strategy,
                medical_facts=medical_facts,
                cultural_context=cultural_context,
                patterns=patterns,
                retry_count=retry_count,
                previous_evaluation=prev_eval
            )
            
            # Convert to dictionary for MCP return
            article_dict = {
                "article_markdown": article.article_markdown,
                "word_count": article.word_count,
                "sections_generated": article.sections_generated,
                "h1_title": article.h1_title,
                "generation_metadata": article.generation_metadata
            }
            
            logger.info(f"Article generation completed: {article.word_count} words")
            return article_dict
            
        except Exception as e:
            logger.error(f"Error generating article: {e}")
            raise
    
    @mcp.tool()
    async def generate_article_with_validation(
        strategy: Dict[str, Any],
        medical_facts: str,
        cultural_context: str,
        patterns: Dict[str, Any],
        target_word_count: int,
        topic: str
    ) -> Dict[str, Any]:
        """
        Generate article and immediately validate for basic quality checks.
        
        Args:
            strategy: Content strategy dictionary
            medical_facts: Medical research facts
            cultural_context: Cultural context
            patterns: Blog patterns
            target_word_count: Target word count for validation
            topic: Article topic for context
            
        Returns:
            Article with basic validation results
        """
        try:
            logger.info(f"Starting article generation with validation for: {topic}")
            
            # Generate the article
            article_result = await generate_complete_article(
                strategy=strategy,
                medical_facts=medical_facts,
                cultural_context=cultural_context,
                patterns=patterns
            )
            
            # Perform basic validation
            validation_results = _perform_basic_validation(
                article_result, target_word_count, topic
            )
            
            # Combine results
            complete_result = {
                **article_result,
                "basic_validation": validation_results,
                "validation_passed": validation_results["passes_basic_checks"],
                "validation_warnings": validation_results["warnings"]
            }
            
            logger.info(f"Article generation with validation completed")
            return complete_result
            
        except Exception as e:
            logger.error(f"Error in article generation with validation: {e}")
            raise
    
    @mcp.tool()
    async def regenerate_article_section(
        original_article: str,
        section_title: str,
        new_content_points: list,
        medical_facts: str,
        patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Regenerate a specific section of an article while keeping the rest intact.
        
        Args:
            original_article: The original complete article
            section_title: Title of the section to regenerate
            new_content_points: New content points for the section
            medical_facts: Medical facts for accuracy
            patterns: Pattern guidelines
            
        Returns:
            Updated article with regenerated section
        """
        try:
            logger.info(f"Regenerating section: {section_title}")
            
            # Split article into sections
            sections = _split_article_into_sections(original_article)
            
            # Find the target section
            target_section_index = None
            for i, section in enumerate(sections):
                if section_title.lower() in section.get('title', '').lower():
                    target_section_index = i
                    break
            
            if target_section_index is None:
                raise ValueError(f"Section '{section_title}' not found in article")
            
            # Generate new section content
            new_section_content = await _generate_section_content(
                section_title, new_content_points, medical_facts, patterns
            )
            
            # Replace the section
            sections[target_section_index]['content'] = new_section_content
            
            # Reassemble the article
            updated_article = _reassemble_article_from_sections(sections)
            
            # Calculate new word count
            word_count = len(updated_article.split())
            
            result = {
                "updated_article": updated_article,
                "word_count": word_count,
                "regenerated_section": section_title,
                "sections_total": len(sections)
            }
            
            logger.info(f"Section regeneration completed")
            return result
            
        except Exception as e:
            logger.error(f"Error regenerating article section: {e}")
            raise
    
    logger.info("Phase 2 generation tools registered successfully")


def _dict_to_content_strategy(strategy_dict: Dict[str, Any]) -> ContentStrategy:
    """Convert strategy dictionary back to ContentStrategy object."""
    from ..models.content import Section, SEOStrategy, ContentRestrictions
    
    # Convert sections
    sections = []
    for section_data in strategy_dict.get("content_sections", []):
        section = Section(
            title=section_data["title"],
            content_points=section_data["content_points"],
            target_words=section_data.get("target_words"),
            medical_focus=section_data.get("medical_focus")
        )
        sections.append(section)
    
    # Convert SEO strategy
    seo_strategy = SEOStrategy(
        main_keyword_placement=strategy_dict["seo_strategy"]["main_keyword_placement"],
        secondary_distribution=strategy_dict["seo_strategy"]["secondary_distribution"]
    )
    
    # Convert content restrictions
    restrictions = ContentRestrictions(
        avoid=strategy_dict["content_restrictions"]["avoid"],
        alternatives=strategy_dict["content_restrictions"]["alternatives"],
        voice_requirements=strategy_dict["content_restrictions"]["voice_requirements"]
    )
    
    # Create complete strategy
    return ContentStrategy(
        h1_title=strategy_dict["h1_title"],
        content_sections=sections,
        seo_strategy=seo_strategy,
        content_restrictions=restrictions,
        medical_focus=strategy_dict["medical_focus"],
        target_word_count=strategy_dict["target_word_count"],
        cultural_context=strategy_dict.get("cultural_context")
    )


def _dict_to_evaluation(eval_dict: Dict[str, Any]) -> Evaluation:
    """Convert evaluation dictionary back to Evaluation object."""
    from ..models.evaluation import ScoreBreakdown
    
    score_breakdown = ScoreBreakdown(
        voice_consistency=eval_dict["score_breakdown"]["voice_consistency"],
        structure_quality=eval_dict["score_breakdown"]["structure_quality"],
        medical_accuracy=eval_dict["score_breakdown"]["medical_accuracy"],
        seo_technical=eval_dict["score_breakdown"]["seo_technical"]
    )
    
    return Evaluation(
        total_score=eval_dict["total_score"],
        score_breakdown=score_breakdown,
        word_count_actual=eval_dict["word_count_actual"],
        word_count_target=eval_dict["word_count_target"],
        word_count_deviation_percent=eval_dict["word_count_deviation_percent"],
        critical_issues=eval_dict["critical_issues"],
        improvements_needed=eval_dict["improvements_needed"],
        passes_quality_gate=eval_dict["passes_quality_gate"],
        retry_count=eval_dict.get("retry_count", 0)
    )


def _perform_basic_validation(
    article_result: Dict[str, Any], 
    target_word_count: int, 
    topic: str
) -> Dict[str, Any]:
    """Perform basic validation checks on generated article."""
    article_content = article_result["article_markdown"]
    actual_word_count = article_result["word_count"]
    
    warnings = []
    issues = []
    
    # Word count check
    word_count_deviation = ((actual_word_count - target_word_count) / target_word_count) * 100
    if word_count_deviation < -15:
        issues.append(f"Word count critically low: {word_count_deviation:.1f}% below target")
    elif word_count_deviation < -5:
        warnings.append(f"Word count below target: {word_count_deviation:.1f}%")
    
    # Basic structure check
    if not article_content.startswith('#'):
        issues.append("Article does not start with H1 header")
    
    h2_count = article_content.count('\n##')
    if h2_count < 3:
        warnings.append(f"Few sections found: only {h2_count} H2 headers")
    
    # Basic voice check (simplified)
    first_person_indicators = [' εγώ ', ' με ', ' μου ', ' μας ']
    first_person_found = any(indicator in article_content.lower() for indicator in first_person_indicators)
    if first_person_found:
        issues.append("First person usage detected (should use third person)")
    
    # Signature check
    if "Δρ. Γεώργιος Χλωρός" not in article_content:
        issues.append("Required signature missing")
    
    # Basic markdown formatting check
    if '**' not in article_content:
        warnings.append("No bold text found - consider adding emphasis")
    
    passes_basic_checks = len(issues) == 0
    
    return {
        "passes_basic_checks": passes_basic_checks,
        "issues": issues,
        "warnings": warnings,
        "word_count_deviation": word_count_deviation,
        "structure_analysis": {
            "h1_count": article_content.count('\n#') + (1 if article_content.startswith('#') else 0),
            "h2_count": h2_count,
            "h3_count": article_content.count('\n###'),
            "bold_text_count": article_content.count('**') // 2
        }
    }


def _split_article_into_sections(article: str) -> List[Dict[str, Any]]:
    """Split article into sections for targeted regeneration."""
    sections = []
    lines = article.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        if line.startswith('##') and not line.startswith('###'):
            # Save previous section
            if current_section:
                sections.append({
                    'title': current_section,
                    'content': '\n'.join(current_content)
                })
            
            # Start new section
            current_section = line.replace('##', '').strip()
            current_content = []
        elif line.startswith('#') and not line.startswith('##'):
            # H1 title - add as introduction section
            if current_section is None:
                current_section = "Introduction"
                current_content = [line]
        else:
            current_content.append(line)
    
    # Add final section
    if current_section:
        sections.append({
            'title': current_section,
            'content': '\n'.join(current_content)
        })
    
    return sections


async def _generate_section_content(
    section_title: str,
    content_points: List[str],
    medical_facts: str,
    patterns: Dict[str, Any]
) -> str:
    """Generate content for a specific section."""
    # This would use OpenRouter to generate just the section content
    # Simplified implementation for now
    content_lines = [f"## {section_title}", ""]
    
    for point in content_points:
        content_lines.append(f"**{point}**")
        content_lines.append("")
        content_lines.append("Περιεχόμενο για αυτό το σημείο θα δημιουργηθεί βάσει των ιατρικών δεδομένων.")
        content_lines.append("")
    
    return '\n'.join(content_lines)


def _reassemble_article_from_sections(sections: List[Dict[str, Any]]) -> str:
    """Reassemble article from sections."""
    article_parts = []
    
    for section in sections:
        if section['title'] == "Introduction":
            # Introduction section includes H1
            article_parts.append(section['content'])
        else:
            # Regular sections
            article_parts.append(f"## {section['title']}")
            article_parts.append(section['content'])
        
        article_parts.append("")  # Add spacing between sections
    
    return '\n'.join(article_parts)
