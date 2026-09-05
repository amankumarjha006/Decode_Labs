"""Dynamic master prompt template compiler and platform rule definitions."""

from app.models import GenerationRequest, Platform, Tone

SYSTEM_PROMPT = """You are an elite, multi-award-winning marketing copywriter and brand strategist.
Your mission is to transform raw product features into captivating, high-converting marketing copy tailored precisely to the target platform, tone, and strategic objectives.

You adhere strictly to platform formatting conventions, audience psychology, and brand safety rules. You never fabricate nonexistent product specifications or make unsubstantiated claims."""

PLATFORM_RULES: dict[Platform, str] = {
    Platform.LINKEDIN: (
        "- Platform: LinkedIn\n"
        "- Audience: B2B decision makers, entrepreneurs, professionals, and industry peers.\n"
        "- Style: Professional, polished, insightful, and value-oriented.\n"
        "- Structure:\n"
        "  * Start with a compelling 1-2 sentence hook that stops the scroll.\n"
        "  * Body formatted with generous whitespace, short 1-2 sentence paragraphs, or clean bullet points.\n"
        "  * Connect product capabilities to tangible business outcomes (ROI, efficiency, growth, leadership).\n"
        "  * Conclude with a thought-provoking conversation-starter or professional Call to Action (CTA).\n"
        "  * Include 2 to 4 relevant industry hashtags at the bottom."
    ),
    Platform.INSTAGRAM: (
        "- Platform: Instagram\n"
        "- Audience: Social-first, visual, consumer-centric audience seeking lifestyle enhancement.\n"
        "- Style: Vibrant, creative, sensory-rich, visually expressive, and immediately engaging.\n"
        "- Structure:\n"
        "  * Grab attention in the first line before the '...more' cut-off.\n"
        "  * Bite-sized paragraphs with tasteful, thematic emoji integration.\n"
        "  * Emphasize aesthetics, daily life integration, and emotional connection.\n"
        "  * Clear, low-friction Call to Action (e.g., 'Tap the link in bio', 'Drop a comment below').\n"
        "  * Include 5 to 10 targeted, community and lifestyle hashtags grouped at the end."
    ),
    Platform.EMAIL: (
        "- Platform: Marketing Email\n"
        "- Audience: Subscribers and prospective customers expecting value in their inbox.\n"
        "- Style: Conversational, personalized, clear, and action-driving.\n"
        "- Mandatory Structure:\n"
        "  Subject Line: [High-converting, curiosity-evoking subject line under 55 characters]\n"
        "  Preview Text: [Engaging pre-header snippet under 90 characters]\n"
        "  Salutation: [Warm greeting, e.g. 'Hi {{First_Name}},' or 'Hello,']\n"
        "  Body: [Compelling storytelling, core value proposition, key bullet points/benefits]\n"
        "  Call to Action (CTA): [Prominent, decisive CTA button or link text, e.g., 'Claim Your Access Now ->']\n"
        "  Sign-off: [Professional sign-off and brand signature]\n"
        "- Constraints: DO NOT include social media hashtags (#) in email copy."
    ),
    Platform.TWITTER: (
        "- Platform: X / Twitter\n"
        "- Audience: Fast-moving, attention-constrained digital audience.\n"
        "- Style: Punchy, razor-sharp, memorable, and high-impact.\n"
        "- Mandatory Constraints:\n"
        "  * Absolute hard maximum of 280 characters for the entire post.\n"
        "  * Front-load the hook in the opening 5 words.\n"
        "  * Crisp, punchy phrasing without filler.\n"
        "  * Include 1 or 2 high-relevance hashtags max.\n"
        "  * No excessive whitespace or lengthy line breaks."
    ),
}

TONE_GUIDELINES: dict[Tone, str] = {
    Tone.PROFESSIONAL: (
        "Maintain an authoritative, articulate, and credible voice. Emphasize competence, trust, and business value."
    ),
    Tone.WITTY: (
        "Infuse clever wordplay, subtle irony, and humorous turns of phrase while keeping the core product proposition sharp."
    ),
    Tone.FRIENDLY: (
        "Adopt a warm, inviting, approachable, and authentic peer-to-peer conversational tone."
    ),
    Tone.LUXURY: (
        "Exude exclusivity, craftsmanship, prestige, and quiet confidence through refined and aspirational vocabulary."
    ),
    Tone.EXCITING: (
        "Deliver electrifying energy, urgent enthusiasm, dynamic verbs, and motivational momentum."
    ),
    Tone.PERSUASIVE: (
        "Focus on psychological triggers, overcoming friction, compelling proof points, and an irresistible call to action."
    ),
    Tone.CASUAL: (
        "Keep it effortless, conversational, jargon-free, and natural—like talking to a good friend."
    ),
}


def _get_creativity_guidance(temperature: float, top_p: float) -> str:
    """Generate dynamic instructions reflecting the temperature and top-p configuration."""
    if temperature <= 0.4:
        temp_note = "Strictly factual, highly consistent, disciplined phrasing. Avoid whimsical metaphors."
    elif temperature <= 0.8:
        temp_note = "Balanced blend of creative flair and structured clarity. Fresh phrasing with disciplined focus."
    else:
        temp_note = "High creative latitude, unexpected associations, distinctive vocabulary, and bold narrative angles."

    if top_p <= 0.5:
        topp_note = "Narrow, focused token selection prioritizing the most probable, authoritative language."
    else:
        topp_note = "Expansive vocabulary pool allowing diverse stylistic nuances."

    return f"- Temperature ({temperature:.2f}): {temp_note}\n- Top-P ({top_p:.2f}): {topp_note}"


def compile_master_prompt(request: GenerationRequest) -> str:
    """Compile a complete, dynamic prompt from the user request and platform constraints.
    
    Args:
        request: Validated GenerationRequest containing product, platform, tone, and tuning.
        
    Returns:
        Fully compiled prompt string ready for LLM inference.
    """
    platform_rules = PLATFORM_RULES.get(
        request.platform,
        PLATFORM_RULES[Platform.LINKEDIN]
    )
    tone_guidance = TONE_GUIDELINES.get(
        request.tone,
        TONE_GUIDELINES[Tone.PROFESSIONAL]
    )
    creativity_guidance = _get_creativity_guidance(request.temperature, request.top_p)

    return f"""You are generating marketing copy for the following product:

PRODUCT NAME:
{request.product_name}

RAW PRODUCT DESCRIPTION:
{request.product_description}

TARGET PLATFORM:
{request.platform.value.upper()}

REQUIRED TONE:
{request.tone.value.upper()} - {tone_guidance}

PLATFORM REQUIREMENTS:
{platform_rules}

INFERENCE TUNING GUIDANCE:
{creativity_guidance}

CRITICAL COPYWRITING DIRECTIVES:
1. Adhere strictly to the requested tone ({request.tone.value}) across every sentence.
2. Comply fully with the target platform's formatting, length limits, and visual conventions.
3. Ground all claims strictly in the provided product details. Do not fabricate technical specifications, certifications, or guarantees.
4. Deliver immediately usable, production-ready copy without meta-commentary (do not include phrases like 'Here is your copy:').
5. If writing for Twitter/X, keep the entire output under 280 characters.
6. If writing for Email, retain all required headers (Subject Line, Preview Text, Salutation, Body, CTA, Sign-off).

Generate the final marketing copy now:"""


def compile_shorten_prompt(request: GenerationRequest, original_copy: str, max_chars: int = 280) -> str:
    """Create a prompt to condense generated copy that exceeded strict platform limits (e.g. Twitter).
    
    Args:
        request: The original GenerationRequest.
        original_copy: The copy that exceeded character limits.
        max_chars: Target hard limit.
        
    Returns:
        Compilation prompt for shortening the text.
    """
    return f"""The marketing copy below for {request.product_name} on {request.platform.value.upper()} is currently {len(original_copy)} characters, which EXCEEDS the hard maximum limit of {max_chars} characters.

ORIGINAL COPY:
{original_copy}

TASK:
Condense and rewrite this copy so that its TOTAL character count is strictly LESS than or equal to {max_chars} characters.
- Retain the {request.tone.value} tone.
- Preserve the most powerful hook and the primary benefit of {request.product_name}.
- Keep 1 relevant hashtag if space permits.
- Return ONLY the shortened marketing copy text, with no introductory or explanatory remarks."""
