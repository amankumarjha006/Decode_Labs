"""Cloudflare Workers AI provider implementation for Stable Diffusion XL image generation."""

import asyncio
import base64
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
import httpx

from app.config import AppConfig, config
from app.models import (
    GeneratedImageItem,
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from app.prompts.prompt_builder import build_enhanced_prompt
from app.services.image_generation_service import ImageGenerationProvider
from app.services.image_storage_service import ImageStorageService
from app.utils.errors import (
    AuthenticationError,
    CloudflareAPIError,
    ConfigurationError,
    ImageProcessingError,
    ModelError,
    NetworkError,
    RateLimitError,
    StudioError,
    TimeoutError,
    ValidationError,
    sanitize_debug_data,
)
from app.utils.image_utils import get_target_dimensions, validate_dimensions
from app.utils.retry import retry_with_exponential_backoff
from app.utils.validation import (
    sanitize_prompt,
    validate_dimensions as validate_dim_inputs,
    validate_guidance,
    validate_num_steps,
    validate_seed,
)

logger = logging.getLogger(__name__)


def build_provider_payload(
    prompt: str,
    width: int,
    height: int,
    num_steps: int = 20,
    guidance: float = 7.5,
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    model: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Centralized payload builder for Stable Diffusion XL on Cloudflare Workers AI.

    Supported parameters:
        prompt, negative_prompt, width, height, num_steps, guidance, seed.
    Does NOT send None values or empty strings.
    """
    # Reconcile alias parameters if provided in kwargs
    if "num_inference_steps" in kwargs and kwargs["num_inference_steps"] is not None:
        num_steps = kwargs["num_inference_steps"]
    if "steps" in kwargs and kwargs["steps"] is not None:
        num_steps = kwargs["steps"]
    if "guidance_scale" in kwargs and kwargs["guidance_scale"] is not None:
        guidance = kwargs["guidance_scale"]

    # Validate dimensions and steps before constructing payload
    validate_dimensions(width, height)

    payload: Dict[str, Any] = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_steps": num_steps,
        "guidance": guidance,
    }

    # Only add negative_prompt when user entered a non-empty string
    if negative_prompt and isinstance(negative_prompt, str) and negative_prompt.strip():
        payload["negative_prompt"] = negative_prompt.strip()

    # Only add seed when supplied
    if seed is not None:
        payload["seed"] = seed

    return payload


class CloudflareWorkersAIService(ImageGenerationProvider):
    """Client for Cloudflare Workers AI REST API generating images via Stable Diffusion XL."""

    def __init__(
        self,
        app_config: Optional[AppConfig] = None,
        storage_service: Optional[ImageStorageService] = None,
    ):
        self.config = app_config or config
        self.storage = storage_service or ImageStorageService()

    @property
    def provider_name(self) -> str:
        return "Cloudflare Workers AI"

    @property
    def model_name(self) -> str:
        return self.config.cloudflare_model

    def validate_credentials(self) -> None:
        """Ensure account ID and API token are provided and not placeholders."""
        if not self.config.is_cloudflare_configured():
            missing: List[str] = []
            if (
                not self.config.cloudflare_account_id
                or self.config.cloudflare_account_id == "your_cloudflare_account_id"
            ):
                missing.append("CLOUDFLARE_ACCOUNT_ID")
            if (
                not self.config.cloudflare_api_token
                or self.config.cloudflare_api_token == "your_cloudflare_api_token"
            ):
                missing.append("CLOUDFLARE_API_TOKEN")

            raise ConfigurationError(
                f"Missing required Cloudflare credentials: {', '.join(missing)}. "
                "Please configure your .env file or environment variables.",
                user_friendly_message=(
                    "Cloudflare credentials not configured. Please set "
                    "CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in your .env file."
                ),
            )

    def get_endpoint_url(self) -> str:
        """Construct endpoint URL dynamically from configuration without exposing secrets."""
        account_id = self.config.cloudflare_account_id
        model = self.config.cloudflare_model
        return f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"

    def get_safe_endpoint_url(self) -> str:
        """Construct a safe endpoint URL with masked account ID for debug display."""
        masked_acc = self.config.get_masked_account_id()
        model = self.config.cloudflare_model
        return f"https://api.cloudflare.com/client/v4/accounts/{masked_acc}/ai/run/{model}"

    async def _execute_http_request(
        self, payload: Dict[str, Any], request_index: int = 1
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Send HTTP POST request to Cloudflare Workers AI with comprehensive error handling."""
        self.validate_credentials()
        endpoint = self.get_endpoint_url()

        # Log safe debugging info
        logger.info("Starting image generation [request #%d]", request_index)
        logger.info("Model: %s", self.config.cloudflare_model)
        logger.info("Dimensions: %dx%d", payload.get("width"), payload.get("height"))
        logger.info("Steps: %s", payload.get("num_steps"))
        logger.info("Guidance: %s", payload.get("guidance"))
        logger.info("Negative prompt supplied: %s", "negative_prompt" in payload)
        logger.info("Seed supplied: %s", "seed" in payload)

        headers = {
            "Authorization": f"Bearer {self.config.cloudflare_api_token}",
            "Content-Type": "application/json",
            "Accept": "image/png, image/jpeg, application/json",
        }

        req_start = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                )
        except httpx.TimeoutException as exc:
            logger.error("Request timed out after %.1fs", self.config.request_timeout)
            raise TimeoutError(
                f"Request timed out after {self.config.request_timeout}s.",
                user_friendly_message=(
                    "The image generation request timed out. "
                    "Try reducing the image resolution or retrying the request."
                ),
            ) from exc
        except (httpx.ConnectError, httpx.NetworkError) as exc:
            logger.error("Network error connecting to Cloudflare Workers AI: %s", exc)
            raise NetworkError(
                f"Network connectivity error: {str(exc)}",
                user_friendly_message=(
                    "Unable to connect to Cloudflare Workers AI. "
                    "Please check your internet connection and try again."
                ),
            ) from exc

        req_duration = round(time.time() - req_start, 2)
        content_type = response.headers.get("Content-Type", "").lower()
        status_code = response.status_code

        logger.info("HTTP response status: %d", status_code)
        logger.info("Response content type: %s", content_type)
        logger.info("Generation duration: %.2fs", req_duration)

        # Parse error responses if not 200 OK
        if status_code != 200:
            error_code: Optional[str] = None
            error_message: Optional[str] = None
            raw_body = response.text[:2000]

            try:
                error_json = response.json()
                if isinstance(error_json, dict):
                    errors = error_json.get("errors", [])
                    if errors and isinstance(errors, list):
                        first_err = errors[0]
                        if isinstance(first_err, dict):
                            error_code = str(first_err.get("code", ""))
                            error_message = first_err.get("message")
                        elif isinstance(first_err, str):
                            error_message = first_err
                    elif "error" in error_json:
                        error_message = str(error_json["error"])
            except Exception:
                error_json = {"raw_response": raw_body}

            debug_meta = {
                "status_code": status_code,
                "content_type": content_type,
                "duration_seconds": req_duration,
                "error_code": error_code,
                "error_message": error_message,
                "raw_response": raw_body[:500],
            }

            # Differentiate HTTP status codes
            if status_code == 400:
                detail = f": {error_message}" if error_message else "."
                friendly = (
                    f"Cloudflare API Error (400): {error_message}"
                    if error_message
                    else "Invalid image generation request. Please check the selected dimensions and generation settings."
                )
                logger.error("HTTP 400 Bad Request: %s", error_message or raw_body)
                raise CloudflareAPIError(
                    message=f"Invalid image generation request{detail}",
                    status_code=400,
                    error_code=error_code,
                    response_body=raw_body,
                    user_friendly_message=friendly,
                )

            if status_code == 401:
                logger.error("HTTP 401 Authentication Failed")
                raise AuthenticationError(
                    message="Authentication failed with Cloudflare Workers AI (HTTP 401).",
                    status_code=401,
                    error_code=error_code,
                    response_body=raw_body,
                    user_friendly_message="Authentication failed. Please check your Cloudflare API token.",
                )

            if status_code == 403:
                logger.error("HTTP 403 Access Denied")
                raise AuthenticationError(
                    message="Access to Cloudflare Workers AI was denied (HTTP 403).",
                    status_code=403,
                    error_code=error_code,
                    response_body=raw_body,
                    user_friendly_message=(
                        "Access to Cloudflare Workers AI was denied. "
                        "Check your API token permissions and Cloudflare account access."
                    ),
                )

            if status_code == 404:
                logger.error("HTTP 404 Model/Endpoint not found")
                raise CloudflareAPIError(
                    message=f"The requested Cloudflare model '{self.config.cloudflare_model}' could not be found.",
                    status_code=404,
                    error_code=error_code,
                    response_body=raw_body,
                    user_friendly_message=(
                        "The requested Cloudflare model or API endpoint could not be found.\n\n"
                        f"Current Model: {self.config.cloudflare_model}"
                    ),
                )

            if status_code == 408:
                logger.error("HTTP 408 Request Timeout")
                raise CloudflareAPIError(
                    message="The image generation request timed out (HTTP 408).",
                    status_code=408,
                    error_code=error_code,
                    response_body=raw_body,
                    user_friendly_message="The image generation request timed out. Try reducing the image resolution or retrying the request.",
                )

            if status_code == 413:
                logger.error("HTTP 413 Request Entity Too Large")
                raise CloudflareAPIError(
                    message="The request was too large (HTTP 413).",
                    status_code=413,
                    error_code=error_code,
                    response_body=raw_body,
                    user_friendly_message="The request was too large. Try reducing the image size or prompt complexity.",
                )

            if status_code == 429:
                body_lower = (raw_body + " " + (error_message or "")).lower()
                is_daily_exhausted = any(
                    k in body_lower for k in ("daily", "exhausted", "quota", "neuron", "allocation")
                )

                if is_daily_exhausted:
                    logger.warning("HTTP 429 Daily Free Allocation Exhausted")
                    friendly = (
                        "Daily Cloudflare Workers AI free allocation has been exhausted. "
                        "The free allocation resets at 00:00 UTC."
                    )
                else:
                    logger.warning("HTTP 429 Rate Limit Hit")
                    friendly = "Cloudflare is currently rate limiting requests. Please wait a moment and try again."

                raise RateLimitError(
                    message=f"Cloudflare rate limit encountered (HTTP 429): {error_message or raw_body}",
                    status_code=429,
                    error_code=error_code,
                    response_body=raw_body,
                    is_daily_allocation_exhausted=is_daily_exhausted,
                    user_friendly_message=friendly,
                )

            if 500 <= status_code <= 599:
                logger.error("HTTP %d Cloudflare Server Error: %s", status_code, raw_body[:200])
                raise CloudflareAPIError(
                    message=f"Cloudflare server error (HTTP {status_code}): {error_message or raw_body}",
                    status_code=status_code,
                    error_code=error_code,
                    response_body=raw_body,
                    user_friendly_message="Cloudflare Workers AI temporarily failed to generate the image. Please try again shortly.",
                )

            # Any other unexpected status code
            raise CloudflareAPIError(
                message=f"Unexpected response from Cloudflare (HTTP {status_code}): {raw_body[:200]}",
                status_code=status_code,
                error_code=error_code,
                response_body=raw_body,
                user_friendly_message=f"Cloudflare API error (HTTP {status_code}). Please try again.",
            )

        # 200 OK: Parse binary image or base64 JSON payload
        image_bytes: Optional[bytes] = None

        if "image/" in content_type:
            image_bytes = response.content
        else:
            try:
                json_data = response.json()
            except Exception:
                if response.content.startswith(b"\x89PNG") or response.content.startswith(b"\xff\xd8"):
                    image_bytes = response.content
                else:
                    raise ImageProcessingError("Failed to decode response as JSON or binary image.")

            if image_bytes is None and isinstance(json_data, dict):
                if json_data.get("success") is False:
                    errors = json_data.get("errors", [])
                    err_msg = "; ".join(e.get("message", "Unknown error") for e in errors)
                    raise CloudflareAPIError(
                        message=f"Cloudflare model error: {err_msg}",
                        status_code=200,
                        user_friendly_message=f"Model generation error: {err_msg}",
                    )

                image_b64: Optional[str] = None
                if "result" in json_data and isinstance(json_data["result"], dict):
                    image_b64 = json_data["result"].get("image")
                elif "image" in json_data:
                    image_b64 = json_data.get("image")

                if image_b64:
                    try:
                        image_bytes = base64.b64decode(image_b64)
                    except Exception as exc:
                        raise ImageProcessingError(f"Failed to decode base64 image data: {exc}") from exc

            if image_bytes is None and (
                response.content.startswith(b"\x89PNG") or response.content.startswith(b"\xff\xd8")
            ):
                image_bytes = response.content

        if not image_bytes or len(image_bytes) < 16:
            raise ImageProcessingError("Response did not contain valid binary image data or base64 image payload.")

        byte_size = len(image_bytes)
        logger.info("Image byte size: %d bytes (%.1f KB)", byte_size, byte_size / 1024)

        debug_info = {
            "status_code": status_code,
            "content_type": content_type,
            "duration_seconds": req_duration,
            "byte_size": byte_size,
        }

        return image_bytes, debug_info

    async def generate_single(
        self,
        prompt: str,
        width: int,
        height: int,
        num_steps: int = 20,
        guidance: float = 7.5,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        request_index: int = 1,
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Generate a single image with exponential backoff retry."""
        # Pre-validation
        validate_dimensions(width, height)
        validate_num_steps(num_steps)
        validate_guidance(guidance)
        validate_seed(seed)
        clean_prompt = sanitize_prompt(prompt)

        payload = build_provider_payload(
            prompt=clean_prompt,
            width=width,
            height=height,
            num_steps=num_steps,
            guidance=guidance,
            negative_prompt=negative_prompt,
            seed=seed,
            model=self.config.cloudflare_model,
        )

        async def _call() -> Tuple[bytes, Dict[str, Any]]:
            return await self._execute_http_request(payload, request_index=request_index)

        return await retry_with_exponential_backoff(
            coro_fn=_call,
            max_retries=self.config.max_retries,
            retryable_exceptions=(RateLimitError, TimeoutError, NetworkError, CloudflareAPIError),
        )

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Handle multi-image generation with semaphore concurrency and result persistence."""
        start_time = time.time()
        request_id = uuid.uuid4().hex

        # 1. Enhance prompt with style modifiers
        enhancement = build_enhanced_prompt(request.prompt, request.style)
        effective_prompt = enhancement.enhanced_prompt

        # 2. Determine target dimensions
        if request.width and request.height:
            target_width, target_height = request.width, request.height
            validate_dimensions(target_width, target_height)
        else:
            target_width, target_height = get_target_dimensions(
                request.aspect_ratio, request.resolution
            )

        # 3. Parameters
        num_steps = request.num_steps
        guidance = request.guidance
        negative_prompt = request.negative_prompt

        warnings: List[str] = []

        # 4. Safe concurrency management (Maximum simultaneous generation requests: 2)
        semaphore = asyncio.Semaphore(self.config.max_concurrent_generations)
        saved_images: List[GeneratedImageItem] = []
        generation_errors: List[str] = []
        all_debug_items: List[Dict[str, Any]] = []

        async def _generate_task(index: int) -> Optional[GeneratedImageItem]:
            async with semaphore:
                item_seed: Optional[int] = None
                if request.seed is not None:
                    item_seed = (request.seed + (index * 7919)) % 2147483647

                try:
                    img_bytes, debug_data = await self.generate_single(
                        prompt=effective_prompt,
                        width=target_width,
                        height=target_height,
                        num_steps=num_steps,
                        guidance=guidance,
                        negative_prompt=negative_prompt,
                        seed=item_seed,
                        request_index=index + 1,
                    )
                    all_debug_items.append(debug_data)
                    item = self.storage.save_image_bytes(img_bytes, prefix=f"img_{index+1}")
                    return item
                except Exception as exc:
                    err_msg = getattr(exc, "user_friendly_message", str(exc))
                    logger.error("Generation error for image #%d: %s", index + 1, exc)
                    generation_errors.append(f"Image #{index+1} failed: {err_msg}")
                    return None

        tasks = [_generate_task(i) for i in range(request.generation_count)]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        for res in results:
            if res is not None:
                saved_images.append(res)

        # If all generations failed, raise error
        if not saved_images:
            combined_err = " | ".join(generation_errors) if generation_errors else "Generation failed."
            raise StudioError(
                f"All image generation attempts failed: {combined_err}",
                user_friendly_message=f"Generation failed: {combined_err}",
            )

        # If partial failure, append to warnings
        if generation_errors:
            warnings.extend(generation_errors)

        duration = round(time.time() - start_time, 2)

        # Build safe debug info dictionary
        safe_debug_info = sanitize_debug_data({
            "request_id": request_id,
            "model": self.config.cloudflare_model,
            "endpoint": self.get_safe_endpoint_url(),
            "safe_payload": {
                "prompt": effective_prompt,
                "width": target_width,
                "height": target_height,
                "num_steps": num_steps,
                "guidance": guidance,
                "negative_prompt": negative_prompt,
                "seed": request.seed,
            },
            "total_images_requested": request.generation_count,
            "successful_images": len(saved_images),
            "generation_time_seconds": duration,
            "telemetry": all_debug_items,
        })

        response = ImageGenerationResponse(
            request_id=request_id,
            original_prompt=request.prompt,
            enhanced_prompt=effective_prompt,
            negative_prompt=negative_prompt,
            style=request.style,
            aspect_ratio=request.aspect_ratio,
            resolution=request.resolution,
            width=target_width,
            height=target_height,
            num_steps=num_steps,
            guidance=guidance,
            seed=request.seed,
            model_used=self.config.cloudflare_model,
            images=saved_images,
            generation_time_seconds=duration,
            warnings=warnings,
            debug_info=safe_debug_info,
        )

        # Persist generation metadata
        self.storage.save_generation_metadata(response)

        return response
