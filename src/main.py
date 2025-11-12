"""
Chloros Blog MCP Server - Railway Compatible
"""

import asyncio
import logging
import os
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Chloros Blog MCP Server")


@mcp.tool()
async def search_pinecone_medical(topic: str, keywords: str) -> dict:
    """Step 3: Search Pinecone medical database for research facts."""
    try:
        from .services.openai_service import OpenAIService
        from .services.pinecone_service import PineconeService
        
        openai_service = OpenAIService()
        pinecone_service = PineconeService()
        
        # Create embedding and search
        embedding = await openai_service.create_embeddings(f"{topic} {keywords}")
        results = await pinecone_service.search_medical_knowledge(embedding, top_k=10)
        
        return {
            "topic": topic,
            "results_count": len(results),
            "medical_facts": [r.get('content', '') for r in results[:5]]
        }
    except Exception as e:
        logger.error(f"Medical research error: {e}")
        return {"error": str(e), "medical_facts": []}


@mcp.tool()
async def cultural_context_research(topic: str) -> dict:
    """Step 1: Research Greek cultural context for medical topic."""
    try:
        from .services.perplexity_service import PerplexityService
        
        service = PerplexityService()
        result = await service.research_cultural_context(topic)
        
        return {
            "topic": topic,
            "cultural_insights": result.get("cultural_insights", ""),
            "patient_concerns": result.get("patient_concerns", [])
        }
    except Exception as e:
        logger.error(f"Cultural research error: {e}")
        return {"error": str(e), "cultural_insights": ""}


@mcp.tool()
async def read_blog_patterns() -> dict:
    """Step 2: Read all patterns, structure, scoring matrix, and fixes from Google Sheets."""
    try:
        from .services.google_service import GoogleService
        
        service = GoogleService()
        patterns = await service.read_blog_patterns()
        
        return {
            "approved_patterns": patterns.get("approved_patterns", []),
            "forbidden_patterns": patterns.get("forbidden_patterns", []),
            "approved_structure": patterns.get("approved_structure", []),
            "scoring_matrix": patterns.get("scoring_matrix", []),
            "specific_fixes": patterns.get("specific_fixes", []),
            "total_patterns": len(patterns.get("approved_patterns", [])),
            "total_structures": len(patterns.get("approved_structure", [])),
            "scoring_criteria": len(patterns.get("scoring_matrix", []))
        }
    except Exception as e:
        logger.error(f"Pattern reading error: {e}")
        return {
            "error": str(e), 
            "approved_patterns": [], 
            "forbidden_patterns": [],
            "approved_structure": [],
            "scoring_matrix": [],
            "specific_fixes": []
        }


@mcp.tool()
async def create_content_strategy(
    topic: str,
    keywords: str,
    target_words: int,
    medical_facts: str,
    cultural_context: str,
    patterns: str
) -> dict:
    """Step 4: Create content strategy based on research."""
    try:
        from .services.openai_service import OpenAIService
        
        service = OpenAIService()
        strategy = await service.create_content_strategy(
            topic=topic,
            main_keywords=keywords,
            secondary_keywords="",
            target_word_count=target_words,
            negative_keywords="",
            medical_facts=medical_facts,
            cultural_context=cultural_context,
            approved_structure=[]
        )
        
        return {
            "h1_title": strategy.h1_title,
            "sections": [
                {
                    "title": s.title,
                    "points": s.content_points,
                    "words": s.target_words
                }
                for s in strategy.content_sections
            ],
            "medical_focus": strategy.medical_focus,
            "target_words": strategy.target_word_count
        }
    except Exception as e:
        logger.error(f"Strategy creation error: {e}")
        return {"error": str(e), "h1_title": f"Άρθρο για {topic}"}


@mcp.tool()
async def generate_blog_post(
    topic: str,
    target_words: int,
    medical_facts: str,
    cultural_context: str,
    strategy: str
) -> dict:
    """Step 5: Generate complete Greek medical blog post."""
    try:
        from .services.openrouter_service import OpenRouterService
        from .models.content import ContentStrategy, Section, SEOStrategy, ContentRestrictions
        
        # Create simple strategy
        section = Section(
            title="Κύριο Περιεχόμενο",
            content_points=[f"Πληροφορίες για {topic}", "Ιατρικές λεπτομέρειες"],
            target_words=target_words
        )
        
        strategy = ContentStrategy(
            h1_title=f"Οδηγός για {topic}",
            content_sections=[section],
            seo_strategy=SEOStrategy(
                main_keyword_placement=["H1", "first paragraph"],
                secondary_distribution=["section 2"]
            ),
            content_restrictions=ContentRestrictions(
                avoid=["emotional stories"],
                alternatives=["evidence-based content"],
                voice_requirements=["third person"]
            ),
            medical_focus=[topic],
            target_word_count=target_words
        )
        
        service = OpenRouterService()
        article = await service.generate_complete_article(
            strategy=strategy,
            medical_facts=medical_facts,
            cultural_context=cultural_context,
            patterns={}
        )
        
        return {
            "topic": topic,
            "article_markdown": article.article_markdown,
            "word_count": article.word_count,
            "h1_title": article.h1_title
        }
        
    except Exception as e:
        logger.error(f"Article generation error: {e}")
        return {"error": str(e), "article_markdown": f"# {topic}\n\nΣφάλμα στη δημιουργία άρθρου."}


@mcp.tool()
async def evaluate_article(article_content: str, target_words: int) -> dict:
    """Step 6: Evaluate article quality with 4-category scoring system."""
    try:
        from .utils.scoring_engine import ScoringEngine
        
        engine = ScoringEngine({})
        evaluation = engine.evaluate_article(article_content, target_words, "Medical Topic")
        
        return {
            "total_score": evaluation.total_score,
            "word_count": evaluation.word_count_actual,
            "passes_quality": evaluation.passes_quality_gate,
            "critical_issues": evaluation.critical_issues,
            "improvements": evaluation.improvements_needed
        }
        
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return {"error": str(e), "total_score": 0}


@mcp.tool()
async def export_to_google_doc(
    article_markdown: str,
    title: str,
    quality_score: int
) -> dict:
    """Step 7: Export article to Google Doc in Drive folder."""
    try:
        from .services.google_service import GoogleService
        
        service = GoogleService()
        status = "PASS" if quality_score >= 80 else "FAIL"
        
        result = await service.create_google_doc(
            article_markdown=article_markdown,
            title=title,
            status=status
        )
        
        return {
            "doc_id": result["doc_id"],
            "doc_url": result["doc_url"],
            "status": status,
            "quality_score": quality_score
        }
    except Exception as e:
        logger.error(f"Google Doc export error: {e}")
        return {"error": str(e), "doc_url": ""}


# Complete workflow tool removed - use individual steps instead


def main():
    """Main entry point."""
    try:
        logger.info("🚀 Starting Chloros Blog MCP Server")
        
        # Check environment
        is_railway = bool(os.getenv('RAILWAY_PROJECT_ID'))
        port = int(os.getenv('PORT', 3000))
        
        if is_railway:
            logger.info(f"Railway deployment detected - starting HTTP server on port {port}")
            # For Railway, run HTTP server
            import uvicorn
            app = mcp.http_app()
            uvicorn.run(app, host="0.0.0.0", port=port)
        else:
            logger.info("Local development - starting MCP stdio server")
            # For local, run stdio
            mcp.run()
            
    except Exception as e:
        logger.error(f"Server startup error: {e}")
        raise


if __name__ == "__main__":
    main()