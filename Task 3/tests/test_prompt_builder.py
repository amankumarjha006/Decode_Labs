"""Unit tests for style presets and prompt enhancement builder."""

from app.models import ImageStyle
from app.prompts.prompt_builder import build_enhanced_prompt
from app.prompts.style_presets import STYLE_PRESETS, get_style_modifiers


def test_prompt_builder_preserves_original_prompt():
    """Verify that original prompt is preserved exactly."""
    original = "A vintage train traveling through snow mountains"
    result = build_enhanced_prompt(original, style=ImageStyle.CYBERPUNK)
    assert result.original_prompt == original
    assert result.enhanced_prompt.startswith(original)


def test_none_style_does_not_overmodify():
    """Verify that style None leaves prompt unaltered."""
    original = "A beautiful sunset over the ocean"
    result = build_enhanced_prompt(original, style=ImageStyle.NONE)
    assert result.original_prompt == original
    assert result.enhanced_prompt == original
    assert result.applied_modifiers == []


def test_style_modifiers_applied():
    """Verify style modifiers are appended for specific styles."""
    original = "A solitary warrior"
    result = build_enhanced_prompt(original, style=ImageStyle.ANIME)
    assert result.style == ImageStyle.ANIME
    assert len(result.applied_modifiers) > 0
    assert "anime aesthetic" in result.enhanced_prompt.lower()
    assert result.enhanced_prompt.startswith(original)


def test_modifier_deduplication():
    """Verify that keywords already in the user's prompt are not duplicated."""
    original = "A photorealistic portrait of an elder with realistic lighting"
    result = build_enhanced_prompt(original, style=ImageStyle.PHOTOREALISTIC)
    # 'photorealistic' and 'realistic lighting' were in the original prompt
    assert "photorealistic" not in result.applied_modifiers
    assert "realistic lighting" not in result.applied_modifiers


def test_all_styles_have_definitions():
    """Verify all ImageStyle enum members exist in STYLE_PRESETS."""
    for style in ImageStyle:
        modifiers = get_style_modifiers(style)
        assert isinstance(modifiers, list)
        if style == ImageStyle.NONE:
            assert len(modifiers) == 0
        else:
            assert len(modifiers) > 0
