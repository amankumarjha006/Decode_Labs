"""High-level copy generation service coordinating prompts, LLM inference, and validation."""

import logging
from typing import Optional
from app.models import GenerationRequest, GenerationResponse, Platform
from app.prompts.master_template import compile_master_prompt, compile_shorten_prompt, SYSTEM_PROMPT
from app.services.llm_service import LLMService
from app.utils.validation import is_twitter_over_limit, validate_output

logger = logging.getLogger("copywriter.generator")


class CopyGenerator:
    """Orchestrates prompt compilation, LLM inference, post-generation validation, and refinement."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()

    async def generate_copy(self, request: GenerationRequest) -> GenerationResponse:
        """Process a validated request to generate platform-specific marketing copy.
        
        Args:
            request: Validated GenerationRequest instance.
            
        Returns:
            Structured GenerationResponse with copy and execution metadata.
        """
        # Step 1: Dynamic Prompt Compilation
        master_prompt = compile_master_prompt(request)

        # Step 2: Primary LLM Inference
        raw_copy = await self.llm_service.generate_completion(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=master_prompt,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_output_tokens,
        )

        final_copy = raw_copy

        # Step 3: Platform Specific Length Validation and Shortening Pass
        if request.platform == Platform.TWITTER and is_twitter_over_limit(final_copy):
            logger.info(
                f"Initial Twitter copy ({len(final_copy)} chars) exceeded 280-char limit. "
                "Initiating single shortening pass..."
            )
            shorten_prompt = compile_shorten_prompt(request, final_copy, max_chars=280)
            shortened_copy = await self.llm_service.generate_completion(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=shorten_prompt,
                temperature=min(request.temperature, 0.5),  # Lower temperature for precision
                top_p=request.top_p,
                max_tokens=100,
            )
            if shortened_copy and len(shortened_copy) < len(final_copy):
                final_copy = shortened_copy

        # Step 4: Quality & Safety Validation
        is_valid, warning = validate_output(final_copy, request.platform)
        if not is_valid:
            logger.warning(f"Validation notice: {warning}")

        # Step 5: Structured Response Assembly
        return GenerationResponse(
            product_name=request.product_name,
            platform=request.platform,
            tone=request.tone,
            generated_copy=final_copy,
            model_used=self.llm_service.model_name,
            temperature=request.temperature,
            top_p=request.top_p,
        )
