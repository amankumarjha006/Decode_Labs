"""Unit tests for dynamic master prompt template compilation."""

from app.models import GenerationRequest, Platform, Tone
from app.prompts.master_template import compile_master_prompt, compile_shorten_prompt


def test_prompt_compilation_contains_key_variables():
    """Verify that product name, description, platform, tone, and rules appear in the compiled prompt."""
    req = GenerationRequest(
        product_name="AeroGlide Shoes",
        product_description="Ultra-light carbon fiber marathon running shoes engineered for peak speed.",
        platform=Platform.LINKEDIN,
        tone=Tone.PROFESSIONAL,
        temperature=0.3,
        top_p=0.85,
    )

    compiled = compile_master_prompt(req)

    # Required variables
    assert "AeroGlide Shoes" in compiled
    assert "Ultra-light carbon fiber marathon running shoes" in compiled
    assert "LINKEDIN" in compiled
    assert "PROFESSIONAL" in compiled

    # LinkedIn specific rules
    assert "B2B decision makers" in compiled or "LinkedIn" in compiled
    assert "ROI" in compiled or "hook" in compiled


def test_instagram_prompt_rules():
    """Verify Instagram-specific rules are inserted for Instagram requests."""
    req = GenerationRequest(
        product_name="GlowSerum",
        product_description="Hydrating vitamin C facial serum made from organic cold-pressed botanicals.",
        platform=Platform.INSTAGRAM,
        tone=Tone.WITTY,
        temperature=0.8,
        top_p=0.9,
    )

    compiled = compile_master_prompt(req)
    assert "INSTAGRAM" in compiled
    assert "WITTY" in compiled
    assert "emoji" in compiled.lower()
    assert "hashtag" in compiled.lower()


def test_email_prompt_rules():
    """Verify Email structure rules are inserted."""
    req = GenerationRequest(
        product_name="DevSprint",
        product_description="Agile project management dashboard for engineering teams.",
        platform=Platform.EMAIL,
        tone=Tone.PERSUASIVE,
    )

    compiled = compile_master_prompt(req)
    assert "EMAIL" in compiled
    assert "Subject Line:" in compiled
    assert "Call to Action (CTA):" in compiled
    assert "DO NOT include social media hashtags" in compiled


def test_shorten_prompt_compilation():
    """Verify shorten prompt compilation correctly targets character limit."""
    req = GenerationRequest(
        product_name="PocketDrone",
        product_description="Foldable 4K pocket drone with obstacle avoidance.",
        platform=Platform.TWITTER,
        tone=Tone.EXCITING,
    )
    long_copy = "A" * 350
    shorten_prompt = compile_shorten_prompt(req, long_copy, max_chars=280)

    assert "350 characters" in shorten_prompt
    assert "280 characters" in shorten_prompt
    assert "PocketDrone" in shorten_prompt
