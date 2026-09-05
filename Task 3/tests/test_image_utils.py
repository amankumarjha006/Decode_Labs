"""Unit tests for image processing, resolution mapping, and Pillow validation."""

import io
import pytest
from PIL import Image
from app.models import AspectRatio, ResolutionPreset
from app.services.image_storage_service import ImageStorageService
from app.utils.errors import ImageProcessingError, ValidationError
from app.utils.image_utils import (
    RESOLUTION_MAP,
    MIN_DIMENSION,
    MAX_DIMENSION,
    get_target_dimensions,
    validate_and_inspect_image,
    validate_dimensions,
)


def create_dummy_png_bytes(width: int = 100, height: int = 100, color: str = "red") -> bytes:
    """Helper to synthesize valid PNG image bytes in memory."""
    img = Image.new("RGB", (width, height), color=color)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def test_resolution_mappings_within_bounds():
    """Verify all aspect ratios map to valid dimensions within 256 and 2048 pixels."""
    for preset in (ResolutionPreset.STANDARD, ResolutionPreset.HIGH):
        for ratio in AspectRatio:
            w, h = get_target_dimensions(ratio, preset)
            assert MIN_DIMENSION <= w <= MAX_DIMENSION
            assert MIN_DIMENSION <= h <= MAX_DIMENSION
            # Test ratio orientation
            if ratio == AspectRatio.RATIO_1_1:
                assert w == h
            elif ratio in (AspectRatio.RATIO_16_9, AspectRatio.RATIO_4_3):
                assert w > h
            elif ratio in (AspectRatio.RATIO_9_16, AspectRatio.RATIO_3_4):
                assert h > w


def test_standard_preset_specific_dimensions():
    """Verify specific standard preset dimensions."""
    assert get_target_dimensions(AspectRatio.RATIO_1_1, ResolutionPreset.STANDARD) == (512, 512)
    assert get_target_dimensions(AspectRatio.RATIO_16_9, ResolutionPreset.STANDARD) == (768, 432)
    assert get_target_dimensions(AspectRatio.RATIO_9_16, ResolutionPreset.STANDARD) == (432, 768)
    assert get_target_dimensions(AspectRatio.RATIO_4_3, ResolutionPreset.STANDARD) == (640, 480)
    assert get_target_dimensions(AspectRatio.RATIO_3_4, ResolutionPreset.STANDARD) == (480, 640)


def test_high_preset_specific_dimensions():
    """Verify specific high preset dimensions."""
    assert get_target_dimensions(AspectRatio.RATIO_1_1, ResolutionPreset.HIGH) == (1024, 1024)
    assert get_target_dimensions(AspectRatio.RATIO_16_9, ResolutionPreset.HIGH) == (1024, 576)
    assert get_target_dimensions(AspectRatio.RATIO_9_16, ResolutionPreset.HIGH) == (576, 1024)
    assert get_target_dimensions(AspectRatio.RATIO_4_3, ResolutionPreset.HIGH) == (1024, 768)
    assert get_target_dimensions(AspectRatio.RATIO_3_4, ResolutionPreset.HIGH) == (768, 1024)


def test_image_validation_valid_bytes():
    """Requirement 15: Image validation - genuine image bytes decode successfully."""
    raw_bytes = create_dummy_png_bytes(width=256, height=256, color="blue")
    img, fmt, width, height = validate_and_inspect_image(raw_bytes)

    assert fmt == "PNG"
    assert width == 256
    assert height == 256
    assert isinstance(img, Image.Image)


def test_image_validation_corrupt_bytes_rejection():
    """Requirement 15: Image validation - corrupted or incomplete bytes are rejected."""
    with pytest.raises(ImageProcessingError):
        validate_and_inspect_image(b"not an image byte stream")

    with pytest.raises(ImageProcessingError):
        validate_and_inspect_image(b"")

    with pytest.raises(ImageProcessingError):
        validate_and_inspect_image(b"\x89PNG\r\n\x1a\ncorrupt_truncated_data")


def test_storage_service_save_and_metadata(tmp_path):
    """Verify ImageStorageService safely writes image files and preserves unique names."""
    images_dir = tmp_path / "images"
    metadata_dir = tmp_path / "meta"
    service = ImageStorageService(images_dir=images_dir, metadata_dir=metadata_dir)

    raw_bytes = create_dummy_png_bytes(width=512, height=512)
    item1 = service.save_image_bytes(raw_bytes, prefix="test1")
    item2 = service.save_image_bytes(raw_bytes, prefix="test2")

    assert item1.width == 512
    assert item1.height == 512
    assert item1.mime_type == "image/png"
    assert item1.file_name != item2.file_name
    assert (images_dir / item1.file_name).exists()
    assert (images_dir / item2.file_name).exists()
