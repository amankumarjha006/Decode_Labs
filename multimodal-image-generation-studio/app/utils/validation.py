"""Input validation and sanitization helpers for Stable Diffusion XL parameters."""

from typing import Optional, Tuple
from app.utils.errors import ValidationError

MIN_DIMENSION = 256
MAX_DIMENSION = 2048
MIN_STEPS = 1
MAX_STEPS = 20
MIN_GUIDANCE = 1.0
MAX_GUIDANCE = 20.0
MIN_GENERATION_COUNT = 1
MAX_GENERATION_COUNT = 4


def sanitize_prompt(prompt: str) -> str:
    """Strip extraneous whitespace and validate basic text integrity."""
    if not isinstance(prompt, str):
        raise ValidationError("Prompt must be a string.")
    cleaned = " ".join(prompt.split())
    if not cleaned:
        raise ValidationError("Prompt cannot be empty or only spaces.")
    if len(cleaned) < 3:
        raise ValidationError("Prompt must be at least 3 characters long.")
    if len(cleaned) > 2000:
        raise ValidationError("Prompt cannot exceed 2000 characters.")
    return cleaned


def validate_generation_count(count: int) -> int:
    """Ensure generation count is within supported boundaries (1-4)."""
    if not isinstance(count, int) or count < MIN_GENERATION_COUNT or count > MAX_GENERATION_COUNT:
        raise ValidationError(
            f"Generation count must be an integer between {MIN_GENERATION_COUNT} and {MAX_GENERATION_COUNT}."
        )
    return count


def validate_seed(seed: Optional[int]) -> Optional[int]:
    """Validate optional seed value."""
    if seed is None:
        return None
    if not isinstance(seed, int) or seed < 0 or seed > 2147483647:
        raise ValidationError("Seed must be an integer between 0 and 2,147,483,647.")
    return seed


def validate_num_steps(steps: Optional[int]) -> int:
    """Validate inference steps for Stable Diffusion XL (1 to 20, default 20)."""
    if steps is None:
        return 20
    if not isinstance(steps, int) or steps < MIN_STEPS or steps > MAX_STEPS:
        raise ValidationError(
            f"Number of steps must be an integer between {MIN_STEPS} and {MAX_STEPS}. Received: {steps}."
        )
    return steps


def validate_guidance(guidance: Optional[float]) -> float:
    """Validate guidance scale for Stable Diffusion XL (1.0 to 20.0, default 7.5)."""
    if guidance is None:
        return 7.5
    if not isinstance(guidance, (int, float)) or guidance < MIN_GUIDANCE or guidance > MAX_GUIDANCE:
        raise ValidationError(
            f"Guidance scale must be between {MIN_GUIDANCE} and {MAX_GUIDANCE}. Received: {guidance}."
        )
    return float(guidance)


def validate_dimensions(width: int, height: int) -> Tuple[int, int]:
    """Validate image dimensions (256 <= width <= 2048, 256 <= height <= 2048)."""
    if not (isinstance(width, int) and isinstance(height, int)):
        raise ValidationError(
            f"Width and height must be integers. Received: width={width}, height={height}."
        )
    if not (MIN_DIMENSION <= width <= MAX_DIMENSION and MIN_DIMENSION <= height <= MAX_DIMENSION):
        raise ValidationError(
            f"Invalid image dimensions: {width} × {height}. "
            f"Width and height must be between {MIN_DIMENSION} and {MAX_DIMENSION} pixels."
        )
    return width, height
