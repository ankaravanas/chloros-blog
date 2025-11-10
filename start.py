#!/usr/bin/env python3
"""
Railway-optimized startup script for Chloros Blog MCP Server.
Handles Railway-specific environment and logging configuration.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to Python path for Railway
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_railway_logging():
    """Configure logging optimized for Railway."""
    
    # Railway-friendly logging configuration
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout  # Railway captures stdout
    )
    
    # Suppress some verbose logs for Railway
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('google.auth').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def main():
    """Railway-optimized main entry point."""
    
    # Setup Railway logging
    setup_railway_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Chloros Blog MCP Server on Railway")
    
    # Log Railway environment info
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info(f"Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT')}")
        logger.info(f"Railway Project: {os.getenv('RAILWAY_PROJECT_ID', 'Unknown')}")
        logger.info(f"Railway Service: {os.getenv('RAILWAY_SERVICE_ID', 'Unknown')}")
    
    # Import and run the main server
    try:
        from src.main import main as server_main
        server_main()
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
