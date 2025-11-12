"""
Chloros Blog MCP Server - Clean, Railway-compatible implementation
"""

import asyncio
import logging
import os
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Chloros Blog MCP Server")


@mcp.tool()
async def medical_research_query(
    topic: str,
    main_keywords: str,
    secondary_keywords: str
) -> dict:
    """Query Pinecone for medical research facts."""
    try:
        from .services.openai_service import OpenAIService
        from .services.pinecone_service import PineconeService
        
        openai_service = OpenAIService()
        pinecone_service = PineconeService()
        
        # Create query embedding
        query_text = f"{topic} {main_keywords} {secondary_keywords}"
        embedding = await openai_service.create_embeddings(query_text)
        
        # Search medical knowledge
        results = await pinecone_service.search_by_topic(
            topic=topic,
            query_embedding=embedding,
            main_keywords=main_keywords,
            secondary_keywords=secondary_keywords
        )
        
        logger.info(f"Medical research completed: {results['total_results']} results")
        return results
        
    except Exception as e:
        logger.error(f"Medical research error: {e}")
        raise


@mcp.tool()
async def cultural_context_research(topic: str) -> dict:
    """Research Greek cultural context via Perplexity."""
    try:
        from .services.perplexity_service import PerplexityService
        
        perplexity_service = PerplexityService()
        result = await perplexity_service.research_cultural_context(topic)
        
        logger.info("Cultural context research completed")
        return result
        
    except Exception as e:
        logger.error(f"Cultural research error: {e}")
        raise


@mcp.tool()
async def read_blog_patterns() -> dict:
    """Read blog patterns from Google Sheets."""
    try:
        from .services.google_service import GoogleService
        
        google_service = GoogleService()
        patterns = await google_service.read_blog_patterns()
        
        logger.info("Blog patterns read successfully")
        return patterns
        
    except Exception as e:
        logger.error(f"Pattern reading error: {e}")
        raise


@mcp.tool()
async def create_content_strategy(
    topic: str,
    main_keywords: str,
    secondary_keywords: str,
    target_word_count: int,
    medical_facts: str,
    cultural_context: str
) -> dict:
    """Create content strategy using OpenAI."""
    try:
        from .services.openai_service import OpenAIService
        
        openai_service = OpenAIService()
        strategy = await openai_service.create_content_strategy(
            topic=topic,
            main_keywords=main_keywords,
            secondary_keywords=secondary_keywords,
            target_word_count=target_word_count,
            negative_keywords="",
            medical_facts=medical_facts,
            cultural_context=cultural_context,
            approved_structure=[]
        )
        
        # Convert to dict for MCP
        return {
            "h1_title": strategy.h1_title,
            "content_sections": [
                {
                    "title": s.title,
                    "content_points": s.content_points,
                    "target_words": s.target_words,
                    "medical_focus": s.medical_focus
                }
                for s in strategy.content_sections
            ],
            "seo_strategy": {
                "main_keyword_placement": strategy.seo_strategy.main_keyword_placement,
                "secondary_distribution": strategy.seo_strategy.secondary_distribution
            },
            "medical_focus": strategy.medical_focus,
            "target_word_count": strategy.target_word_count
        }
        
    except Exception as e:
        logger.error(f"Strategy creation error: {e}")
        raise


@mcp.tool()
async def generate_complete_article(
    strategy: dict,
    medical_facts: str,
    cultural_context: str,
    patterns: dict
) -> dict:
    """Generate complete article using OpenRouter."""
    try:
        from .services.openrouter_service import OpenRouterService
        from .models.content import ContentStrategy, Section, SEOStrategy, ContentRestrictions
        
        # Convert strategy dict to ContentStrategy object
        sections = []
        for section_data in strategy.get("content_sections", []):
            section = Section(
                title=section_data["title"],
                content_points=section_data["content_points"],
                target_words=section_data.get("target_words"),
                medical_focus=section_data.get("medical_focus")
            )
            sections.append(section)
        
        content_strategy = ContentStrategy(
            h1_title=strategy["h1_title"],
            content_sections=sections,
            seo_strategy=SEOStrategy(
                main_keyword_placement=strategy["seo_strategy"]["main_keyword_placement"],
                secondary_distribution=strategy["seo_strategy"]["secondary_distribution"]
            ),
            content_restrictions=ContentRestrictions(
                avoid=["emotional stories"],
                alternatives=["evidence-based examples"],
                voice_requirements=["third person"]
            ),
            medical_focus=strategy["medical_focus"],
            target_word_count=strategy["target_word_count"]
        )
        
        openrouter_service = OpenRouterService()
        article = await openrouter_service.generate_complete_article(
            strategy=content_strategy,
            medical_facts=medical_facts,
            cultural_context=cultural_context,
            patterns=patterns
        )
        
        return {
            "article_markdown": article.article_markdown,
            "word_count": article.word_count,
            "h1_title": article.h1_title
        }
        
    except Exception as e:
        logger.error(f"Article generation error: {e}")
        raise


@mcp.tool()
async def evaluate_article_quality(
    article_content: str,
    topic: str,
    target_word_count: int
) -> dict:
    """Evaluate article quality with scoring system."""
    try:
        from .utils.scoring_engine import ScoringEngine
        
        scoring_engine = ScoringEngine({})
        evaluation = scoring_engine.evaluate_article(
            article_content=article_content,
            target_word_count=target_word_count,
            topic=topic
        )
        
        return {
            "total_score": evaluation.total_score,
            "passes_quality_gate": evaluation.passes_quality_gate,
            "word_count_actual": evaluation.word_count_actual,
            "word_count_deviation_percent": evaluation.word_count_deviation_percent,
            "critical_issues": evaluation.critical_issues,
            "improvements_needed": evaluation.improvements_needed,
            "score_breakdown": {
                "voice_consistency": evaluation.score_breakdown.voice_consistency,
                "structure_quality": evaluation.score_breakdown.structure_quality,
                "medical_accuracy": evaluation.score_breakdown.medical_accuracy,
                "seo_technical": evaluation.score_breakdown.seo_technical
            }
        }
        
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        raise


@mcp.tool()
async def create_google_doc(
    article_markdown: str,
    title: str,
    status: str
) -> dict:
    """Create Google Doc from article."""
    try:
        from .services.google_service import GoogleService
        
        google_service = GoogleService()
        result = await google_service.create_google_doc(
            article_markdown=article_markdown,
            title=title,
            status=status
        )
        
        logger.info(f"Google Doc created: {result['doc_url']}")
        return result
        
    except Exception as e:
        logger.error(f"Doc creation error: {e}")
        raise


@mcp.tool()
async def complete_article_workflow(
    topic: str,
    main_keywords: str,
    secondary_keywords: str,
    target_word_count: int
) -> dict:
    """Complete end-to-end article creation workflow."""
    try:
        logger.info(f"Starting workflow for: {topic}")
        
        # Phase 1: Research
        medical_research = await medical_research_query(topic, main_keywords, secondary_keywords)
        cultural_research = await cultural_context_research(topic)
        patterns = await read_blog_patterns()
        
        medical_facts = "\n".join(medical_research.get('medical_facts', []))
        cultural_context = cultural_research.get('cultural_insights', '')
        
        # Create strategy
        strategy = await create_content_strategy(
            topic=topic,
            main_keywords=main_keywords,
            secondary_keywords=secondary_keywords,
            target_word_count=target_word_count,
            medical_facts=medical_facts,
            cultural_context=cultural_context
        )
        
        # Phase 2: Generate article
        article = await generate_complete_article(
            strategy=strategy,
            medical_facts=medical_facts,
            cultural_context=cultural_context,
            patterns=patterns
        )
        
        # Phase 3: Evaluate
        evaluation = await evaluate_article_quality(
            article_content=article["article_markdown"],
            topic=topic,
            target_word_count=target_word_count
        )
        
        # Phase 4: Publish if quality passes
        result = {
            "topic": topic,
            "article": article,
            "evaluation": evaluation,
            "workflow_completed": True
        }
        
        if evaluation["passes_quality_gate"]:
            doc_result = await create_google_doc(
                article_markdown=article["article_markdown"],
                title=topic,
                status="PASS"
            )
            result["google_doc"] = doc_result
            result["status"] = "PUBLISHED"
        else:
            result["status"] = "NEEDS_REVIEW"
        
        logger.info(f"Workflow completed: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        raise


def main():
    """Main entry point for Railway-compatible MCP server."""
    try:
        # Setup server
        asyncio.run(setup_server())
        
        # Log environment info
        is_railway = bool(os.getenv('RAILWAY_PROJECT_ID'))
        logger.info(f"Environment: {'Railway' if is_railway else 'Local'}")
        logger.info("🚀 MCP Server ready - connect via MCP protocol")
        
        # Start MCP server
        mcp.run()
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


async def setup_server():
    """Setup MCP server with all tools."""
    logger.info("Initializing Chloros Blog MCP Server...")
    logger.info("✅ All MCP tools registered")
    logger.info("🎉 Ready for blog automation!")


if __name__ == "__main__":
    main()