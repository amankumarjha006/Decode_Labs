"""Service for validating, saving, and indexing generated images and generation metadata."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from app.config import config
from app.models import GeneratedImageItem, ImageGenerationResponse
from app.utils.errors import StorageError
from app.utils.image_utils import validate_and_inspect_image


class ImageStorageService:
    """Handles disk operations, PIL image validation, unique naming, and metadata storage."""

    def __init__(
        self,
        images_dir: Path | None = None,
        metadata_dir: Path | None = None,
    ):
        self.images_dir = images_dir or config.generated_images_dir
        self.metadata_dir = metadata_dir or config.metadata_dir
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create necessary directories if not already existing."""
        try:
            self.images_dir.mkdir(parents=True, exist_ok=True)
            self.metadata_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            raise StorageError(f"Failed to create storage directories: {exc}") from exc

    def save_image_bytes(
        self,
        image_bytes: bytes,
        prefix: str = "image",
    ) -> GeneratedImageItem:
        """Validate image bytes with Pillow and safely save to disk with a collision-free filename."""
        # 1. Validate image integrity and extract actual dimensions & format
        img, img_format, width, height = validate_and_inspect_image(image_bytes)

        # 2. Determine file extension
        ext = "jpg" if img_format in ("JPEG", "JPG") else "png"
        mime_type = "image/jpeg" if ext == "jpg" else "image/png"

        # 3. Create collision-proof filename: image_YYYYMMDD_HHMMSS_<unique_id>.<ext>
        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        file_name = f"{prefix}_{timestamp_str}_{unique_id}.{ext}"
        destination = self.images_dir / file_name

        # Prevent overwriting
        counter = 1
        while destination.exists():
            file_name = f"{prefix}_{timestamp_str}_{unique_id}_{counter}.{ext}"
            destination = self.images_dir / file_name
            counter += 1

        # 4. Save bytes safely
        try:
            with open(destination, "wb") as f:
                f.write(image_bytes)
        except Exception as exc:
            raise StorageError(f"Failed to write image file {file_name}: {exc}") from exc

        file_size = destination.stat().st_size

        return GeneratedImageItem(
            image_id=unique_id,
            local_path=str(destination.resolve()),
            file_name=file_name,
            mime_type=mime_type,
            width=width,
            height=height,
            file_size_bytes=file_size,
        )

    def save_generation_metadata(
        self,
        response: ImageGenerationResponse,
    ) -> Path:
        """Persist generation session metadata to JSON. API secrets are NEVER included."""
        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        meta_id = response.request_id[:8]
        meta_filename = f"generation_{timestamp_str}_{meta_id}.json"
        meta_file_path = self.metadata_dir / meta_filename

        metadata_dict: Dict[str, Any] = {
            "request_id": response.request_id,
            "created_at": response.created_at,
            "generation_time_seconds": response.generation_time_seconds,
            "model_used": response.model_used,
            "original_prompt": response.original_prompt,
            "enhanced_prompt": response.enhanced_prompt,
            "negative_prompt": response.negative_prompt,
            "style": response.style.value,
            "width": response.width,
            "height": response.height,
            "aspect_ratio": response.aspect_ratio.value,
            "resolution": response.resolution.value,
            "num_steps": response.num_steps,
            "guidance": response.guidance,
            "seed": response.seed,
            "generation_count": len(response.images),
            "warnings": response.warnings,
            "images": [img.model_dump() for img in response.images],
        }

        try:
            with open(meta_file_path, "w", encoding="utf-8") as f:
                json.dump(metadata_dict, f, indent=2)
            return meta_file_path
        except Exception as exc:
            raise StorageError(f"Failed to write metadata file {meta_filename}: {exc}") from exc

    def list_recent_metadata(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent generation records for sidebar history."""
        records: List[Dict[str, Any]] = []
        if not self.metadata_dir.exists():
            return records

        json_files = sorted(
            self.metadata_dir.glob("generation_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for json_path in json_files[:limit]:
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    records.append(data)
            except Exception:
                continue
        return records
