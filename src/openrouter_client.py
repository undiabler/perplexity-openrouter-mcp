"""
Generic OpenRouter client using OpenAI SDK with async support.
"""

import os

import httpx
from openai import AsyncOpenAI

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

class OpenRouterClient:
    """
    Async client for OpenRouter API.
    Validates API key on initialization.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)

        Raises:
            ValueError: If API key is not provided or invalid
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not configured. "
                "Set OPENROUTER_API_KEY environment variable."
            )

        self._client: AsyncOpenAI | None = None

    async def _validate_api_key(self) -> None:
        """Validate API key via OpenRouter auth endpoint."""
        async with httpx.AsyncClient() as http:
            response = await http.get(
                f"{OPENROUTER_BASE_URL}/auth/key",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            if response.status_code != 200:
                raise ValueError(
                    f"Invalid OpenRouter API key (status {response.status_code})"
                )

    async def _get_client(self) -> AsyncOpenAI:
        """Get or create the OpenAI client, validating key on first use."""
        if self._client is None:
            await self._validate_api_key()
            self._client = AsyncOpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=self.api_key,
            )
        return self._client

    async def chat_completion(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
    ) -> dict:
        """
        Send chat completion request to OpenRouter.

        Args:
            prompt: User prompt/question (required)
            model: Model identifier (required, e.g. "perplexity/sonar-pro")
            system_prompt: Optional system message

        Returns:
            Dict with content, model, tokens, annotations (if available)
        """
        client = await self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
        )

        choice = response.choices[0]

        # Extract annotations (citations) if available
        annotations = None
        if hasattr(choice.message, "annotations"):
            annotations = choice.message.annotations

        return {
            "content": choice.message.content or "",
            "model": response.model,
            "tokens": response.usage.total_tokens if response.usage else 0,
            "annotations": annotations,
        }

    async def close(self) -> None:
        """Close the client connection."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

