"""Unit tests for Pydantic models, validation constraints, and enums."""

import pytest
from pydantic import ValidationError
from app.models import GenerationRequest, GenerationResponse, Platform, Tone


def test_valid_generation_request():
    """Verify that a properly constructed request passes validation."""
    req = GenerationRequest(
        product_name="EcoBottle",
        product_description="A stainless steel insulated water bottle for outdoor adventurers.",
        platform=Platform.INSTAGRAM,
        tone=Tone.WITTY,
        temperature=0.8,
        top_p=0.95,
        max_output_tokens=300,
    )
    assert req.product_name == "EcoBottle"
    assert req.platform == Platform.INSTAGRAM
    assert req.tone == Tone.WITTY
    assert req.temperature == 0.8
    assert req.top_p == 0.95
    assert req.max_output_tokens == 300


def test_case_insensitive_enums():
    """Verify that enums accept mixed-case strings."""
    req = GenerationRequest(
        product_name="PowerBank",
        product_description="A 20000mAh portable charger with USB-C fast charging.",
        platform="INSTAGRAM",
        tone="LuXuRy",
    )
    assert req.platform == Platform.INSTAGRAM
    assert req.tone == Tone.LUXURY


def test_invalid_temperature_low():
    """Temperature below 0.0 must raise ValidationError."""
    with pytest.raises(ValidationError):
        GenerationRequest(
            product_name="Test Product",
            product_description="Test description with adequate characters.",
            platform=Platform.LINKEDIN,
            tone=Tone.PROFESSIONAL,
            temperature=-0.1,
        )


def test_invalid_temperature_high():
    """Temperature above 2.0 must raise ValidationError."""
    with pytest.raises(ValidationError):
        GenerationRequest(
            product_name="Test Product",
            product_description="Test description with adequate characters.",
            platform=Platform.LINKEDIN,
            tone=Tone.PROFESSIONAL,
            temperature=2.5,
        )


def test_invalid_top_p():
    """Top-p outside [0.0, 1.0] must raise ValidationError."""
    with pytest.raises(ValidationError):
        GenerationRequest(
            product_name="Test Product",
            product_description="Test description with adequate characters.",
            platform=Platform.LINKEDIN,
            tone=Tone.PROFESSIONAL,
            top_p=1.2,
        )


def test_empty_product_name():
    """Empty or whitespace-only product name must raise ValidationError."""
    with pytest.raises(ValidationError):
        GenerationRequest(
            product_name="   ",
            product_description="Valid product description text.",
            platform=Platform.EMAIL,
            tone=Tone.FRIENDLY,
        )


def test_too_short_product_description():
    """Description shorter than 10 characters must raise ValidationError."""
    with pytest.raises(ValidationError):
        GenerationRequest(
            product_name="Gadget",
            product_description="Short",
            platform=Platform.EMAIL,
            tone=Tone.FRIENDLY,
        )


def test_invalid_platform():
    """Nonexistent platform must raise ValidationError."""
    with pytest.raises(ValidationError):
        GenerationRequest(
            product_name="Smart Watch",
            product_description="Fitness tracking watch with heart rate sensor.",
            platform="myspace",
            tone=Tone.CASUAL,
        )


def test_generation_response_auto_counts():
    """Verify word and character counts are calculated automatically."""
    resp = GenerationResponse(
        product_name="Smart Watch",
        platform=Platform.LINKEDIN,
        tone=Tone.PROFESSIONAL,
        generated_copy="Transform your daily productivity with our next-generation smartwatch.",
        model_used="gpt-4.1-mini",
        temperature=0.7,
        top_p=0.9,
    )
    assert resp.character_count == len(resp.generated_copy)
    assert resp.word_count == len(resp.generated_copy.split())
