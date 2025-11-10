"""
Pinecone service for medical research and RAG validation.
Handles vector search against medical knowledge base.
"""

import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings

logger = logging.getLogger(__name__)


class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    def __init__(self):
        """Initialize Pinecone client and index."""
        self.client = Pinecone(api_key=settings.pinecone_api_key)
        self.index = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize the Pinecone index."""
        try:
            self.index = self.client.Index(settings.pinecone_index_name)
            logger.info(f"Connected to Pinecone index: {settings.pinecone_index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def search_medical_knowledge(
        self,
        query_embedding: List[float],
        top_k: int = 25,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for medical knowledge using vector similarity.
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of matching documents with metadata
        """
        try:
            if not self.index:
                raise ValueError("Pinecone index not initialized")
            
            # Perform vector search
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_metadata,
                include_metadata=True,
                include_values=False
            )
            
            # Extract and format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    'id': match.id,
                    'score': float(match.score),
                    'content': match.metadata.get('content', ''),
                    'source': match.metadata.get('source', 'Unknown'),
                    'type': match.metadata.get('type', 'medical'),
                    'metadata': match.metadata
                })
            
            logger.info(f"Retrieved {len(formatted_results)} medical knowledge results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching medical knowledge: {e}")
            raise
    
    async def search_by_topic(
        self,
        topic: str,
        query_embedding: List[float],
        main_keywords: str,
        secondary_keywords: str
    ) -> Dict[str, Any]:
        """
        Search for medical facts related to a specific topic.
        
        Args:
            topic: Main topic/condition
            query_embedding: Embedded query vector
            main_keywords: Primary keywords
            secondary_keywords: Secondary keywords
            
        Returns:
            Dictionary with medical facts and citations
        """
        try:
            # Create metadata filters for medical content
            filter_metadata = {
                "type": {"$in": ["treatment", "procedure", "guideline", "study"]},
                "$or": [
                    {"keywords": {"$in": main_keywords.split(", ")}},
                    {"topic": {"$eq": topic.lower()}}
                ]
            }
            
            # Search for relevant medical content
            results = await self.search_medical_knowledge(
                query_embedding=query_embedding,
                top_k=25,
                filter_metadata=filter_metadata
            )
            
            # Extract medical facts and citations
            medical_facts = []
            citations = []
            
            for result in results:
                if result['score'] > 0.7:  # High relevance threshold
                    medical_facts.append(result['content'])
                    citations.append({
                        'source': result['source'],
                        'content': result['content'][:200] + "...",
                        'relevance_score': result['score']
                    })
            
            return {
                'medical_facts': medical_facts,
                'citations': citations,
                'total_results': len(results),
                'high_relevance_count': len(medical_facts)
            }
            
        except Exception as e:
            logger.error(f"Error searching by topic '{topic}': {e}")
            raise
    
    async def validate_medical_accuracy(
        self,
        content: str,
        content_embedding: List[float],
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Validate medical accuracy of content against knowledge base.
        
        Args:
            content: Content to validate
            content_embedding: Embedding of the content
            threshold: Similarity threshold for validation
            
        Returns:
            Validation results with accuracy score
        """
        try:
            # Search for similar medical content
            results = await self.search_medical_knowledge(
                query_embedding=content_embedding,
                top_k=10,
                filter_metadata={"type": {"$in": ["guideline", "study", "fact"]}}
            )
            
            # Calculate accuracy metrics
            high_similarity_matches = [r for r in results if r['score'] > threshold]
            accuracy_score = min(100, len(high_similarity_matches) * 10)  # Max 100
            
            # Check for contradictions
            contradictions = []
            for result in results:
                if result['score'] > 0.6 and self._check_contradiction(content, result['content']):
                    contradictions.append(result)
            
            return {
                'accuracy_score': accuracy_score,
                'supporting_evidence': high_similarity_matches,
                'contradictions': contradictions,
                'validation_passed': accuracy_score >= 70 and len(contradictions) == 0,
                'recommendations': self._generate_accuracy_recommendations(results)
            }
            
        except Exception as e:
            logger.error(f"Error validating medical accuracy: {e}")
            raise
    
    def _check_contradiction(self, content: str, reference: str) -> bool:
        """Check if content contradicts reference material."""
        # Simple contradiction detection (can be enhanced with NLP)
        contradiction_indicators = [
            ("increase", "decrease"), ("high", "low"), ("effective", "ineffective"),
            ("safe", "dangerous"), ("recommended", "not recommended")
        ]
        
        content_lower = content.lower()
        reference_lower = reference.lower()
        
        for positive, negative in contradiction_indicators:
            if positive in content_lower and negative in reference_lower:
                return True
            if negative in content_lower and positive in reference_lower:
                return True
        
        return False
    
    def _generate_accuracy_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on search results."""
        recommendations = []
        
        if len(results) < 5:
            recommendations.append("Consider adding more medical evidence and citations")
        
        high_score_results = [r for r in results if r['score'] > 0.8]
        if len(high_score_results) < 3:
            recommendations.append("Ensure content aligns closely with established medical guidelines")
        
        procedure_results = [r for r in results if r.get('type') == 'procedure']
        if len(procedure_results) > 0:
            recommendations.append("Include specific procedure details and success rates")
        
        return recommendations
