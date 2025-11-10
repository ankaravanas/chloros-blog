"""
Health check utilities for Railway deployment monitoring.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HealthChecker:
    """Health check utilities for monitoring server status."""
    
    def __init__(self):
        """Initialize health checker."""
        self.start_time = datetime.now()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status for monitoring."""
        
        uptime = datetime.now() - self.start_time
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "environment": {
                "platform": "Railway" if os.getenv('RAILWAY_ENVIRONMENT') else "Local",
                "python_version": os.sys.version.split()[0],
                "port": os.getenv('PORT', '3000'),
                "host": os.getenv('HOST', '0.0.0.0')
            },
            "services": {
                "openai": self._check_env_var('OPENAI_API_KEY'),
                "openrouter": self._check_env_var('OPENROUTER_API_KEY'),
                "perplexity": self._check_env_var('PERPLEXITY_API_KEY'),
                "pinecone": self._check_env_var('PINECONE_API_KEY'),
                "google_oauth": self._check_google_oauth()
            },
            "configuration": {
                "quality_threshold": os.getenv('QUALITY_PASS_THRESHOLD', '80'),
                "max_retries": os.getenv('MAX_RETRIES', '3'),
                "openrouter_model": os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3-haiku'),
                "log_level": os.getenv('LOG_LEVEL', 'INFO')
            }
        }
        
        # Check if any critical services are missing
        critical_services = ['openai', 'pinecone', 'google_oauth']
        missing_services = [
            service for service in critical_services 
            if not health_status['services'][service]
        ]
        
        if missing_services:
            health_status['status'] = 'degraded'
            health_status['missing_services'] = missing_services
            health_status['warnings'] = [
                f"Missing configuration for: {', '.join(missing_services)}"
            ]
        
        return health_status
    
    def _check_env_var(self, var_name: str) -> bool:
        """Check if environment variable is configured."""
        value = os.getenv(var_name)
        return bool(value and value != f'your_{var_name.lower()}_here')
    
    def _check_google_oauth(self) -> bool:
        """Check if Google OAuth is properly configured."""
        required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REFRESH_TOKEN']
        return all(self._check_env_var(var) for var in required_vars)
    
    def log_startup_info(self):
        """Log comprehensive startup information."""
        health = self.get_health_status()
        
        logger.info("🚀 Chloros Blog MCP Server Health Check")
        logger.info(f"Status: {health['status'].upper()}")
        logger.info(f"Platform: {health['environment']['platform']}")
        logger.info(f"Host: {health['environment']['host']}:{health['environment']['port']}")
        
        # Log service status
        for service, status in health['services'].items():
            status_icon = "✅" if status else "❌"
            logger.info(f"Service {service}: {status_icon}")
        
        # Log warnings if any
        if 'warnings' in health:
            for warning in health['warnings']:
                logger.warning(f"⚠️ {warning}")
        
        # Railway-specific logging
        if health['environment']['platform'] == 'Railway':
            railway_project = os.getenv('RAILWAY_PROJECT_ID', 'Unknown')
            railway_service = os.getenv('RAILWAY_SERVICE_ID', 'Unknown')
            logger.info(f"Railway Project: {railway_project}")
            logger.info(f"Railway Service: {railway_service}")


# Global health checker instance
health_checker = HealthChecker()
