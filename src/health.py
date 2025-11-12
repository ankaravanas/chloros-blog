"""
Simple health check for Railway deployment.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_health_status() -> dict:
    """Get basic health status."""
    
    required_vars = [
        'OPENAI_API_KEY', 'OPENROUTER_API_KEY', 'PERPLEXITY_API_KEY',
        'PINECONE_API_KEY', 'GOOGLE_CLIENT_ID', 'GOOGLE_REFRESH_TOKEN'
    ]
    
    configured_apis = sum(1 for var in required_vars if os.getenv(var))
    
    return {
        "status": "healthy" if configured_apis >= 5 else "degraded",
        "apis_configured": f"{configured_apis}/{len(required_vars)}",
        "environment": "Railway" if os.getenv('RAILWAY_PROJECT_ID') else "Local",
        "timestamp": datetime.now().isoformat()
    }


def log_startup_info():
    """Log startup information."""
    health = get_health_status()
    
    logger.info("🚀 Chloros Blog MCP Server")
    logger.info(f"Status: {health['status'].upper()}")
    logger.info(f"Environment: {health['environment']}")
    logger.info(f"APIs configured: {health['apis_configured']}")
    
    if health['environment'] == 'Railway':
        project_id = os.getenv('RAILWAY_PROJECT_ID', 'Unknown')
        logger.info(f"Railway Project: {project_id}")


# Create global instance for backward compatibility
class HealthChecker:
    def get_health_status(self):
        return get_health_status()
    
    def log_startup_info(self):
        return log_startup_info()

health_checker = HealthChecker()