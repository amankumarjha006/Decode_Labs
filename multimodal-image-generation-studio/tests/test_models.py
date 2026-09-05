"""Unit tests for Pydantic domain models and validation for Stable Diffusion XL."""

import pytest
from pydantic import ValidationError
from app.models import (
    AspectRatio,
    GeneratedImageItem,
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageStyle,
    ResolutionPreset,
)


def test_valid_sdxl_request():
    """Test that a well-formed SDXL request instantiates successfully."""
    req = ImageGenerationRequest(
        prompt="A serene cyberpunk city in rain",
        negative_prompt="blurry, distorted",
        style=ImageStyle.CYBERPUNK,
        aspect_ratio=AspectRatio.RATIO_16_9,
        resolution=ResolutionPreset.HIGH,
        width=1024,
        height=576,
        generation_count=2,
        seed=12345,
        num_steps=20,
        guidance=7.5,
    )
    assert req.prompt == "A serene cyberpunk city in rain"
    assert req.negative_prompt == "blurry, distorted"
    assert req.style == ImageStyle.CYBERPUNK
    assert req.aspect_ratio == AspectRatio.RATIO_16_9
    assert req.resolution == ResolutionPreset.HIGH
    assert req.width == 1024
    assert req.height == 576
    assert req.generation_count == 2
    assert req.seed == 12345
    assert req.num_steps == 20
    assert req.guidance == 7.5


def test_defaults_sdxl_request():
    """Test default values for SDXL parameters."""
    req = ImageGenerationRequest(prompt="A simple prompt")
    assert req.num_steps == 20
    assert req.guidance == 7.5
    assert req.negative_prompt is None
    assert req.seed is None
    assert req.generation_count == 1


def test_empty_prompt_rejection():
    """Test that empty or whitespace prompts are rejected."""
    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="")

    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="   ")

    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="ab")  # Less than 3 chars


def test_prompt_whitespace_stripping():
    """Test that leading/trailing whitespaces are stripped."""
    req = ImageGenerationRequest(prompt="   Floating castle   ")
    assert req.prompt == "Floating castle"


def test_negative_prompt_handling():
    """Test negative prompt stripping and None behavior."""
    req1 = ImageGenerationRequest(prompt="Castle", negative_prompt="   ")
    assert req1.negative_prompt is None

    req2 = ImageGenerationRequest(prompt="Castle", negative_prompt="  ugly, text  ")
    assert req2.negative_prompt == "ugly, text"


def test_invalid_generation_count():
    """Test that generation count outside 1-4 is rejected."""
    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="Valid prompt", generation_count=0)

    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="Valid prompt", generation_count=5)


def test_invalid_num_steps():
    """Test that steps outside 1-20 are rejected."""
    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="Valid prompt", num_steps=0)

    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="Valid prompt", num_steps=21)


def test_invalid_guidance():
    """Test that guidance outside 1.0-20.0 is rejected."""
    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="Valid prompt", guidance=0.5)

    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="Valid prompt", guidance=25.0)


def test_dimension_validation_on_request():
    """Test dimension validation when explicitly set on request."""
    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="Valid prompt", width=255, height=512)

    with pytest.raises(ValidationError):
        ImageGenerationRequest(prompt="Valid prompt", width=1024, height=2049)


def test_response_model_instantiation():
    """Test that response model serializes correctly with SDXL metadata."""
    img_item = GeneratedImageItem(
        image_id="abc12345",
        local_path="/path/to/image.png",
        file_name="image_20260101_120000_abc12345.png",
        mime_type="image/png",
        width=1024,
        height=576,
        file_size_bytes=102400,
    )

    resp = ImageGenerationResponse(
        request_id="req_9876",
        original_prompt="Cyberpunk car",
        enhanced_prompt="Cyberpunk car, neon lights, futuristic",
        negative_prompt="blurry, distorted",
        style=ImageStyle.CYBERPUNK,
        aspect_ratio=AspectRatio.RATIO_16_9,
        resolution=ResolutionPreset.HIGH,
        width=1024,
        height=576,
        num_steps=20,
        guidance=7.5,
        seed=42,
        model_used="@cf/stabilityai/stable-diffusion-xl-base-1.0",
        images=[img_item],
        generation_time_seconds=2.45,
    )

    assert resp.request_id == "req_9876"
    assert resp.model_used == "@cf/stabilityai/stable-diffusion-xl-base-1.0"
    assert resp.num_steps == 20
    assert resp.guidance == 7.5
    assert resp.seed == 42
    assert len(resp.images) == 1
    assert resp.images[0].width == 1024
    assert resp.images[0].height == 576
