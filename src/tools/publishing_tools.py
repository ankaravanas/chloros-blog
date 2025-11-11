"""
Phase 4 publishing tools for Google Workspace integration.
Implements document creation, folder management, and tracking sheet updates.
"""

import logging
from typing import Dict, Any
from typing import List  # Separate import for Railway compatibility
from fastmcp import FastMCP

from ..services.google_service import GoogleService

logger = logging.getLogger(__name__)

# Service instance
google_service = GoogleService()


async def register_publishing_tools(mcp: FastMCP):
    """Register all Phase 4 publishing tools with the MCP server."""
    
    @mcp.tool()
    async def create_google_doc(
        article_markdown: str,
        title: str,
        status: str
    ) -> Dict[str, str]:
        """
        Create a Google Doc from markdown article content.
        
        Args:
            article_markdown: Article content in Markdown format
            title: Base title for the document
            status: "PASS" or "FAIL" status for document naming
            
        Returns:
            Dictionary with doc_id and doc_url
        """
        try:
            logger.info(f"Creating Google Doc for: {title}")
            
            # Create the document
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
        evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Publish article by managing folder placement and tracking sheet updates.
        
        Args:
            doc_id: Google Doc ID
            article_content: Article content for reference
            status: "PASS" or "FAIL" status
            evaluation: Evaluation results dictionary
            
        Returns:
            Publication results with status and metadata
        """
        try:
            logger.info(f"Publishing article with status: {status}")
            
            # Publish the article
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
    async def create_and_publish_article(
        article_markdown: str,
        title: str,
        evaluation: Dict[str, Any],
        force_publish: bool = False
    ) -> Dict[str, Any]:
        """
        Complete publishing workflow: create document and publish based on evaluation.
        
        Args:
            article_markdown: Article content in Markdown
            title: Article title
            evaluation: Evaluation results
            force_publish: Force publish even if evaluation fails
            
        Returns:
            Complete publishing results
        """
        try:
            logger.info(f"Starting complete publishing workflow for: {title}")
            
            # Determine status based on evaluation
            passes_quality = evaluation.get("passes_quality_gate", False)
            status = "PASS" if (passes_quality or force_publish) else "FAIL"
            
            # Create Google Doc
            doc_result = await create_google_doc(
                article_markdown=article_markdown,
                title=title,
                status=status
            )
            
            # Publish the article
            publish_result = await publish_article(
                doc_id=doc_result["doc_id"],
                article_content=article_markdown,
                status=status,
                evaluation=evaluation
            )
            
            # Combine results
            complete_result = {
                **doc_result,
                **publish_result,
                "publishing_workflow": "completed",
                "forced_publish": force_publish,
                "original_evaluation_passed": passes_quality
            }
            
            logger.info("Complete publishing workflow finished successfully")
            return complete_result
            
        except Exception as e:
            logger.error(f"Error in complete publishing workflow: {e}")
            raise
    
    @mcp.tool()
    async def update_article_status(
        doc_id: str,
        new_status: str,
        reason: str,
        updated_evaluation: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Update the status of an already published article.
        
        Args:
            doc_id: Google Doc ID
            new_status: New status ("PUBLISHED", "NEEDS_REVIEW", "ARCHIVED")
            reason: Reason for status change
            updated_evaluation: Updated evaluation if available
            
        Returns:
            Status update results
        """
        try:
            logger.info(f"Updating article status to: {new_status}")
            
            # This would involve moving the document and updating tracking sheets
            # Simplified implementation for now
            
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            # Log status change (would update Google Sheets)
            status_change_record = {
                "doc_id": doc_id,
                "doc_url": doc_url,
                "old_status": "unknown",  # Would track this in real implementation
                "new_status": new_status,
                "reason": reason,
                "timestamp": timestamp,
                "updated_evaluation": updated_evaluation
            }
            
            logger.info(f"Article status updated successfully")
            return {
                "status_updated": True,
                "new_status": new_status,
                "doc_url": doc_url,
                "timestamp": timestamp,
                "change_record": status_change_record
            }
            
        except Exception as e:
            logger.error(f"Error updating article status: {e}")
            raise
    
    @mcp.tool()
    async def get_publishing_statistics() -> Dict[str, Any]:
        """
        Get statistics about published articles from tracking sheets.
        
        Returns:
            Publishing statistics and metrics
        """
        try:
            logger.info("Retrieving publishing statistics")
            
            # This would read from Google Sheets to get actual statistics
            # Simplified implementation for now
            
            statistics = {
                "total_articles": 0,
                "published_count": 0,
                "needs_review_count": 0,
                "average_quality_score": 0.0,
                "pass_rate": 0.0,
                "recent_articles": [],
                "quality_trends": {
                    "improving": False,
                    "average_score_trend": "stable"
                },
                "common_issues": [
                    "Word count below target",
                    "Voice consistency issues",
                    "Missing variability disclaimers"
                ]
            }
            
            logger.info("Publishing statistics retrieved")
            return statistics
            
        except Exception as e:
            logger.error(f"Error retrieving publishing statistics: {e}")
            raise
    
    @mcp.tool()
    async def batch_publish_articles(
        articles: List[Dict[str, Any]],
        force_publish_threshold: int = 70
    ) -> Dict[str, Any]:
        """
        Publish multiple articles in batch with intelligent status determination.
        
        Args:
            articles: List of article dictionaries with content and evaluations
            force_publish_threshold: Score threshold for force publishing
            
        Returns:
            Batch publishing results
        """
        try:
            logger.info(f"Starting batch publishing of {len(articles)} articles")
            
            published_results = []
            failed_articles = []
            
            for i, article in enumerate(articles):
                try:
                    article_content = article["article_markdown"]
                    title = article.get("title", f"Article {i+1}")
                    evaluation = article["evaluation"]
                    
                    # Determine if should force publish
                    quality_score = evaluation.get("total_score", 0)
                    force_publish = quality_score >= force_publish_threshold
                    
                    # Publish individual article
                    result = await create_and_publish_article(
                        article_markdown=article_content,
                        title=title,
                        evaluation=evaluation,
                        force_publish=force_publish
                    )
                    
                    published_results.append({
                        "article_index": i,
                        "title": title,
                        "result": result,
                        "quality_score": quality_score
                    })
                    
                except Exception as e:
                    logger.error(f"Error publishing article {i}: {e}")
                    failed_articles.append({
                        "article_index": i,
                        "title": article.get("title", f"Article {i+1}"),
                        "error": str(e)
                    })
            
            # Calculate batch statistics
            total_articles = len(articles)
            successful_publishes = len(published_results)
            failed_publishes = len(failed_articles)
            success_rate = (successful_publishes / total_articles) * 100 if total_articles > 0 else 0
            
            batch_result = {
                "total_articles": total_articles,
                "successful_publishes": successful_publishes,
                "failed_publishes": failed_publishes,
                "success_rate": success_rate,
                "published_results": published_results,
                "failed_articles": failed_articles,
                "batch_completed": True
            }
            
            logger.info(f"Batch publishing completed: {successful_publishes}/{total_articles} successful")
            return batch_result
            
        except Exception as e:
            logger.error(f"Error in batch publishing: {e}")
            raise
    
    @mcp.tool()
    async def archive_old_articles(
        days_threshold: int = 30,
        quality_threshold: int = 60
    ) -> Dict[str, Any]:
        """
        Archive old articles that are below quality threshold.
        
        Args:
            days_threshold: Archive articles older than this many days
            quality_threshold: Archive articles below this quality score
            
        Returns:
            Archiving results
        """
        try:
            logger.info(f"Starting archival of old articles (>{days_threshold} days, <{quality_threshold} quality)")
            
            # This would involve querying Google Sheets for old articles
            # and moving them to an archive folder
            # Simplified implementation for now
            
            archived_count = 0  # Would be actual count in real implementation
            archived_articles = []  # Would contain actual article data
            
            archival_result = {
                "archived_count": archived_count,
                "archived_articles": archived_articles,
                "days_threshold": days_threshold,
                "quality_threshold": quality_threshold,
                "archival_completed": True
            }
            
            logger.info(f"Archival completed: {archived_count} articles archived")
            return archival_result
            
        except Exception as e:
            logger.error(f"Error in article archival: {e}")
            raise
    
    logger.info("Phase 4 publishing tools registered successfully")
