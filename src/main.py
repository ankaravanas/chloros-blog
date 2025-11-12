"""
Chloros Blog MCP Server - Complete functionality, Railway-compatible
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
    """
    Phase 1: Query Pinecone vector database for medical research.
    
    Args:
        topic: Main medical topic to research
        main_keywords: Primary keywords for the search
        secondary_keywords: Additional relevant keywords
        
    Returns:
        Dictionary with medical facts and citations
    """
    try:
        from .services.openai_service import OpenAIService
        from .services.pinecone_service import PineconeService
        
        logger.info(f"Starting medical research for topic: {topic}")
        
        openai_service = OpenAIService()
        pinecone_service = PineconeService()
        
        # Create query embedding
        query_text = f"{topic} {main_keywords} {secondary_keywords}"
        query_embedding = await openai_service.create_embeddings(query_text)
        
        # Search medical knowledge base
        result = await pinecone_service.search_by_topic(
            topic=topic,
            query_embedding=query_embedding,
            main_keywords=main_keywords,
            secondary_keywords=secondary_keywords
        )
        
        logger.info(f"Medical research completed: {result['total_results']} results found")
        return result
        
    except Exception as e:
        logger.error(f"Error in medical research query: {e}")
        raise


@mcp.tool()
async def cultural_context_research(topic: str) -> dict:
    """
    Phase 1: Research Greek cultural context using Perplexity API.
    
    Args:
        topic: Medical topic to research cultural context for
        
    Returns:
        Dictionary with cultural insights and patient concerns
    """
    try:
        from .services.perplexity_service import PerplexityService
        
        logger.info(f"Starting cultural context research for: {topic}")
        
        perplexity_service = PerplexityService()
        result = await perplexity_service.research_cultural_context(topic)
        
        logger.info("Cultural context research completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in cultural context research: {e}")
        raise


@mcp.tool()
async def read_blog_patterns() -> dict:
    """
    Phase 1: Read blog patterns from Google Sheets.
    
    Returns:
        Dictionary containing all pattern data from Google Sheets
    """
    try:
        from .services.google_service import GoogleService
        
        logger.info("Reading blog patterns from Google Sheets")
        
        google_service = GoogleService()
        patterns_data = await google_service.read_blog_patterns()
        
        logger.info("Blog patterns read successfully")
        return patterns_data
        
    except Exception as e:
        logger.error(f"Error reading blog patterns: {e}")
        raise


@mcp.tool()
async def create_content_strategy(
    topic: str,
    main_keywords: str,
    secondary_keywords: str,
    target_word_count: int,
    negative_keywords: str,
    medical_facts: str,
    cultural_context: str,
    approved_structure: list
) -> dict:
    """
    Phase 1: Create comprehensive content strategy using OpenAI.
    
    Args:
        topic: Main topic of the article
        main_keywords: Primary keywords for SEO
        secondary_keywords: Secondary keywords
        target_word_count: Target word count for the article
        negative_keywords: Keywords to avoid
        medical_facts: Medical facts from research
        cultural_context: Cultural context from research
        approved_structure: Approved structure patterns
        
    Returns:
        Complete content strategy as dictionary
    """
    try:
        from .services.openai_service import OpenAIService
        
        logger.info(f"Creating content strategy for: {topic}")
        
        openai_service = OpenAIService()
        strategy = await openai_service.create_content_strategy(
            topic=topic,
            main_keywords=main_keywords,
            secondary_keywords=secondary_keywords,
            target_word_count=target_word_count,
            negative_keywords=negative_keywords,
            medical_facts=medical_facts,
            cultural_context=cultural_context,
            approved_structure=approved_structure
        )
        
        # Convert to dictionary for MCP return
        strategy_dict = {
            "h1_title": strategy.h1_title,
            "content_sections": [
                {
                    "title": section.title,
                    "content_points": section.content_points,
                    "target_words": section.target_words,
                    "medical_focus": section.medical_focus
                }
                for section in strategy.content_sections
            ],
            "seo_strategy": {
                "main_keyword_placement": strategy.seo_strategy.main_keyword_placement,
                "secondary_distribution": strategy.seo_strategy.secondary_distribution
            },
            "content_restrictions": {
                "avoid": strategy.content_restrictions.avoid,
                "alternatives": strategy.content_restrictions.alternatives,
                "voice_requirements": strategy.content_restrictions.voice_requirements
            },
            "medical_focus": strategy.medical_focus,
            "target_word_count": strategy.target_word_count,
            "cultural_context": strategy.cultural_context
        }
        
        logger.info("Content strategy created successfully")
        return strategy_dict
        
    except Exception as e:
        logger.error(f"Error creating content strategy: {e}")
        raise


@mcp.tool()
async def generate_complete_article(
    strategy: dict,
    medical_facts: str,
    cultural_context: str,
    patterns: dict,
    retry_count: int = 0,
    previous_evaluation: dict = None
) -> dict:
    """
    Phase 2: Generate a complete article using OpenRouter and the content strategy.
    
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
        from .services.openrouter_service import OpenRouterService
        from .models.content import ContentStrategy, Section, SEOStrategy, ContentRestrictions
        
        logger.info(f"Starting article generation (attempt {retry_count + 1})")
        
        # Convert strategy dictionary to ContentStrategy object
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
                avoid=strategy.get("content_restrictions", {}).get("avoid", ["emotional stories"]),
                alternatives=strategy.get("content_restrictions", {}).get("alternatives", ["evidence-based examples"]),
                voice_requirements=strategy.get("content_restrictions", {}).get("voice_requirements", ["third person"])
            ),
            medical_focus=strategy["medical_focus"],
            target_word_count=strategy["target_word_count"]
        )
        
        # Convert previous evaluation if provided
        prev_eval = None
        if previous_evaluation:
            from .models.evaluation import Evaluation, ScoreBreakdown
            score_breakdown = ScoreBreakdown(
                voice_consistency=previous_evaluation.get("score_breakdown", {}).get("voice_consistency", 0),
                structure_quality=previous_evaluation.get("score_breakdown", {}).get("structure_quality", 0),
                medical_accuracy=previous_evaluation.get("score_breakdown", {}).get("medical_accuracy", 0),
                seo_technical=previous_evaluation.get("score_breakdown", {}).get("seo_technical", 0)
            )
            prev_eval = Evaluation(
                total_score=previous_evaluation.get("total_score", 0),
                score_breakdown=score_breakdown,
                word_count_actual=previous_evaluation.get("word_count_actual", 0),
                word_count_target=previous_evaluation.get("word_count_target", 0),
                word_count_deviation_percent=previous_evaluation.get("word_count_deviation_percent", 0),
                critical_issues=previous_evaluation.get("critical_issues", []),
                improvements_needed=previous_evaluation.get("improvements_needed", []),
                passes_quality_gate=previous_evaluation.get("passes_quality_gate", False)
            )
        
        openrouter_service = OpenRouterService()
        article = await openrouter_service.generate_complete_article(
            strategy=content_strategy,
            medical_facts=medical_facts,
            cultural_context=cultural_context,
            patterns=patterns,
            retry_count=retry_count,
            previous_evaluation=prev_eval
        )
        
        # Convert to dictionary
        article_dict = {
            "article_markdown": article.article_markdown,
            "word_count": article.word_count,
            "sections_generated": article.sections_generated,
            "h1_title": article.h1_title
        }
        
        logger.info(f"Article generation completed: {article.word_count} words")
        return article_dict
        
    except Exception as e:
        logger.error(f"Error generating article: {e}")
        raise


@mcp.tool()
async def evaluate_article_quality(
    complete_article: str,
    topic: str,
    word_count_target: int,
    patterns: dict,
    scoring_matrix: dict
) -> dict:
    """
    Phase 3: Comprehensive evaluation of article quality using the 4-category scoring system.
    
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
        from .services.openrouter_service import OpenRouterService
        
        logger.info(f"Starting article quality evaluation for topic: {topic}")
        
        openrouter_service = OpenRouterService()
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
            "retry_count": evaluation.retry_count
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
    retry_count: int = 0
) -> dict:
    """
    Phase 3: Evaluate article using local scoring engine (faster, deterministic).
    
    Args:
        complete_article: Article content to evaluate
        topic: Article topic
        word_count_target: Target word count
        retry_count: Current retry count
        
    Returns:
        Evaluation results using local scoring
    """
    try:
        from .utils.scoring_engine import ScoringEngine
        
        logger.info(f"Starting local scoring evaluation for: {topic}")
        
        scoring_engine = ScoringEngine({})
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
async def create_google_doc(
    article_markdown: str,
    title: str,
    status: str
) -> dict:
    """
    Phase 4: Create a Google Doc from markdown article content.
    
    Args:
        article_markdown: Article content in Markdown format
        title: Base title for the document
        status: "PASS" or "FAIL" status for document naming
        
    Returns:
        Dictionary with doc_id and doc_url
    """
    try:
        from .services.google_service import GoogleService
        
        logger.info(f"Creating Google Doc for: {title}")
        
        google_service = GoogleService()
        result = await google_service.create_google_doc(
            article_markdown=article_markdown,
            title=title,
            status=status
        )
        
        logger.info(f"Google Doc created successfully: {result['doc_url']}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating Google Doc: {e}")
        raise


@mcp.tool()
async def publish_article(
    doc_id: str,
    article_content: str,
    status: str,
    evaluation: dict
) -> dict:
    """
    Phase 4: Publish article by managing folder placement and tracking sheet updates.
    
    Args:
        doc_id: Google Doc ID
        article_content: Article content for reference
        status: "PASS" or "FAIL" status
        evaluation: Evaluation results dictionary
        
    Returns:
        Publication results with status and metadata
    """
    try:
        from .services.google_service import GoogleService
        
        logger.info(f"Publishing article with status: {status}")
        
        google_service = GoogleService()
        result = await google_service.publish_article(
            doc_id=doc_id,
            article_content=article_content,
            status=status,
            evaluation=evaluation
        )
        
        logger.info(f"Article published successfully: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"Error publishing article: {e}")
        raise


@mcp.tool()
async def parallel_research_phase(
    topic: str,
    main_keywords: str,
    secondary_keywords: str,
    target_word_count: int,
    negative_keywords: str = ""
) -> dict:
    """
    Phase 1: Execute all research tasks in parallel for maximum efficiency.
    
    Args:
        topic: Main medical topic
        main_keywords: Primary keywords
        secondary_keywords: Secondary keywords  
        target_word_count: Target word count
        negative_keywords: Keywords to avoid (optional)
        
    Returns:
        Complete research results including strategy
    """
    try:
        logger.info(f"Starting parallel research phase for: {topic}")
        
        # Execute all research tasks in parallel
        medical_task = medical_research_query(topic, main_keywords, secondary_keywords)
        cultural_task = cultural_context_research(topic)
        patterns_task = read_blog_patterns()
        
        # Wait for all research to complete
        medical_results, cultural_results, patterns_data = await asyncio.gather(
            medical_task,
            cultural_task, 
            patterns_task,
            return_exceptions=True
        )
        
        # Check for exceptions
        if isinstance(medical_results, Exception):
            raise medical_results
        if isinstance(cultural_results, Exception):
            raise cultural_results
        if isinstance(patterns_data, Exception):
            raise patterns_data
        
        # Prepare data for strategy creation
        medical_facts = "\n".join(medical_results.get('medical_facts', []))
        cultural_context = cultural_results.get('cultural_insights', '')
        approved_structure = patterns_data.get('approved_patterns', [])
        
        # Create content strategy
        strategy = await create_content_strategy(
            topic=topic,
            main_keywords=main_keywords,
            secondary_keywords=secondary_keywords,
            target_word_count=target_word_count,
            negative_keywords=negative_keywords,
            medical_facts=medical_facts,
            cultural_context=cultural_context,
            approved_structure=approved_structure
        )
        
        # Combine all results
        complete_results = {
            "medical_research": medical_results,
            "cultural_context": cultural_results,
            "blog_patterns": patterns_data,
            "content_strategy": strategy,
            "research_summary": {
                "medical_facts_count": len(medical_results.get('medical_facts', [])),
                "cultural_insights_length": len(cultural_context),
                "approved_patterns_count": len(patterns_data.get('approved_patterns', [])),
                "strategy_sections_count": len(strategy.get('content_sections', []))
            }
        }
        
        logger.info("Parallel research phase completed successfully")
        return complete_results
        
    except Exception as e:
        logger.error(f"Error in parallel research phase: {e}")
        raise


@mcp.tool()
async def complete_article_workflow(
    topic: str,
    main_keywords: str,
    secondary_keywords: str,
    target_word_count: int,
    negative_keywords: str = "",
    use_retry_logic: bool = True,
    max_retries: int = 3
) -> dict:
    """
    Complete end-to-end article creation workflow with retry logic.
    
    Args:
        topic: Main medical topic
        main_keywords: Primary keywords for SEO
        secondary_keywords: Secondary keywords
        target_word_count: Target word count
        negative_keywords: Keywords to avoid
        use_retry_logic: Whether to use retry logic for failed generations
        max_retries: Maximum retry attempts
        
    Returns:
        Complete workflow results including all phases
    """
    try:
        logger.info(f"Starting complete article workflow for: {topic}")
        workflow_results = {}
        
        # Phase 1: Parallel Research
        logger.info("Phase 1: Starting parallel research...")
        research_results = await parallel_research_phase(
            topic=topic,
            main_keywords=main_keywords,
            secondary_keywords=secondary_keywords,
            target_word_count=target_word_count,
            negative_keywords=negative_keywords
        )
        workflow_results["phase1_research"] = research_results
        logger.info("Phase 1: Research completed successfully")
        
        # Phase 2: Generation with optional retry logic
        retry_count = 0
        best_result = None
        
        while retry_count <= max_retries:
            try:
                logger.info(f"Phase 2: Generation attempt {retry_count + 1}")
                
                # Generate article
                article = await generate_complete_article(
                    strategy=research_results["content_strategy"],
                    medical_facts="\n".join(research_results["medical_research"].get("medical_facts", [])),
                    cultural_context=research_results["cultural_context"].get("cultural_insights", ""),
                    patterns=research_results["blog_patterns"],
                    retry_count=retry_count,
                    previous_evaluation=best_result.get("evaluation") if best_result else None
                )
                
                # Phase 3: Evaluate
                logger.info("Phase 3: Evaluating article quality...")
                evaluation = await evaluate_with_local_scoring(
                    complete_article=article["article_markdown"],
                    topic=topic,
                    word_count_target=target_word_count,
                    retry_count=retry_count
                )
                
                current_result = {
                    "article": article,
                    "evaluation": evaluation,
                    "attempt": retry_count + 1
                }
                
                # Check if quality passes
                if evaluation["passes_quality_gate"] or not use_retry_logic:
                    best_result = current_result
                    logger.info(f"Quality gate passed on attempt {retry_count + 1}")
                    break
                
                # If this is the last attempt, use the best result
                if retry_count >= max_retries:
                    best_result = current_result
                    logger.warning(f"Max retries reached, using final attempt")
                    break
                
                # Store best result and retry
                if not best_result or evaluation["total_score"] > best_result["evaluation"]["total_score"]:
                    best_result = current_result
                
                retry_count += 1
                logger.info(f"Quality gate failed (score: {evaluation['total_score']}/100), retrying...")
                
            except Exception as e:
                logger.error(f"Generation attempt {retry_count + 1} failed: {e}")
                if retry_count >= max_retries:
                    raise
                retry_count += 1
        
        workflow_results["phase2_generation"] = best_result["article"]
        workflow_results["phase3_evaluation"] = best_result["evaluation"]
        
        # Phase 4: Publishing
        logger.info("Phase 4: Starting publishing...")
        final_evaluation = best_result["evaluation"]
        final_article = best_result["article"]
        
        # Determine publishing status
        status = "PASS" if final_evaluation["passes_quality_gate"] else "FAIL"
        
        # Create Google Doc
        doc_result = await create_google_doc(
            article_markdown=final_article["article_markdown"],
            title=topic,
            status=status
        )
        
        # Publish article
        publish_result = await publish_article(
            doc_id=doc_result["doc_id"],
            article_content=final_article["article_markdown"],
            status=status,
            evaluation=final_evaluation
        )
        
        workflow_results["phase4_publishing"] = {**doc_result, **publish_result}
        logger.info("Phase 4: Publishing completed")
        
        # Compile final results
        final_results = {
            **workflow_results,
            "workflow_summary": {
                "topic": topic,
                "target_word_count": target_word_count,
                "final_word_count": final_article["word_count"],
                "final_quality_score": final_evaluation["total_score"],
                "retry_count": retry_count,
                "final_status": status,
                "published_status": publish_result.get("status", "UNKNOWN"),
                "workflow_completed": True,
                "google_doc_url": doc_result["doc_url"]
            }
        }
        
        logger.info(f"Complete workflow finished successfully for: {topic}")
        return final_results
        
    except Exception as e:
        logger.error(f"Error in complete article workflow: {e}")
        raise


def main():
    """Main entry point for Railway-compatible MCP server."""
    try:
        # Setup server
        asyncio.run(setup_server())
        
        # Detect Railway environment
        is_railway = bool(os.getenv('RAILWAY_PROJECT_ID'))
        port = int(os.getenv('PORT', 3000))
        
        logger.info(f"Environment: {'Railway' if is_railway else 'Local'}")
        
        if is_railway:
            # Railway deployment - run HTTP server with MCP endpoint
            logger.info(f"Starting Railway HTTP server on port {port}")
            run_railway_server(port)
        else:
            # Local development - use MCP stdio
            logger.info("Starting MCP server in stdio mode")
            mcp.run()
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


def run_railway_server(port: int):
    """Run Railway server with proper MCP SSE endpoint."""
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    
    # Create main FastAPI app
    app = FastAPI(
        title="Chloros Blog MCP Server",
        description="MCP server for automated orthopedic blog creation"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with server info."""
        from .health import get_health_status
        health = get_health_status()
        
        return JSONResponse(content={
            "name": "Chloros Blog MCP Server",
            "version": "1.0.0",
            "description": "MCP server for automated Greek orthopedic blog creation",
            "status": "running",
            "health": health,
            "mcp_tools": 11,
            "endpoints": {
                "health": "/health",
                "mcp": "/mcp",
                "tools": "/tools"
            },
            "mcp_connection": {
                "protocol": "Server-Sent Events (SSE)",
                "endpoint": "/mcp",
                "usage": "Connect Claude Desktop to this MCP server"
            }
        })
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        from .health import get_health_status
        return JSONResponse(content=get_health_status())
    
    @app.get("/tools")
    async def list_tools():
        """List available MCP tools."""
        tools = [
            {"name": "medical_research_query", "phase": "1", "description": "Query Pinecone for medical research"},
            {"name": "cultural_context_research", "phase": "1", "description": "Research Greek cultural context"},
            {"name": "read_blog_patterns", "phase": "1", "description": "Read patterns from Google Sheets"},
            {"name": "create_content_strategy", "phase": "1", "description": "Create content strategy"},
            {"name": "parallel_research_phase", "phase": "1", "description": "Execute all research in parallel"},
            {"name": "generate_complete_article", "phase": "2", "description": "Generate complete Greek article"},
            {"name": "evaluate_article_quality", "phase": "3", "description": "AI-powered quality evaluation"},
            {"name": "evaluate_with_local_scoring", "phase": "3", "description": "Local scoring evaluation"},
            {"name": "create_google_doc", "phase": "4", "description": "Create Google Doc from markdown"},
            {"name": "publish_article", "phase": "4", "description": "Publish article to Drive"},
            {"name": "complete_article_workflow", "phase": "1-4", "description": "End-to-end workflow"}
        ]
        
        return JSONResponse(content={
            "total_tools": len(tools),
            "tools": tools,
            "workflow_phases": {
                "1": "Research & Strategy (30s)",
                "2": "Content Generation (120s)", 
                "3": "Quality Evaluation (20s)",
                "4": "Publishing (5s)"
            }
        })
    
    # Mount the MCP HTTP app at /mcp endpoint
    mcp_app = mcp.http_app()
    app.mount("/mcp", mcp_app)
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


async def setup_server():
    """Setup MCP server with health monitoring."""
    from .health import log_startup_info
    
    logger.info("Initializing Chloros Blog MCP Server...")
    log_startup_info()
    
    logger.info("✅ All MCP tools registered:")
    logger.info("   - medical_research_query (Phase 1)")
    logger.info("   - cultural_context_research (Phase 1)")
    logger.info("   - read_blog_patterns (Phase 1)")
    logger.info("   - create_content_strategy (Phase 1)")
    logger.info("   - parallel_research_phase (Phase 1 Combined)")
    logger.info("   - generate_complete_article (Phase 2)")
    logger.info("   - evaluate_article_quality (Phase 3)")
    logger.info("   - evaluate_with_local_scoring (Phase 3)")
    logger.info("   - create_google_doc (Phase 4)")
    logger.info("   - publish_article (Phase 4)")
    logger.info("   - complete_article_workflow (End-to-End)")
    logger.info("🎉 Ready for blog automation with ALL functionality!")


if __name__ == "__main__":
    main()