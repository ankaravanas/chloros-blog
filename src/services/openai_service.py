"""
OpenAI service for embeddings and content strategy generation.
Handles text embeddings and strategic planning for content creation.
"""

import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings
from ..models.content import ContentStrategy, Section, SEOStrategy, ContentRestrictions

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.embedding_model = settings.openai_embedding_model
        self.embedding_dimensions = settings.embedding_dimensions
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def create_embeddings(self, text: str) -> List[float]:
        """
        Create embeddings for text using OpenAI's embedding model.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
                dimensions=self.embedding_dimensions
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Created embedding for text of length {len(text)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def create_content_strategy(
        self,
        topic: str,
        main_keywords: str,
        secondary_keywords: str,
        target_word_count: int,
        negative_keywords: str,
        medical_facts: str,
        cultural_context: str,
        approved_structure: List[Dict[str, Any]]
    ) -> ContentStrategy:
        """
        Generate a comprehensive content strategy using OpenAI.
        
        Args:
            topic: Main topic of the article
            main_keywords: Primary keywords for SEO
            secondary_keywords: Secondary keywords
            target_word_count: Target word count for the article
            negative_keywords: Keywords to avoid
            medical_facts: Medical facts from Pinecone research
            cultural_context: Cultural context from Perplexity research
            approved_structure: Approved structure patterns from Google Sheets
            
        Returns:
            Complete content strategy
        """
        try:
            system_prompt = self._get_strategy_system_prompt()
            user_prompt = self._build_strategy_user_prompt(
                topic, main_keywords, secondary_keywords, target_word_count,
                negative_keywords, medical_facts, cultural_context, approved_structure
            )
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            strategy_data = eval(result)  # Parse JSON response
            
            # Convert to Pydantic model
            strategy = self._parse_strategy_response(strategy_data)
            
            logger.info(f"Created content strategy for topic: {topic}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error creating content strategy: {e}")
            raise
    
    def _get_strategy_system_prompt(self) -> str:
        """Get the system prompt for content strategy generation."""
        return """
        You are an expert content strategist for medical blog articles, specializing in 
        Greek orthopedic surgery content. Your task is to create comprehensive content 
        strategies that will guide article generation.
        
        Key requirements:
        1. Generate H1 titles that include the main keyword naturally
        2. Create section outlines that follow proven medical content patterns
        3. Plan SEO keyword placement strategically throughout the content
        4. Consider Greek cultural context and patient concerns
        5. Ensure medical accuracy and professional tone
        6. Plan for Γ' ενικό (third person) voice throughout
        
        Always respond with valid JSON containing all required fields.
        Focus on educational value and building trust through expertise demonstration.
        """
    
    def _build_strategy_user_prompt(
        self,
        topic: str,
        main_keywords: str,
        secondary_keywords: str,
        target_word_count: int,
        negative_keywords: str,
        medical_facts: str,
        cultural_context: str,
        approved_structure: List[Dict[str, Any]]
    ) -> str:
        """Build the user prompt for strategy generation."""
        return f"""
        Create a comprehensive content strategy for a Greek orthopedic blog article.
        
        TOPIC: {topic}
        MAIN KEYWORDS: {main_keywords}
        SECONDARY KEYWORDS: {secondary_keywords}
        TARGET WORD COUNT: {target_word_count}
        AVOID KEYWORDS: {negative_keywords}
        
        MEDICAL RESEARCH CONTEXT:
        {medical_facts[:1500]}  # Truncate to fit in context
        
        CULTURAL CONTEXT:
        {cultural_context[:800]}
        
        APPROVED STRUCTURES:
        {str(approved_structure)[:500]}
        
        Generate a JSON response with the following structure:
        {{
            "h1_title": "Title with main keyword in Greek",
            "content_sections": [
                {{
                    "title": "Section title",
                    "content_points": ["Point 1", "Point 2"],
                    "target_words": 300,
                    "medical_focus": ["concept1", "concept2"]
                }}
            ],
            "seo_strategy": {{
                "main_keyword_placement": ["H1", "first paragraph", "conclusion"],
                "secondary_distribution": ["section 2", "section 4"]
            }},
            "content_restrictions": {{
                "avoid": ["emotional stories", "first person voice"],
                "alternatives": ["evidence-based examples", "third person voice"],
                "voice_requirements": ["Γ' ενικό throughout", "professional tone"]
            }},
            "medical_focus": ["key medical concept 1", "key medical concept 2"],
            "target_word_count": {target_word_count},
            "cultural_context": "Brief summary of cultural considerations"
        }}
        
        Ensure:
        1. H1 title includes main keyword naturally in Greek
        2. 5-7 logical sections following medical content flow
        3. Each section has 3-5 content points and realistic word targets
        4. SEO strategy places keywords naturally, not forced
        5. Content restrictions prevent common medical blog pitfalls
        6. Medical focus aligns with the research provided
        """
    
    def _parse_strategy_response(self, strategy_data: Dict[str, Any]) -> ContentStrategy:
        """Parse the strategy response into a Pydantic model."""
        try:
            # Parse sections
            sections = []
            for section_data in strategy_data.get("content_sections", []):
                section = Section(
                    title=section_data["title"],
                    content_points=section_data["content_points"],
                    target_words=section_data.get("target_words"),
                    medical_focus=section_data.get("medical_focus")
                )
                sections.append(section)
            
            # Parse SEO strategy
            seo_strategy = SEOStrategy(
                main_keyword_placement=strategy_data["seo_strategy"]["main_keyword_placement"],
                secondary_distribution=strategy_data["seo_strategy"]["secondary_distribution"]
            )
            
            # Parse content restrictions
            restrictions = ContentRestrictions(
                avoid=strategy_data["content_restrictions"]["avoid"],
                alternatives=strategy_data["content_restrictions"]["alternatives"],
                voice_requirements=strategy_data["content_restrictions"]["voice_requirements"]
            )
            
            # Create complete strategy
            strategy = ContentStrategy(
                h1_title=strategy_data["h1_title"],
                content_sections=sections,
                seo_strategy=seo_strategy,
                content_restrictions=restrictions,
                medical_focus=strategy_data["medical_focus"],
                target_word_count=strategy_data["target_word_count"],
                cultural_context=strategy_data.get("cultural_context")
            )
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error parsing strategy response: {e}")
            raise
    
    async def create_query_embedding(self, topic: str, keywords: str) -> List[float]:
        """
        Create an embedding for a research query combining topic and keywords.
        
        Args:
            topic: Main topic
            keywords: Relevant keywords
            
        Returns:
            Query embedding vector
        """
        query_text = f"{topic} {keywords}"
        return await self.create_embeddings(query_text)
