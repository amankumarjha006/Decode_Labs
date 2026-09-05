"""Provider abstractions and orchestrator interface for text-to-image generation."""

from abc import ABC, abstractmethod
from typing import Optional
from app.models import ImageGenerationRequest, ImageGenerationResponse


class ImageGenerationProvider(ABC):
    """Abstract base class establishing the contract for image generation backends."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the generation provider."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier of the active model."""
        pass

    @abstractmethod
    async def generate_single(
        self,
        prompt: str,
        width: int,
        height: int,
        seed: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        negative_prompt: Optional[str] = None,
    ) -> bytes:
        """Generate a single image returning raw image bytes."""
        pass

    @abstractmethod
    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Handle full end-to-end request lifecycle with prompt enhancement and storage."""
        pass
