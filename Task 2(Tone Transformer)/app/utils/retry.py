"""Retry handling with exponential backoff and jitter for LLM API calls."""

import asyncio
import logging
import random
from typing import Callable, Any, TypeVar
import groq

logger = logging.getLogger("copywriter.retry")

T = TypeVar("T")


class NonRetryableError(Exception):
    """Exception representing permanent errors that should not be retried."""
    pass


def is_retryable_error(exc: Exception) -> bool:
    """Determine whether an exception is temporary and eligible for retry.
    
    Args:
        exc: Caught exception.
        
    Returns:
        True if retryable (e.g. rate limits, timeouts, server 5xx), False otherwise.
    """
    # Fatal authentication or client input errors should fail immediately
    if isinstance(exc, (groq.AuthenticationError, groq.PermissionDeniedError, groq.BadRequestError)):
        return False

    # Retry rate limits, server errors, and network connection drops
    if isinstance(exc, (
        groq.RateLimitError,
        groq.InternalServerError,
        groq.APITimeoutError,
        groq.APIConnectionError
    )):
        return True

    # Generic HTTP or network errors with 429 or 5xx
    status_code = getattr(exc, "status_code", None)
    if status_code is not None:
        if status_code in (429, 500, 502, 503, 504):
            return True
        if status_code in (400, 401, 403, 404, 422):
            return False

    return False


async def retry_with_exponential_backoff(
    coro_fn: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 16.0,
    **kwargs: Any
) -> Any:
    """Execute an asynchronous coroutine with exponential backoff and jitter on transient errors.
    
    Formula:
        delay = min(base_delay * (2 ** attempt) + uniform(0, 1), max_delay)
    
    Args:
        coro_fn: Async callable to execute.
        max_retries: Number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Ceiling delay in seconds.
        
    Returns:
        Result of the coroutine.
        
    Raises:
        Exception: The last caught exception if retries are exhausted or error is non-retryable.
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await coro_fn(*args, **kwargs)
        except Exception as exc:
            last_exception = exc
            
            # Stop immediately if error is non-retryable or we reached maximum retries
            if not is_retryable_error(exc) or attempt == max_retries:
                raise exc

            # Calculate backoff with jitter
            jitter = random.uniform(0.1, 1.0)
            delay = min(base_delay * (2 ** attempt) + jitter, max_delay)
            
            logger.warning(
                f"[Attempt {attempt + 1}/{max_retries}] Transient API error: {exc}. "
                f"Retrying in {delay:.2f} seconds..."
            )
            await asyncio.sleep(delay)

    if last_exception:
        raise last_exception
