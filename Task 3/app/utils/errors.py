"""Custom domain exceptions and error helpers for the Image Generation Studio."""

from typing import Any, Dict, Optional


def sanitize_debug_data(data: Any) -> Any:
    """Recursively sanitize sensitive fields in dicts, lists, strings, or debug objects.

    Redacts values associated with keys containing: token, authorization, secret, password, api_key.
    """
    sensitive_substrings = ("token", "authorization", "secret", "password", "api_key")

    if isinstance(data, dict):
        sanitized: Dict[str, Any] = {}
        for k, v in data.items():
            key_lower = str(k).lower()
            if any(sub in key_lower for sub in sensitive_substrings):
                sanitized[k] = "***REDACTED***"
            else:
                sanitized[k] = sanitize_debug_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_debug_data(item) for item in data]
    elif isinstance(data, str):
        # Look for Bearer token patterns in raw string
        if "bearer " in data.lower():
            import re
            return re.sub(r'(?i)bearer\s+[a-zA-Z0-9_\-\.]+', 'Bearer ***REDACTED***', data)
        return data
    return data


class StudioError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, user_friendly_message: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.user_friendly_message = user_friendly_message or message


class CloudflareAPIError(StudioError):
    """Structured custom exception capturing detailed Cloudflare API error information."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        response_body: Optional[str] = None,
        user_friendly_message: Optional[str] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.response_body = response_body
        super().__init__(message, user_friendly_message=user_friendly_message or message)


class ConfigurationError(StudioError):
    """Raised when required environment or provider configuration is missing."""
    pass


class AuthenticationError(CloudflareAPIError):
    """Raised when Cloudflare authentication or authorization fails (401/403)."""
    pass


class RateLimitError(CloudflareAPIError):
    """Raised when the provider API returns HTTP 429 Too Many Requests."""

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        error_code: Optional[str] = None,
        response_body: Optional[str] = None,
        is_daily_allocation_exhausted: bool = False,
        user_friendly_message: Optional[str] = None,
    ):
        self.is_daily_allocation_exhausted = is_daily_allocation_exhausted
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            response_body=response_body,
            user_friendly_message=user_friendly_message,
        )


class TimeoutError(StudioError):
    """Raised when an API request exceeds the configured timeout."""
    pass


class NetworkError(StudioError):
    """Raised when low-level network connectivity or DNS fails."""
    pass


class ModelError(StudioError):
    """Raised when the AI model returns an error during inference."""
    pass


class ValidationError(StudioError):
    """Raised when request inputs fail semantic validation."""
    pass


class ImageProcessingError(StudioError):
    """Raised when image bytes cannot be parsed, validated, or decoded."""
    pass


class StorageError(StudioError):
    """Raised when saving generated images or metadata to disk fails."""
    pass
