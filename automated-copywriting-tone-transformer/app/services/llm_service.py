"""Groq LLM integration service with async client and resilience."""

from typing import Optional
import groq
from app.config import (
    GROQ_API_KEY,
    MODEL_NAME,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    validate_api_key,
    get_api_key_help,
)
from app.utils.retry import retry_with_exponential_backoff


class ApiKeyMissingError(Exception):
    """Raised when the Groq API key is missing or improperly configured."""
    pass


class LLMService:
    """Service wrapper for asynchronous Groq Chat Completions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        max_retries: int = MAX_RETRIES,
        timeout: float = REQUEST_TIMEOUT,
        client: Optional[groq.AsyncGroq] = None,
    ):
        self.api_key = (api_key or GROQ_API_KEY).strip()
        self.model_name = model_name or MODEL_NAME
        self.max_retries = max_retries
        self.timeout = timeout
        self._custom_client = client

    def get_client(self) -> groq.AsyncGroq:
        """Instantiate or return the AsyncGroq client, validating the key first."""
        if self._custom_client:
            return self._custom_client

        if not validate_api_key(self.api_key):
            raise ApiKeyMissingError(get_api_key_help())

        return groq.AsyncGroq(
            api_key=self.api_key,
            timeout=self.timeout,
        )

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 500,
    ) -> str:
        """Call Groq Chat Completions asynchronously with retry logic.
        
        Args:
            system_prompt: Guiding system instruction.
            user_prompt: Dynamically compiled prompt for the task.
            temperature: Sampling temperature (0.0 to 2.0).
            top_p: Nucleus sampling cutoff (0.0 to 1.0).
            max_tokens: Maximum tokens in completion.
            
        Returns:
            Generated text content.
            
        Raises:
            ApiKeyMissingError: If API key is not configured.
            Exception: If API request fails after retries.
        """
        client = self.get_client()

        async def _call_api() -> str:
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
            choice = response.choices[0]
            content = choice.message.content or ""
            return content.strip()

        return await retry_with_exponential_backoff(
            _call_api,
            max_retries=self.max_retries
        )
