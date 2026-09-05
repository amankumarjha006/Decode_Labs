"""Unit tests for output validation and mocked pipeline execution without an API key."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models import GenerationRequest, Platform, Tone
from app.services.generator import CopyGenerator
from app.services.llm_service import LLMService
from app.utils.validation import (
    validate_output,
    is_twitter_over_limit,
    is_empty_or_whitespace,
)


def test_empty_generated_copy_rejected():
    """Empty or whitespace-only text must fail validation."""
    assert is_empty_or_whitespace("") is True
    assert is_empty_or_whitespace("   \n\t  ") is True
    assert is_empty_or_whitespace("Valid copy text") is False

    is_valid, msg = validate_output("", Platform.LINKEDIN)
    assert is_valid is False
    assert "empty" in msg.lower()


def test_twitter_length_validation():
    """Twitter validation must fail when text exceeds 280 characters."""
    short_text = "Check out our new smart bottle! Keeps your drinks cold for 24 hours. #EcoLiving"
    assert is_twitter_over_limit(short_text) is False

    valid, msg = validate_output(short_text, Platform.TWITTER)
    assert valid is True
    assert msg is None

    long_text = "A" * 281
    assert is_twitter_over_limit(long_text) is True
    valid, msg = validate_output(long_text, Platform.TWITTER)
    assert valid is False
    assert "280" in msg


def test_email_validation_warning():
    """Email validation returns a notice if no Subject line is found."""
    email_without_subject = "Hi team,\nHere is our product announcement.\nClick here!"
    valid, msg = validate_output(email_without_subject, Platform.EMAIL)
    assert valid is True
    assert msg is not None
    assert "Subject" in msg

    email_with_subject = "Subject: Elevate your workflow\n\nHi Alex,\nCheck out our tool.\nBest,\nTeam"
    valid, msg = validate_output(email_with_subject, Platform.EMAIL)
    assert valid is True
    assert msg is None


@pytest.mark.asyncio
async def test_generator_with_mocked_llm():
    """Verify CopyGenerator executes seamlessly with a mocked LLM service (no API key needed)."""
    mock_llm = MagicMock(spec=LLMService)
    mock_llm.model_name = "mock-gpt-4"
    mock_llm.generate_completion = AsyncMock(
        return_value="🚀 Revolutionize your enterprise data with CloudScale AI. Reduce compute by 40%."
    )

    generator = CopyGenerator(llm_service=mock_llm)
    req = GenerationRequest(
        product_name="CloudScale AI",
        product_description="Enterprise cloud cost optimization powered by predictive models.",
        platform=Platform.LINKEDIN,
        tone=Tone.PROFESSIONAL,
    )

    response = await generator.generate_copy(req)

    assert response.product_name == "CloudScale AI"
    assert response.platform == Platform.LINKEDIN
    assert response.model_used == "mock-gpt-4"
    assert "Revolutionize your enterprise data" in response.generated_copy
    assert response.character_count > 0
    assert response.word_count > 0
    assert mock_llm.generate_completion.called


@pytest.mark.asyncio
async def test_twitter_shortening_pass_triggered_when_over_limit():
    """Verify that if Twitter output exceeds 280 characters, a shortening pass is executed."""
    initial_long_copy = "B" * 320
    shortened_copy = "C" * 200

    mock_llm = MagicMock(spec=LLMService)
    mock_llm.model_name = "mock-gpt-4"
    # First call returns too long, second call returns shortened
    mock_llm.generate_completion = AsyncMock(
        side_effect=[initial_long_copy, shortened_copy]
    )

    generator = CopyGenerator(llm_service=mock_llm)
    req = GenerationRequest(
        product_name="PocketDrone",
        product_description="Foldable 4K pocket drone with obstacle avoidance.",
        platform=Platform.TWITTER,
        tone=Tone.EXCITING,
    )

    response = await generator.generate_copy(req)

    assert mock_llm.generate_completion.call_count == 2
    assert response.generated_copy == shortened_copy
    assert response.character_count == 200
