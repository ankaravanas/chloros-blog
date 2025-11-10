"""
Phase 1 research tools for parallel data gathering.
Implements medical research, cultural context, pattern reading, and strategy creation.
"""

import logging
import asyncio
from typing import Dict, Any, List
from fastmcp import FastMCP

from ..services.pinecone_service import PineconeService
from ..services.perplexity_service import PerplexityService
from ..services.openai_service import OpenAIService
from ..services.google_service import GoogleService
from ..models.content import ContentStrategy

logger = logging.getLogger(__name__)

# Service instances
pinecone_service = PineconeService()
perplexity_service = PerplexityService()
openai_service = OpenAIService()
google_service = GoogleService()


async def register_research_tools(mcp: FastMCP):
    """Register all Phase 1 research tools with the MCP server."""
    
    @mcp.tool()
    async def medical_research_query(
        topic: str,
        main_keywords: str,
        secondary_keywords: str
    ) -> Dict[str, Any]:
        """
        Query Pinecone vector database for medical research.
        
        Args:
            topic: Main medical topic to research
            main_keywords: Primary keywords for the search
            secondary_keywords: Additional relevant keywords
            
        Returns:
            Dictionary with medical facts and citations
        """
        try:
            logger.info(f"Starting medical research for topic: {topic}")
            
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
    async def cultural_context_research(topic: str) -> Dict[str, Any]:
        """
        Research Greek cultural context using Perplexity API.
        
        Args:
            topic: Medical topic to research cultural context for
            
        Returns:
            Dictionary with cultural insights and patient concerns
        """
        try:
            logger.info(f"Starting cultural context research for: {topic}")
            
            # Research cultural context
            result = await perplexity_service.research_cultural_context(topic)
            
            logger.info("Cultural context research completed")
            return result
            
        except Exception as e:
            logger.error(f"Error in cultural context research: {e}")
            raise
    
    @mcp.tool()
    async def read_blog_patterns() -> Dict[str, Any]:
        """
        Read blog patterns from Google Sheets.
        
        Returns:
            Dictionary containing all pattern data from Google Sheets
        """
        try:
            logger.info("Reading blog patterns from Google Sheets")
            
            # Read all pattern data
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
        approved_structure: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create comprehensive content strategy using OpenAI.
        
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
            logger.info(f"Creating content strategy for: {topic}")
            
            # Create content strategy
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
    async def parallel_research_phase(
        topic: str,
        main_keywords: str,
        secondary_keywords: str,
        target_word_count: int,
        negative_keywords: str = ""
    ) -> Dict[str, Any]:
        """
        Execute all Phase 1 research tasks in parallel for maximum efficiency.
        
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
            approved_structure = [
                {
                    "name": struct.name,
                    "sections": struct.required_sections,
                    "order": struct.section_order
                }
                for struct in patterns_data.get('approved_structure', [])
            ]
            
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
    
    logger.info("Phase 1 research tools registered successfully")
