"""
Main entry point for the Chloros Blog MCP Server.
Sets up the FastMCP server and registers all tools.
"""

import asyncio
import logging
from typing import Any, Dict

from fastmcp import FastMCP
from dotenv import load_dotenv

from .config import settings
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
    
    # Register all tool categories
    await register_research_tools(mcp)
    await register_generation_tools(mcp)
    await register_evaluation_tools(mcp)
    await register_publishing_tools(mcp)
    await register_workflow_tools(mcp)
    
    logger.info("All tools registered successfully")


def main():
    """Main entry point for the server."""
    try:
        # Setup and run the server
        asyncio.run(setup_server())
        
        # Start the MCP server
        logger.info(f"Server starting on port {settings.port}")
        mcp.run(port=settings.port)
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
