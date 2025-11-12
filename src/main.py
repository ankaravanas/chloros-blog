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
async def medical_research_query(topic: str, keywords: str) -> dict:
    """Query medical research database for topic."""
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
    """Research Greek cultural context for medical topic."""
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
async def generate_article(
    topic: str,
    target_words: int,
    medical_facts: str,
    cultural_context: str
) -> dict:
    """Generate complete Greek medical article."""
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
    """Evaluate article quality."""
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
async def create_blog_article(
    topic: str,
    keywords: str,
    target_words: int = 2000
) -> dict:
    """Complete blog article creation workflow."""
    try:
        logger.info(f"Creating blog article for: {topic}")
        
        # Step 1: Research
        medical_research = await medical_research_query(topic, keywords)
        cultural_research = await cultural_context_research(topic)
        
        # Step 2: Generate
        article = await generate_article(
            topic=topic,
            target_words=target_words,
            medical_facts="\n".join(medical_research.get("medical_facts", [])),
            cultural_context=cultural_research.get("cultural_insights", "")
        )
        
        # Step 3: Evaluate
        evaluation = await evaluate_article(
            article_content=article.get("article_markdown", ""),
            target_words=target_words
        )
        
        # Step 4: Create Google Doc if quality passes
        result = {
            "topic": topic,
            "article": article,
            "evaluation": evaluation,
            "workflow_completed": True
        }
        
        if evaluation.get("passes_quality", False):
            try:
                from .services.google_service import GoogleService
                google_service = GoogleService()
                doc_result = await google_service.create_google_doc(
                    article_markdown=article.get("article_markdown", ""),
                    title=topic,
                    status="PASS"
                )
                result["google_doc"] = doc_result
                result["status"] = "PUBLISHED"
            except Exception as e:
                logger.warning(f"Google Doc creation failed: {e}")
                result["status"] = "ARTICLE_READY"
        else:
            result["status"] = "NEEDS_IMPROVEMENT"
        
        logger.info(f"Blog article workflow completed: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"Blog creation workflow error: {e}")
        return {"error": str(e), "status": "FAILED"}


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