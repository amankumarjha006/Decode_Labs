"""Unit tests for input validation, boundary checks, and security sanitization."""

import pytest
from app.utils.errors import ValidationError, sanitize_debug_data
from app.utils.validation import (
    sanitize_prompt,
    validate_dimensions,
    validate_generation_count,
    validate_guidance,
    validate_num_steps,
    validate_seed,
)


def test_sanitize_valid_prompt():
    """Test standard valid prompt sanitization."""
    raw = "   A   magnificent forest    with glowing trees   "
    cleaned = sanitize_prompt(raw)
    assert cleaned == "A magnificent forest with glowing trees"


def test_sanitize_empty_prompt():
    """Test empty prompt raises ValidationError."""
    with pytest.raises(ValidationError):
        sanitize_prompt("")

    with pytest.raises(ValidationError):
        sanitize_prompt("    ")


def test_sanitize_short_prompt():
    """Test prompt under 3 characters raises ValidationError."""
    with pytest.raises(ValidationError):
        sanitize_prompt("hi")


def test_sanitize_long_prompt():
    """Test prompt over 2000 characters raises ValidationError."""
    with pytest.raises(ValidationError):
        sanitize_prompt("a" * 2001)


def test_valid_dimensions():
    """Requirement 4: Test valid dimensions between 256 and 2048."""
    assert validate_dimensions(256, 256) == (256, 256)
    assert validate_dimensions(1024, 768) == (1024, 768)
    assert validate_dimensions(2048, 2048) == (2048, 2048)


def test_width_below_256_rejected():
    """Requirement 5: Width below 256 rejected."""
    with pytest.raises(ValidationError) as exc:
        validate_dimensions(255, 512)
    assert "between 256 and 2048" in str(exc.value)


def test_width_above_2048_rejected():
    """Requirement 6: Width above 2048 rejected."""
    with pytest.raises(ValidationError) as exc:
        validate_dimensions(2049, 512)
    assert "between 256 and 2048" in str(exc.value)


def test_height_below_256_rejected():
    """Requirement 7: Height below 256 rejected."""
    with pytest.raises(ValidationError) as exc:
        validate_dimensions(512, 255)
    assert "between 256 and 2048" in str(exc.value)


def test_height_above_2048_rejected():
    """Requirement 8: Height above 2048 rejected."""
    with pytest.raises(ValidationError) as exc:
        validate_dimensions(512, 2049)
    assert "between 256 and 2048" in str(exc.value)


def test_steps_below_1_rejected():
    """Requirement 9: Steps below 1 rejected."""
    with pytest.raises(ValidationError):
        validate_num_steps(0)


def test_steps_above_20_rejected():
    """Requirement 10: Steps above 20 rejected."""
    with pytest.raises(ValidationError):
        validate_num_steps(21)


def test_valid_steps():
    """Test valid step range (1 to 20)."""
    assert validate_num_steps(1) == 1
    assert validate_num_steps(20) == 20
    assert validate_num_steps(None) == 20  # Default


def test_guidance_validation():
    """Test guidance scale range 1.0 to 20.0."""
    assert validate_guidance(1.0) == 1.0
    assert validate_guidance(7.5) == 7.5
    assert validate_guidance(20.0) == 20.0
    with pytest.raises(ValidationError):
        validate_guidance(0.5)
    with pytest.raises(ValidationError):
        validate_guidance(25.0)


def test_generation_count_below_1_rejected():
    """Requirement 11: Generation count below 1 rejected."""
    with pytest.raises(ValidationError):
        validate_generation_count(0)


def test_generation_count_above_4_rejected():
    """Requirement 12: Generation count above 4 rejected."""
    with pytest.raises(ValidationError):
        validate_generation_count(5)


def test_valid_generation_count():
    """Test valid generation counts (1 to 4)."""
    assert validate_generation_count(1) == 1
    assert validate_generation_count(4) == 4


def test_validate_seed():
    """Requirement 3 related: Validate seed behavior."""
    assert validate_seed(None) is None
    assert validate_seed(0) == 0
    assert validate_seed(42) == 42
    with pytest.raises(ValidationError):
        validate_seed(-5)
    with pytest.raises(ValidationError):
        validate_seed(2147483648)


def test_sensitive_data_sanitization():
    """Requirement 14: Sensitive data sanitization helper."""
    raw_debug = {
        "model": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
        "CLOUDFLARE_API_TOKEN": "secret_token_12345",
        "authorization": "Bearer secret_bearer_token",
        "api_key": "my_secret_key",
        "password": "super_secret_password",
        "nested": {
            "token": "nested_token",
            "safe_param": "visible_value",
        },
        "safe_list": ["item1", {"auth_token": "secret_in_list"}],
    }
    sanitized = sanitize_debug_data(raw_debug)

    assert sanitized["model"] == "@cf/stabilityai/stable-diffusion-xl-base-1.0"
    assert sanitized["CLOUDFLARE_API_TOKEN"] == "***REDACTED***"
    assert sanitized["authorization"] == "***REDACTED***"
    assert sanitized["api_key"] == "***REDACTED***"
    assert sanitized["password"] == "***REDACTED***"
    assert sanitized["nested"]["token"] == "***REDACTED***"
    assert sanitized["nested"]["safe_param"] == "visible_value"
    assert sanitized["safe_list"][1]["auth_token"] == "***REDACTED***"
