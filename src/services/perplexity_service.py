"""
Perplexity service for cultural context research.
Handles queries about Greek healthcare culture and patient perceptions.
"""

import logging
import httpx
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings

logger = logging.getLogger(__name__)


class PerplexityService:
    """Service for interacting with Perplexity API for cultural context research."""
    
    def __init__(self):
        """Initialize Perplexity service."""
        self.base_url = "https://api.perplexity.ai"
        self.model = "sonar-pro"
        self.headers = {
            "Authorization": f"Bearer {settings.perplexity_api_key}",
            "Content-Type": "application/json"
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def research_cultural_context(self, topic: str) -> Dict[str, Any]:
        """
        Research Greek cultural context for a medical topic.
        
        Args:
            topic: Medical topic to research cultural context for
            
        Returns:
            Dictionary with cultural insights and patient concerns
        """
        try:
            # Construct culturally-focused query
            query = self._build_cultural_query(topic)
            
            async with httpx.AsyncClient(timeout=900.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": self._get_cultural_system_prompt()
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 2000
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse the response into structured data
                parsed_result = self._parse_cultural_response(content)
                
                logger.info(f"Retrieved cultural context for topic: {topic}")
                return parsed_result
                
        except httpx.TimeoutException:
            logger.error(f"Timeout while researching cultural context for: {topic}")
            raise
        except Exception as e:
            logger.error(f"Error researching cultural context: {e}")
            raise
    
    def _build_cultural_query(self, topic: str) -> str:
        """Build a culturally-focused query for the topic."""
        return f"""
        Research the cultural context of {topic} in Greece, focusing on:
        
        1. Greek patient attitudes and perceptions about {topic}
        2. Cultural beliefs that might affect treatment acceptance
        3. Common concerns or fears Greek patients have about {topic}
        4. How the Greek healthcare system typically handles {topic}
        5. Family dynamics and decision-making patterns in Greek culture regarding {topic}
        6. Traditional or alternative approaches Greeks might consider
        7. Communication preferences (direct vs indirect) about {topic}
        8. Economic considerations and insurance coverage in Greece
        
        Provide specific, actionable insights that would help a Greek orthopedic surgeon 
        communicate more effectively with patients about {topic}.
        """
    
    def _get_cultural_system_prompt(self) -> str:
        """Get the system prompt for cultural context research."""
        return """
        You are a cultural research specialist focused on Greek healthcare culture.
        Your task is to provide specific, actionable cultural insights about medical topics
        in the Greek context. 
        
        Focus on:
        - Patient attitudes and behaviors
        - Cultural beliefs affecting healthcare decisions
        - Communication preferences
        - Family involvement in medical decisions
        - Economic and social factors
        - Traditional vs modern medical approaches
        
        Provide concrete, specific insights that would help healthcare providers
        communicate more effectively with Greek patients.
        
        Do NOT provide medical advice or clinical information - focus only on
        cultural, social, and communication aspects.
        """
    
    def _parse_cultural_response(self, content: str) -> Dict[str, Any]:
        """Parse the cultural research response into structured data."""
        try:
            # Extract key sections using simple text parsing
            lines = content.split('\n')
            
            cultural_insights = []
            patient_concerns = []
            healthcare_context = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                if any(keyword in line.lower() for keyword in ['attitude', 'perception', 'belief']):
                    current_section = 'insights'
                elif any(keyword in line.lower() for keyword in ['concern', 'fear', 'worry']):
                    current_section = 'concerns'
                elif any(keyword in line.lower() for keyword in ['healthcare', 'system', 'insurance']):
                    current_section = 'context'
                
                # Extract content based on current section
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    content_text = line[1:].strip()
                    if current_section == 'insights':
                        cultural_insights.append(content_text)
                    elif current_section == 'concerns':
                        patient_concerns.append(content_text)
                    elif current_section == 'context':
                        healthcare_context.append(content_text)
                elif current_section and len(line) > 20:  # Substantial content
                    if current_section == 'insights':
                        cultural_insights.append(line)
                    elif current_section == 'concerns':
                        patient_concerns.append(line)
                    elif current_section == 'context':
                        healthcare_context.append(line)
            
            # Fallback: if parsing failed, use the full content
            if not cultural_insights and not patient_concerns:
                cultural_insights = [content]
            
            return {
                'cultural_insights': '\n'.join(cultural_insights) if cultural_insights else content,
                'patient_concerns': patient_concerns or ["General healthcare concerns in Greek culture"],
                'healthcare_context': '\n'.join(healthcare_context) if healthcare_context else "Greek healthcare system context"
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse cultural response, using raw content: {e}")
            return {
                'cultural_insights': content,
                'patient_concerns': ["Cultural considerations for Greek patients"],
                'healthcare_context': "Greek healthcare cultural context"
            }
    
    async def research_patient_communication(self, topic: str, target_audience: str = "middle-aged adults") -> Dict[str, Any]:
        """
        Research effective communication strategies for Greek patients.
        
        Args:
            topic: Medical topic
            target_audience: Target patient demographic
            
        Returns:
            Communication strategies and preferences
        """
        try:
            query = f"""
            How should a Greek orthopedic surgeon communicate about {topic} with {target_audience}?
            
            Focus on:
            1. Preferred communication style (direct vs indirect)
            2. Level of medical detail patients expect
            3. Role of family in discussions
            4. Addressing common misconceptions
            5. Building trust and credibility
            6. Cultural sensitivities to avoid
            7. Effective persuasion techniques in Greek culture
            """
            
            async with httpx.AsyncClient(timeout=900.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert in Greek healthcare communication and patient relations."
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1500
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                return {
                    'communication_strategies': content,
                    'target_audience': target_audience,
                    'topic': topic
                }
                
        except Exception as e:
            logger.error(f"Error researching patient communication: {e}")
            raise
