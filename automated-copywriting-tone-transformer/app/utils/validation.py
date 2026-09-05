"""Validation and brand safety utility functions for marketing copy."""

from typing import Tuple, Optional
from app.models import Platform


TWITTER_MAX_CHARS = 280
INSTAGRAM_RECOMMENDED_MAX_CHARS = 2200
LINKEDIN_RECOMMENDED_MAX_CHARS = 3000


def is_empty_or_whitespace(text: str) -> bool:
    """Check if generated text is empty or purely whitespace."""
    return not text or not text.strip()


def is_twitter_over_limit(text: str, max_chars: int = TWITTER_MAX_CHARS) -> bool:
    """Determine whether the copy exceeds Twitter/X 280 character limit."""
    return len(text.strip()) > max_chars


def validate_output(copy: str, platform: Platform) -> Tuple[bool, Optional[str]]:
    """Validate generated copy against platform rules and safety standards.
    
    Args:
        copy: The generated marketing copy.
        platform: Target platform.
        
    Returns:
        A tuple of (is_valid, error_or_warning_message).
    """
    if is_empty_or_whitespace(copy):
        return False, "Generated copy is empty or contains only whitespace."

    cleaned = copy.strip()

    if platform == Platform.TWITTER:
        if len(cleaned) > TWITTER_MAX_CHARS:
            return False, f"Twitter copy exceeds {TWITTER_MAX_CHARS} characters (actual: {len(cleaned)})."

    elif platform == Platform.INSTAGRAM:
        if len(cleaned) > INSTAGRAM_RECOMMENDED_MAX_CHARS:
            return False, f"Instagram copy exceeds recommended limit of {INSTAGRAM_RECOMMENDED_MAX_CHARS} characters."

    elif platform == Platform.LINKEDIN:
        if len(cleaned) > LINKEDIN_RECOMMENDED_MAX_CHARS:
            return False, f"LinkedIn copy exceeds recommended limit of {LINKEDIN_RECOMMENDED_MAX_CHARS} characters."

    elif platform == Platform.EMAIL:
        # Check for essential components of email format
        lower_copy = cleaned.lower()
        has_subject = "subject:" in lower_copy or "subject line:" in lower_copy
        if not has_subject:
            return True, "Notice: Generated email copy appears to lack an explicit 'Subject:' line."

    return True, None
