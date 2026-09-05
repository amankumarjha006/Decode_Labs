"""Domain models and Pydantic validation schemas for Image Generation Studio (Stable Diffusion XL)."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class ImageStyle(str, Enum):
    """Supported artistic styles for prompt enhancement."""

    NONE = "none"
    PHOTOREALISTIC = "photorealistic"
    DIGITAL_ART = "digital_art"
    ANIME = "anime"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"
    MINIMALIST = "minimalist"
    WATERCOLOR = "watercolor"
    OIL_PAINTING = "oil_painting"
    THREE_D_RENDER = "three_d_render"
    CINEMATIC = "cinematic"

    @property
    def display_name(self) -> str:
        """Formatted human-friendly name for UI dropdowns."""
        mapping = {
            ImageStyle.NONE: "None",
            ImageStyle.PHOTOREALISTIC: "Photorealistic",
            ImageStyle.DIGITAL_ART: "Digital Art",
            ImageStyle.ANIME: "Anime",
            ImageStyle.CYBERPUNK: "Cyberpunk",
            ImageStyle.FANTASY: "Fantasy",
            ImageStyle.MINIMALIST: "Minimalist",
            ImageStyle.WATERCOLOR: "Watercolor",
            ImageStyle.OIL_PAINTING: "Oil Painting",
            ImageStyle.THREE_D_RENDER: "3D Render",
            ImageStyle.CINEMATIC: "Cinematic",
        }
        return mapping.get(self, self.value.replace("_", " ").title())


class AspectRatio(str, Enum):
    """Supported image aspect ratios."""

    RATIO_1_1 = "1:1"
    RATIO_16_9 = "16:9"
    RATIO_9_16 = "9:16"
    RATIO_4_3 = "4:3"
    RATIO_3_4 = "3:4"

    @property
    def display_label(self) -> str:
        labels = {
            AspectRatio.RATIO_1_1: "1:1 (Square)",
            AspectRatio.RATIO_16_9: "16:9 (Landscape)",
            AspectRatio.RATIO_9_16: "9:16 (Portrait / Story)",
            AspectRatio.RATIO_4_3: "4:3 (Classic Landscape)",
            AspectRatio.RATIO_3_4: "3:4 (Classic Portrait)",
        }
        return labels.get(self, self.value)


class ResolutionPreset(str, Enum):
    """Quality and resolution presets."""

    STANDARD = "standard"
    HIGH = "high"

    @property
    def display_name(self) -> str:
        return "Standard" if self == ResolutionPreset.STANDARD else "High (1024px Max)"


class ImageGenerationRequest(BaseModel):
    """Validated image generation request payload for Stable Diffusion XL."""

    prompt: str = Field(
        ...,
        description="The primary natural-language description of the desired image.",
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        description="Optional elements to avoid in the generated image.",
    )
    style: ImageStyle = Field(
        default=ImageStyle.NONE,
        description="Artistic style preset to apply.",
    )
    aspect_ratio: AspectRatio = Field(
        default=AspectRatio.RATIO_1_1,
        description="Aspect ratio for image dimensions.",
    )
    resolution: ResolutionPreset = Field(
        default=ResolutionPreset.STANDARD,
        description="Standard or High resolution preset.",
    )
    generation_count: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of images to generate (1 to 4).",
    )
    seed: Optional[int] = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="Optional seed for deterministic generation.",
    )
    num_steps: int = Field(
        default=20,
        ge=1,
        le=20,
        description="Number of denoising steps (1 to 20 for Stable Diffusion XL).",
    )
    guidance: float = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        description="Guidance scale parameter (1.0 to 20.0 for Stable Diffusion XL).",
    )
    # Explicit pixel dimensions (optional, calculated from aspect_ratio & resolution if not provided)
    width: Optional[int] = Field(
        default=None,
        ge=256,
        le=2048,
        description="Optional explicit width in pixels (256 to 2048).",
    )
    height: Optional[int] = Field(
        default=None,
        ge=256,
        le=2048,
        description="Optional explicit height in pixels (256 to 2048).",
    )

    # Backwards compatibility parameters
    num_inference_steps: Optional[int] = Field(
        default=None,
        description="Deprecated alias for num_steps.",
    )
    guidance_scale: Optional[float] = Field(
        default=None,
        description="Deprecated alias for guidance.",
    )

    @model_validator(mode="before")
    @classmethod
    def reconcile_aliases(cls, data: any) -> any:
        if isinstance(data, dict):
            # If num_inference_steps was provided, map it to num_steps
            if "num_inference_steps" in data and data["num_inference_steps"] is not None:
                steps_val = data["num_inference_steps"]
                if not (1 <= steps_val <= 20):
                    raise ValueError(f"Number of steps must be between 1 and 20. Received: {steps_val}")
                data["num_steps"] = steps_val
            # If guidance_scale was provided, map it to guidance
            if "guidance_scale" in data and data["guidance_scale"] is not None:
                cfg_val = data["guidance_scale"]
                if not (1.0 <= cfg_val <= 20.0):
                    raise ValueError(f"Guidance scale must be between 1.0 and 20.0. Received: {cfg_val}")
                data["guidance"] = cfg_val
        return data

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Prompt must be a string")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Prompt cannot be empty or solely whitespace.")
        if len(cleaned) < 3:
            raise ValueError("Prompt must be at least 3 characters long.")
        if len(cleaned) > 2000:
            raise ValueError("Prompt cannot exceed 2000 characters.")
        return cleaned

    @field_validator("negative_prompt")
    @classmethod
    def clean_negative_prompt(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        return cleaned if cleaned else None

    @field_validator("num_steps")
    @classmethod
    def validate_steps(cls, v: int) -> int:
        if not (1 <= v <= 20):
            raise ValueError("num_steps must be between 1 and 20.")
        return v

    @field_validator("guidance")
    @classmethod
    def validate_guidance_value(cls, v: float) -> float:
        if not (1.0 <= v <= 20.0):
            raise ValueError("guidance must be between 1.0 and 20.0.")
        return float(v)

    @field_validator("width", "height")
    @classmethod
    def validate_dimensions_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (256 <= v <= 2048):
            raise ValueError(f"Dimension {v} must be between 256 and 2048 pixels.")
        return v


class GeneratedImageItem(BaseModel):
    """Metadata describing a saved image artifact."""

    image_id: str
    local_path: str
    file_name: str
    mime_type: str = "image/png"
    width: int
    height: int
    file_size_bytes: int


class ImageGenerationResponse(BaseModel):
    """Structured response containing all generated assets and execution telemetry."""

    request_id: str
    original_prompt: str
    enhanced_prompt: str
    negative_prompt: Optional[str] = None
    style: ImageStyle
    aspect_ratio: AspectRatio
    resolution: ResolutionPreset
    width: int = 512
    height: int = 512
    num_steps: int = 20
    guidance: float = 7.5
    seed: Optional[int] = None
    model_used: str = "@cf/stabilityai/stable-diffusion-xl-base-1.0"
    images: List[GeneratedImageItem] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    generation_time_seconds: float
    warnings: List[str] = Field(default_factory=list)
    debug_info: Optional[dict] = None
