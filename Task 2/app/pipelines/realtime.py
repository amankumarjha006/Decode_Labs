"""Real-time asynchronous copywriting pipeline with semaphore concurrency control."""

import asyncio
from typing import List, Optional
from app.config import DEFAULT_CONCURRENCY
from app.models import GenerationRequest, GenerationResponse
from app.services.generator import CopyGenerator


class RealtimePipeline:
    """Handles real-time asynchronous marketing copy requests with concurrency limiting."""

    def __init__(
        self,
        generator: Optional[CopyGenerator] = None,
        concurrency_limit: int = DEFAULT_CONCURRENCY,
    ):
        self.generator = generator or CopyGenerator()
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def generate_single(self, request: GenerationRequest) -> GenerationResponse:
        """Process a single generation request under concurrency semaphore protection.
        
        Args:
            request: Validated GenerationRequest.
            
        Returns:
            GenerationResponse with copy and execution statistics.
        """
        async with self.semaphore:
            return await self.generator.generate_copy(request)

    async def generate_batch(self, requests: List[GenerationRequest]) -> List[GenerationResponse]:
        """Process a list of generation requests concurrently up to the semaphore limit.
        
        Args:
            requests: List of validated GenerationRequest instances.
            
        Returns:
            List of generated responses in the same order.
        """
        async def _bounded_task(req: GenerationRequest) -> GenerationResponse:
            async with self.semaphore:
                return await self.generator.generate_copy(req)

        tasks = [_bounded_task(req) for req in requests]
        return await asyncio.gather(*tasks)
