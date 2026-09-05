"""Utility functions and error definitions."""

from app.utils.errors import (
    StudioError,
    CloudflareAPIError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    NetworkError,
    ModelError,
    ValidationError,
    ImageProcessingError,
    StorageError,
    sanitize_debug_data,
)
from app.utils.image_utils import (
    RESOLUTION_MAP,
    MIN_DIMENSION,
    MAX_DIMENSION,
    get_target_dimensions,
    validate_and_inspect_image,
)
from app.utils.retry import retry_with_exponential_backoff
from app.utils.validation import (
    sanitize_prompt,
    validate_generation_count,
    validate_seed,
    validate_dimensions,
    validate_num_steps,
    validate_guidance,
)

__all__ = [
    "StudioError",
    "CloudflareAPIError",
    "ConfigurationError",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutError",
    "NetworkError",
    "ModelError",
    "ValidationError",
    "ImageProcessingError",
    "StorageError",
    "sanitize_debug_data",
    "RESOLUTION_MAP",
    "MIN_DIMENSION",
    "MAX_DIMENSION",
    "get_target_dimensions",
    "validate_and_inspect_image",
    "retry_with_exponential_backoff",
    "sanitize_prompt",
    "validate_generation_count",
    "validate_seed",
    "validate_dimensions",
    "validate_num_steps",
    "validate_guidance",
]
