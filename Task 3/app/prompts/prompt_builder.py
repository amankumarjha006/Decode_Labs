"""Prompt builder and enhancement engine."""

from dataclasses import dataclass
from typing import List, Union
from app.models import ImageStyle
from app.prompts.style_presets import get_style_modifiers


@dataclass(frozen=True)
class EnhancedPromptResult:
    """Encapsulates prompt enhancement output."""

    original_prompt: str
    enhanced_prompt: str
    style: ImageStyle
    applied_modifiers: List[str]


def build_enhanced_prompt(
    prompt: str, style: Union[ImageStyle, str] = ImageStyle.NONE
) -> EnhancedPromptResult:
    """Build enhanced prompt by intelligently appending style modifiers.

    Preserves the user's original prompt verbatim, and avoids repeating
    modifier keywords if they already exist in the prompt.
    """
    raw_prompt = prompt.strip()
    if isinstance(style, str):
        try:
            style = ImageStyle(style.lower())
        except ValueError:
            style = ImageStyle.NONE

    modifiers = get_style_modifiers(style)

    if not modifiers or style == ImageStyle.NONE:
        return EnhancedPromptResult(
            original_prompt=raw_prompt,
            enhanced_prompt=raw_prompt,
            style=style,
            applied_modifiers=[],
        )

    # Filter out modifiers that already exist in the prompt (case-insensitive)
    lower_prompt = raw_prompt.lower()
    applicable_modifiers = [
        mod for mod in modifiers if mod.lower() not in lower_prompt
    ]

    if not applicable_modifiers:
        return EnhancedPromptResult(
            original_prompt=raw_prompt,
            enhanced_prompt=raw_prompt,
            style=style,
            applied_modifiers=[],
        )

    modifier_str = ", ".join(applicable_modifiers)
    # Strip any trailing punctuation before joining
    clean_base = raw_prompt.rstrip(".,; ")
    enhanced = f"{clean_base}, {modifier_str}"

    return EnhancedPromptResult(
        original_prompt=raw_prompt,
        enhanced_prompt=enhanced,
        style=style,
        applied_modifiers=applicable_modifiers,
    )
