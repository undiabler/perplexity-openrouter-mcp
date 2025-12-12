"""
Perplexity web search tools via OpenRouter.
Provides 4 tools matching the official Perplexity MCP interface.
"""

from src.openrouter_client import OpenRouterClient


class PerplexitySearch:
    """
    Perplexity search service with 4 tool methods.
    Each tool uses a specific Perplexity model optimized for its purpose.
    """

    # Model constants
    MODEL_SEARCH = "perplexity/sonar"
    MODEL_ASK = "perplexity/sonar-pro"
    MODEL_RESEARCH = "perplexity/sonar-deep-research"
    MODEL_REASON = "perplexity/sonar-reasoning-pro"

    def __init__(self, api_key: str | None = None):
        """
        Initialize Perplexity search service.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
        """
        self.client = OpenRouterClient(api_key=api_key)

    def _format_citations(self, content: str, annotations: list | None) -> list[dict]:
        """
        Extract citation sources from annotations.

        Args:
            content: The LLM response content with [1], [2] style citations
            annotations: List of annotation objects from the API response

        Returns:
            List of source dicts with url and title
        """
        if not annotations:
            return []

        sources = []
        for ann in annotations:
            # Handle both dict and object formats
            if isinstance(ann, dict):
                ann_type = ann.get("type")
                url_citation = ann.get("url_citation", {})
            else:
                ann_type = getattr(ann, "type", None)
                url_citation = getattr(ann, "url_citation", {})

            if ann_type == "url_citation":
                # Extract URL and title
                if isinstance(url_citation, dict):
                    url = url_citation.get("url", "")
                    title = url_citation.get("title", url)
                else:
                    url = getattr(url_citation, "url", "")
                    title = getattr(url_citation, "title", url)

                if url:
                    sources.append({"url": url, "title": title})

        return sources

    async def _query(self, query: str, model: str) -> dict:
        """
        Internal method to query a Perplexity model.

        Args:
            query: User query
            model: Perplexity model to use

        Returns:
            Dict with answer and sources
        """
        response = await self.client.chat_completion(
            prompt=query,
            model=model,
        )

        sources = self._format_citations(response["content"], response["annotations"])

        return {
            "answer": response["content"],
            "sources": sources,
        }

    async def perplexity_search(self, query: str) -> dict:
        """
        Direct web search using Perplexity Search API.
        Best for: Finding current information quickly.

        Args:
            query: Search query

        Returns:
            Dict with answer and sources
        """
        return await self._query(query, self.MODEL_SEARCH)

    async def perplexity_ask(self, query: str) -> dict:
        """
        General-purpose conversational AI with real-time web search.
        Best for: Answering questions with up-to-date information.

        Args:
            query: Question to ask

        Returns:
            Dict with answer and sources
        """
        return await self._query(query, self.MODEL_ASK)

    async def perplexity_research(self, query: str) -> dict:
        """
        Deep, comprehensive research using sonar-deep-research model.
        Best for: In-depth research requiring multiple sources.

        Args:
            query: Research topic or question

        Returns:
            Dict with answer and sources
        """
        return await self._query(query, self.MODEL_RESEARCH)

    async def perplexity_reason(self, query: str) -> dict:
        """
        Advanced reasoning and problem-solving.
        Best for: Complex problems requiring step-by-step reasoning.

        Args:
            query: Problem or question requiring reasoning

        Returns:
            Dict with answer and sources
        """
        return await self._query(query, self.MODEL_REASON)

    async def close(self) -> None:
        """Close the client connection."""
        await self.client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

