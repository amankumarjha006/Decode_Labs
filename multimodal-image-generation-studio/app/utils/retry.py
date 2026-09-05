"""Asynchronous retry helper with exponential backoff and jitter."""

import asyncio
import logging
import random
from typing import Awaitable, Callable, Tuple, Type, TypeVar
from app.utils.errors import (
    AuthenticationError,
    CloudflareAPIError,
    ConfigurationError,
    RateLimitError,
    ValidationError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Non-retryable errors that should fail fast
FATAL_ERRORS: Tuple[Type[Exception], ...] = (
    AuthenticationError,
    ConfigurationError,
    ValidationError,
)


async def retry_with_exponential_backoff(
    coro_fn: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 10.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> T:
    """Execute async callable with exponential backoff and random jitter.

    Non-retryable errors (e.g. auth failures, validation errors, 400, 404, daily quota exhaustion) exit immediately.
    """
    delay = initial_delay
    last_exception: Exception = RuntimeError("No execution occurred")

    for attempt in range(max_retries + 1):
        try:
            return await coro_fn()
        except FATAL_ERRORS:
            # Fatal business or auth errors must fail immediately
            raise
        except CloudflareAPIError as exc:
            # Non-retryable Cloudflare status codes: 400 (bad request), 401 (auth), 403 (forbidden), 404 (model not found)
            if exc.status_code in (400, 401, 403, 404):
                raise
            # Check for daily allocation exhaustion on 429
            if getattr(exc, "is_daily_allocation_exhausted", False):
                raise
            last_exception = exc
            if attempt == max_retries:
                break
            jitter = random.uniform(0.8, 1.2)
            sleep_time = round(min(delay * jitter, max_delay), 2)
            logger.warning(
                "Retry attempt %d/%d after %.1f seconds due to %s",
                attempt + 1,
                max_retries,
                sleep_time,
                f"HTTP {exc.status_code}" if exc.status_code else str(exc),
            )
            await asyncio.sleep(sleep_time)
            delay *= backoff_factor
        except retryable_exceptions as exc:
            last_exception = exc
            if attempt == max_retries:
                break

            jitter = random.uniform(0.8, 1.2)
            sleep_time = round(min(delay * jitter, max_delay), 2)
            logger.warning(
                "Retry attempt %d/%d after %.1f seconds due to %s",
                attempt + 1,
                max_retries,
                sleep_time,
                type(exc).__name__,
            )
            await asyncio.sleep(sleep_time)
            delay *= backoff_factor

    raise last_exception
