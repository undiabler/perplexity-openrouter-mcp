"""
FastMCP tool definitions for Perplexity MCP Server.

These are thin wrappers around PerplexitySearch methods.
All business logic lives in PerplexitySearch.
"""

import os
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from fastmcp.exceptions import ToolError

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
mcp.add_middleware(BearerAuthMiddleware())


@mcp.tool()
async def perplexity_search(query: str) -> dict:
    """
    Performs web search using the Perplexity Search API.

    Returns ranked search results with titles, URLs, snippets, and metadata.
    Perfect for finding up-to-date facts, news, or specific information.

    Args:
        query: Search query string

    Returns:
        Dict with answer and sources (list of {url, title} citations)
    """
    return await get_search().perplexity_search(query)


@mcp.tool()
async def perplexity_ask(query: str) -> dict:
    """
    Engages in a conversation using the Sonar API.

    Accepts a query and returns a chat completion response from the Perplexity model.
    Best for answering questions with up-to-date information.

    Args:
        query: Question to ask

    Returns:
        Dict with answer and sources (list of {url, title} citations)
    """
    return await get_search().perplexity_ask(query)


@mcp.tool()
async def perplexity_research(query: str) -> dict:
    """
    Performs deep research using the Perplexity API.

    Returns a comprehensive research response with citations.
    Best for in-depth research requiring multiple sources.

    Args:
        query: Research topic or question

    Returns:
        Dict with answer and sources (list of {url, title} citations)
    """
    return await get_search().perplexity_research(query)


@mcp.tool()
async def perplexity_reason(query: str) -> dict:
    """
    Performs reasoning tasks using the Perplexity API.

    Returns a well-reasoned response using the sonar-reasoning-pro model.
    Best for complex problems requiring step-by-step reasoning.

    Args:
        query: Problem or question requiring reasoning

    Returns:
        Dict with answer and sources (list of {url, title} citations)
    """
    return await get_search().perplexity_reason(query)

