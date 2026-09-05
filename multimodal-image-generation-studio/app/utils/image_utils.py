"""Image utilities for resolution mapping, dimension calculation, and PIL verification."""

import io
from typing import Dict, Tuple
from PIL import Image
from app.models import AspectRatio, ResolutionPreset
from app.utils.errors import ImageProcessingError, ValidationError

# Dimension limits supported by Stable Diffusion XL
MIN_DIMENSION = 256
MAX_DIMENSION = 2048

# Centralized resolution presets: (width, height)
# Updated to match Stable Diffusion XL optimal specifications
RESOLUTION_MAP: Dict[ResolutionPreset, Dict[AspectRatio, Tuple[int, int]]] = {
    ResolutionPreset.STANDARD: {
        AspectRatio.RATIO_1_1: (512, 512),
        AspectRatio.RATIO_16_9: (768, 432),
        AspectRatio.RATIO_9_16: (432, 768),
        AspectRatio.RATIO_4_3: (640, 480),
        AspectRatio.RATIO_3_4: (480, 640),
    },
    ResolutionPreset.HIGH: {
        AspectRatio.RATIO_1_1: (1024, 1024),
        AspectRatio.RATIO_16_9: (1024, 576),
        AspectRatio.RATIO_9_16: (576, 1024),
        AspectRatio.RATIO_4_3: (1024, 768),
        AspectRatio.RATIO_3_4: (768, 1024),
    },
}


def validate_dimensions(width: int, height: int) -> Tuple[int, int]:
    """Validate image dimensions before calling the API.

    Must satisfy:
        256 <= width <= 2048
        256 <= height <= 2048

    Raises:
        ValidationError with requested dimensions and allowed range if invalid.
    """
    if not (MIN_DIMENSION <= width <= MAX_DIMENSION and MIN_DIMENSION <= height <= MAX_DIMENSION):
        raise ValidationError(
            f"Invalid image dimensions: {width} × {height}. "
            f"Width and height must be between {MIN_DIMENSION} and {MAX_DIMENSION} pixels.",
            user_friendly_message=(
                f"Invalid image dimensions: {width} × {height}. "
                f"Width and height must be between {MIN_DIMENSION} and {MAX_DIMENSION} pixels."
            ),
        )
    return width, height


def get_target_dimensions(
    aspect_ratio: AspectRatio, resolution: ResolutionPreset = ResolutionPreset.STANDARD
) -> Tuple[int, int]:
    """Retrieve optimal pixel dimensions for specified aspect ratio and resolution preset."""
    res_dict = RESOLUTION_MAP.get(resolution, RESOLUTION_MAP[ResolutionPreset.STANDARD])
    w, h = res_dict.get(aspect_ratio, (1024, 1024))
    validate_dimensions(w, h)
    return w, h


def validate_and_inspect_image(image_bytes: bytes) -> Tuple[Image.Image, str, int, int]:
    """Validate that raw bytes represent a genuine, uncorrupted image.

    Checks:
        - Image can be opened by Pillow
        - Image format is valid (e.g., PNG, JPEG, WEBP)
        - Image dimensions are valid (> 0)

    Returns:
        Tuple containing (PIL Image instance, format string (e.g., 'PNG'), width, height).

    Raises:
        ImageProcessingError: If data is empty, invalid, or corrupted.
    """
    if not image_bytes or len(image_bytes) < 16:
        raise ImageProcessingError("Received empty or incomplete image byte stream.")

    try:
        buffer = io.BytesIO(image_bytes)
        img = Image.open(buffer)
        # Verify file integrity
        img.verify()

        # Reopen after verify() because verify() clears the image state
        buffer.seek(0)
        img = Image.open(buffer)
        img_format = (img.format or "PNG").upper()
        width, height = img.size

        if width <= 0 or height <= 0:
            raise ImageProcessingError(f"Image has invalid dimensions: {width}x{height}")

        # Validate format is recognized image
        valid_formats = ("PNG", "JPEG", "JPG", "WEBP")
        if img_format not in valid_formats:
            raise ImageProcessingError(f"Unsupported image format: {img_format}. Expected one of {valid_formats}")

        return img, img_format, width, height
    except Exception as exc:
        if isinstance(exc, ImageProcessingError):
            raise
        raise ImageProcessingError(f"Corrupted or unrecognized image data: {str(exc)}") from exc
