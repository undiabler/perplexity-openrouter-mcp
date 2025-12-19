"""
FastMCP tool definitions for Perplexity MCP Server.

These are thin wrappers around PerplexitySearch methods.
All business logic lives in PerplexitySearch.
"""

import os
from contextlib import asynccontextmanager

import mcp.types as mcp_types
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext

from src.perplexity_search import PerplexitySearch

# Global reference for tools to access
_search: PerplexitySearch | None = None

def get_search() -> PerplexitySearch:
    """Get the PerplexitySearch instance."""
    if _search is None:
        raise RuntimeError("PerplexitySearch not initialized")
    return _search

@asynccontextmanager
async def lifespan(app):
    """
    Lifespan context manager for FastMCP.

    Handles async startup and shutdown of PerplexitySearch.
    """
    global _search
    _search = PerplexitySearch()

    try:
        yield
    finally:
        await _search.close()
        _search = None
        print("Server stopped.")

class ArgumentSanitizerMiddleware(Middleware):
    """
    Strip extra/unknown fields from tool arguments before Pydantic validation.

    Some MCP clients (e.g., n8n) include metadata fields like 'tool', 'id', 'toolCallId'
    inside the arguments dict. FastMCP's strict Pydantic validation rejects these
    unexpected fields. This middleware filters arguments to only include parameters
    defined in the tool's JSON schema.
    """

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        message = context.message
        arguments = message.arguments or {}

        # Get the tool to access its parameter schema
        tools = await mcp._tool_manager.get_tools()
        tool = tools.get(message.name)

        if tool and arguments:
            # Get valid parameter names from the tool's JSON schema
            valid_params = set(tool.parameters.get("properties", {}).keys())
            # Filter to only include valid parameters, silently dropping extras
            cleaned_args = {k: v for k, v in arguments.items() if k in valid_params}

            # Create new message with cleaned arguments
            new_message = mcp_types.CallToolRequestParams(name=message.name, arguments=cleaned_args)
            context = context.copy(message=new_message)

        return await call_next(context)

class BearerAuthMiddleware(Middleware):
    """Validate Bearer token from Authorization header."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        headers = get_http_headers()
        auth_header = headers.get("authorization", "")

        expected_token = os.getenv("MCP_BEARER_TOKEN")
        if not expected_token:
            raise ToolError("Server misconfigured: MCP_BEARER_TOKEN not set")

        if not auth_header.startswith("Bearer "):
            raise ToolError("Unauthorized: Missing Bearer token")

        token = auth_header[7:]  # Remove "Bearer " prefix
        if token != expected_token:
            raise ToolError("Unauthorized: Invalid token")

        return await call_next(context)

mcp = FastMCP("Perplexity MCP Server", lifespan=lifespan)
# Register middlewares in order: sanitize args first, then authenticate
mcp.add_middleware(ArgumentSanitizerMiddleware())
mcp.add_middleware(BearerAuthMiddleware())

@mcp.tool()
async def perplexity_search(query: str) -> str:
    """
    Performs web search using the Perplexity Search API.

    Returns ranked search results with titles, URLs, snippets, and metadata.
    Perfect for finding up-to-date facts, news, or specific information.

    Args:
        query: Search query string

    Returns:
        Answer text with markdown sources list appended
    """
    return await get_search().perplexity_search(query)

@mcp.tool()
async def perplexity_ask(query: str) -> str:
    """
    Engages in a conversation using the Sonar API.

    Accepts a query and returns a chat completion response from the Perplexity model.
    Best for answering questions with up-to-date information.

    Args:
        query: Question to ask

    Returns:
        Answer text with markdown sources list appended
    """
    return await get_search().perplexity_ask(query)

@mcp.tool()
async def perplexity_research(query: str) -> str:
    """
    Performs deep research using the Perplexity API.

    Returns a comprehensive research response with citations.
    Best for in-depth research requiring multiple sources.

    Args:
        query: Research topic or question

    Returns:
        Answer text with markdown sources list appended
    """
    return await get_search().perplexity_research(query)

@mcp.tool()
async def perplexity_reason(query: str) -> str:
    """
    Performs reasoning tasks using the Perplexity API.

    Returns a well-reasoned response using the sonar-reasoning-pro model.
    Best for complex problems requiring step-by-step reasoning.

    Args:
        query: Problem or question requiring reasoning

    Returns:
        Answer text with markdown sources list appended
    """
    return await get_search().perplexity_reason(query)

