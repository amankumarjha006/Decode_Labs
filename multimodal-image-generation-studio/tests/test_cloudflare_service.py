"""Unit tests for CloudflareWorkersAIService with Stable Diffusion XL using mocked HTTP responses."""

import base64
import io
import pytest
from PIL import Image
import httpx
from app.config import AppConfig
from app.models import (
    AspectRatio,
    ImageGenerationRequest,
    ImageStyle,
    ResolutionPreset,
)
from app.services.cloudflare_service import (
    CloudflareWorkersAIService,
    build_provider_payload,
)
from app.services.image_storage_service import ImageStorageService
from app.utils.errors import (
    AuthenticationError,
    CloudflareAPIError,
    ConfigurationError,
    RateLimitError,
    ValidationError,
)


def create_dummy_png_bytes(width: int = 512, height: int = 512) -> bytes:
    img = Image.new("RGB", (width, height), color="purple")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_valid_sdxl_payload():
    """Requirement 1: Test valid Stable Diffusion XL payload construction."""
    payload = build_provider_payload(
        prompt="Cyberpunk drone",
        width=1024,
        height=576,
        num_steps=20,
        guidance=7.5,
        negative_prompt="blurry, distorted",
        seed=999,
    )
    assert payload["prompt"] == "Cyberpunk drone"
    assert payload["width"] == 1024
    assert payload["height"] == 576
    assert payload["num_steps"] == 20
    assert payload["guidance"] == 7.5
    assert payload["negative_prompt"] == "blurry, distorted"
    assert payload["seed"] == 999


def test_negative_prompt_omitted_when_empty():
    """Requirement 2: Negative prompt omitted when empty or None."""
    payload1 = build_provider_payload(
        prompt="A landscape",
        width=512,
        height=512,
        negative_prompt="",
    )
    assert "negative_prompt" not in payload1

    payload2 = build_provider_payload(
        prompt="A landscape",
        width=512,
        height=512,
        negative_prompt="   ",
    )
    assert "negative_prompt" not in payload2

    payload3 = build_provider_payload(
        prompt="A landscape",
        width=512,
        height=512,
        negative_prompt=None,
    )
    assert "negative_prompt" not in payload3


def test_seed_omitted_when_none():
    """Requirement 3: Seed omitted when None."""
    payload = build_provider_payload(
        prompt="A forest",
        width=512,
        height=512,
        seed=None,
    )
    assert "seed" not in payload


def test_payload_builder_rejects_invalid_dimensions():
    """Verify payload builder enforces dimension limits."""
    with pytest.raises(ValidationError):
        build_provider_payload(prompt="Test", width=100, height=512)
    with pytest.raises(ValidationError):
        build_provider_payload(prompt="Test", width=512, height=3000)


def test_unconfigured_credentials_raises_configuration_error(tmp_path):
    """Test that missing credentials throw ConfigurationError."""
    dummy_config = AppConfig(
        cloudflare_account_id="",
        cloudflare_api_token="",
        output_directory=tmp_path,
        generated_images_dir=tmp_path / "images",
        metadata_dir=tmp_path / "meta",
    )
    service = CloudflareWorkersAIService(app_config=dummy_config)
    with pytest.raises(ConfigurationError):
        service.validate_credentials()


@pytest.mark.asyncio
async def test_mocked_binary_image_generation(monkeypatch, tmp_path):
    """Requirement 16: Test successful image response handling with binary PNG."""
    test_bytes = create_dummy_png_bytes(512, 512)

    mock_response = httpx.Response(
        status_code=200,
        content=test_bytes,
        headers={"Content-Type": "image/png"},
        request=httpx.Request("POST", "https://api.cloudflare.com"),
    )

    async def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    test_config = AppConfig(
        cloudflare_account_id="test_acc_id_12345",
        cloudflare_api_token="test_token_67890",
        cloudflare_model="@cf/stabilityai/stable-diffusion-xl-base-1.0",
        output_directory=tmp_path,
        generated_images_dir=tmp_path / "images",
        metadata_dir=tmp_path / "meta",
    )
    storage = ImageStorageService(
        images_dir=tmp_path / "images",
        metadata_dir=tmp_path / "meta",
    )
    service = CloudflareWorkersAIService(app_config=test_config, storage_service=storage)

    req = ImageGenerationRequest(
        prompt="A mystical portal",
        negative_prompt="blurry",
        style=ImageStyle.FANTASY,
        aspect_ratio=AspectRatio.RATIO_1_1,
        resolution=ResolutionPreset.STANDARD,
        width=512,
        height=512,
        generation_count=1,
        num_steps=20,
        guidance=7.5,
    )

    response = await service.generate(req)
    assert response.request_id is not None
    assert response.model_used == "@cf/stabilityai/stable-diffusion-xl-base-1.0"
    assert len(response.images) == 1
    assert response.images[0].width == 512
    assert response.images[0].height == 512
    assert response.num_steps == 20
    assert response.guidance == 7.5
    assert response.negative_prompt == "blurry"


@pytest.mark.asyncio
async def test_mocked_json_base64_generation(monkeypatch, tmp_path):
    """Requirement 16: Test generation flow with mocked JSON base64 result payload."""
    test_bytes = create_dummy_png_bytes(512, 512)
    b64_str = base64.b64encode(test_bytes).decode("utf-8")

    mock_response = httpx.Response(
        status_code=200,
        json={"result": {"image": b64_str}, "success": True},
        headers={"Content-Type": "application/json"},
        request=httpx.Request("POST", "https://api.cloudflare.com"),
    )

    async def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    test_config = AppConfig(
        cloudflare_account_id="test_acc_id_12345",
        cloudflare_api_token="test_token_67890",
        cloudflare_model="@cf/stabilityai/stable-diffusion-xl-base-1.0",
        output_directory=tmp_path,
        generated_images_dir=tmp_path / "images",
        metadata_dir=tmp_path / "meta",
    )
    storage = ImageStorageService(
        images_dir=tmp_path / "images",
        metadata_dir=tmp_path / "meta",
    )
    service = CloudflareWorkersAIService(app_config=test_config, storage_service=storage)

    req = ImageGenerationRequest(
        prompt="Minimalist chair",
        style=ImageStyle.MINIMALIST,
        aspect_ratio=AspectRatio.RATIO_1_1,
        resolution=ResolutionPreset.STANDARD,
        width=512,
        height=512,
        generation_count=1,
    )

    response = await service.generate(req)
    assert len(response.images) == 1
    assert response.images[0].width == 512


@pytest.mark.asyncio
async def test_error_response_parsing_400(monkeypatch, tmp_path):
    """Requirement 13: Detailed error response parsing for HTTP 400."""
    error_payload = {
        "success": False,
        "errors": [{"code": 1001, "message": "Invalid parameter: num_steps must be less than or equal to 20."}],
    }
    mock_response = httpx.Response(
        status_code=400,
        json=error_payload,
        request=httpx.Request("POST", "https://api.cloudflare.com"),
    )

    async def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    test_config = AppConfig(
        cloudflare_account_id="test_acc",
        cloudflare_api_token="test_tok",
        output_directory=tmp_path,
        generated_images_dir=tmp_path / "images",
        metadata_dir=tmp_path / "meta",
    )
    service = CloudflareWorkersAIService(app_config=test_config)

    with pytest.raises(CloudflareAPIError) as exc_info:
        await service.generate_single("test prompt", 512, 512)

    err = exc_info.value
    assert err.status_code == 400
    assert err.error_code == "1001"
    assert "Invalid parameter: num_steps must be less than or equal to 20." in err.user_friendly_message


@pytest.mark.asyncio
async def test_error_response_parsing_401(monkeypatch, tmp_path):
    """Test HTTP 401 authentication error parsing."""
    mock_response = httpx.Response(
        status_code=401,
        json={"success": False, "errors": [{"message": "Invalid credentials"}]},
        request=httpx.Request("POST", "https://api.cloudflare.com"),
    )

    async def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    test_config = AppConfig(
        cloudflare_account_id="test_acc",
        cloudflare_api_token="test_tok",
        output_directory=tmp_path,
        generated_images_dir=tmp_path / "images",
        metadata_dir=tmp_path / "meta",
    )
    service = CloudflareWorkersAIService(app_config=test_config)

    with pytest.raises(AuthenticationError) as exc_info:
        await service.generate_single("test prompt", 512, 512)

    assert exc_info.value.status_code == 401
    assert "Authentication failed" in exc_info.value.user_friendly_message


@pytest.mark.asyncio
async def test_error_response_parsing_404(monkeypatch, tmp_path):
    """Test HTTP 404 model not found error parsing displays model name."""
    mock_response = httpx.Response(
        status_code=404,
        json={"success": False, "errors": [{"message": "Model not found"}]},
        request=httpx.Request("POST", "https://api.cloudflare.com"),
    )

    async def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    test_config = AppConfig(
        cloudflare_account_id="test_acc",
        cloudflare_api_token="test_tok",
        cloudflare_model="@cf/stabilityai/stable-diffusion-xl-base-1.0",
        output_directory=tmp_path,
        generated_images_dir=tmp_path / "images",
        metadata_dir=tmp_path / "meta",
    )
    service = CloudflareWorkersAIService(app_config=test_config)

    with pytest.raises(CloudflareAPIError) as exc_info:
        await service.generate_single("test prompt", 512, 512)

    assert exc_info.value.status_code == 404
    assert "@cf/stabilityai/stable-diffusion-xl-base-1.0" in exc_info.value.user_friendly_message


@pytest.mark.asyncio
async def test_error_response_429_daily_allocation_exhausted(monkeypatch, tmp_path):
    """Test HTTP 429 quota exhaustion differentiates from temporary rate limits."""
    mock_response = httpx.Response(
        status_code=429,
        json={"success": False, "errors": [{"message": "Daily free neuron quota allocation exhausted"}]},
        request=httpx.Request("POST", "https://api.cloudflare.com"),
    )

    async def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    test_config = AppConfig(
        cloudflare_account_id="test_acc",
        cloudflare_api_token="test_tok",
        output_directory=tmp_path,
        generated_images_dir=tmp_path / "images",
        metadata_dir=tmp_path / "meta",
    )
    service = CloudflareWorkersAIService(app_config=test_config)

    with pytest.raises(RateLimitError) as exc_info:
        await service.generate_single("test prompt", 512, 512)

    err = exc_info.value
    assert err.status_code == 429
    assert err.is_daily_allocation_exhausted is True
    assert "Daily Cloudflare Workers AI free allocation has been exhausted" in err.user_friendly_message
