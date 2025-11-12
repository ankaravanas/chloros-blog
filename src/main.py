"""
Main entry point for the Chloros Blog MCP Server.
Sets up the FastMCP server and registers all tools.
"""

import asyncio
import logging
import os
from typing import Any, Dict

from fastmcp import FastMCP
from dotenv import load_dotenv

from .config import settings
from .health import health_checker
from .tools.research_tools import register_research_tools
from .tools.generation_tools import register_generation_tools
from .tools.evaluation_tools import register_evaluation_tools
from .tools.publishing_tools import register_publishing_tools
from .tools.workflow_tools import register_workflow_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Chloros Blog MCP Server")


async def setup_server():
    """Initialize the MCP server and register all tools."""
    logger.info("Starting Chloros Blog MCP Server...")
    
    # Log health status for Railway monitoring
    health_checker.log_startup_info()
    
    # Register all tool categories
    await register_research_tools(mcp)
    await register_generation_tools(mcp)
    await register_evaluation_tools(mcp)
    await register_publishing_tools(mcp)
    await register_workflow_tools(mcp)
    
    logger.info("All tools registered successfully")
    logger.info("🎉 Chloros Blog MCP Server ready for blog automation!")


def main():
    """Main entry point for the server."""
    try:
        # Setup and run the server
        asyncio.run(setup_server())
        
        # Railway provides PORT environment variable, fallback to settings.port
        port = int(os.getenv('PORT', settings.port))
        
        # Detect Railway environment
        is_railway = bool(os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'))
        environment = 'Railway' if is_railway else 'Local'
        
        # Start the MCP server
        logger.info(f"Server starting on port {port}")
        logger.info(f"Environment: {environment}")
        
        if is_railway:
            logger.info(f"Railway Project ID: {os.getenv('RAILWAY_PROJECT_ID', 'Unknown')}")
            logger.info(f"Railway Service ID: {os.getenv('RAILWAY_SERVICE_ID', 'Unknown')}")
        
        # FastMCP server startup
        logger.info("Starting MCP server...")
        
        # MCP servers run via stdio protocol
        # Railway will keep the container alive as long as the process runs
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
