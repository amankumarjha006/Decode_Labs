"""Multimodal Image Generation Studio - Main Streamlit Web Application (Stable Diffusion XL)."""

import asyncio
from typing import Any, Dict, List, Optional
import streamlit as st

from app.config import config
from app.models import (
    AspectRatio,
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageStyle,
    ResolutionPreset,
)
from app.prompts.prompt_builder import build_enhanced_prompt
from app.services.cloudflare_service import CloudflareWorkersAIService
from app.services.image_storage_service import ImageStorageService
from app.ui.components import (
    inject_custom_css,
    render_debug_panel,
    render_enhanced_prompt_preview,
    render_gallery,
    render_header,
    render_metadata_card,
    render_sample_prompts_selector,
    render_sidebar_constraints,
    render_sidebar_history,
)
from app.utils.errors import CloudflareAPIError, StudioError, ValidationError
from app.utils.image_utils import get_target_dimensions, validate_dimensions
from app.utils.validation import (
    sanitize_prompt,
    validate_generation_count,
    validate_guidance,
    validate_num_steps,
    validate_seed,
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Multimodal Image Generation Studio",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject modern styling
inject_custom_css()

# Initialize session state collections
if "history" not in st.session_state:
    storage_svc = ImageStorageService()
    st.session_state["history"] = storage_svc.list_recent_metadata(limit=10)

if "current_response" not in st.session_state:
    st.session_state["current_response"] = None

if "current_debug_info" not in st.session_state:
    st.session_state["current_debug_info"] = None

if "prompt_input" not in st.session_state:
    st.session_state["prompt_input"] = ""

if "selected_style" not in st.session_state:
    st.session_state["selected_style"] = ImageStyle.NONE

if "selected_ratio" not in st.session_state:
    st.session_state["selected_ratio"] = AspectRatio.RATIO_1_1

# Services
storage_service = ImageStorageService()
cloudflare_service = CloudflareWorkersAIService(storage_service=storage_service)

# Render Header
render_header(is_configured=config.is_cloudflare_configured())

# Sidebar: Model Constraints & Usage Limits (Provider Configuration completely removed)
render_sidebar_constraints()

# Render History in Sidebar
render_sidebar_history(st.session_state["history"])

# Main Form Area
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

# Sample Prompt Loader
sample = render_sample_prompts_selector(config.sample_prompts_file)
if sample:
    st.session_state["prompt_input"] = sample.get("prompt", "")
    try:
        st.session_state["selected_style"] = ImageStyle(sample.get("style", "none"))
    except ValueError:
        st.session_state["selected_style"] = ImageStyle.NONE
    try:
        st.session_state["selected_ratio"] = AspectRatio(sample.get("aspect_ratio", "1:1"))
    except ValueError:
        st.session_state["selected_ratio"] = AspectRatio.RATIO_1_1

# Prompt Input Area
prompt_text = st.text_area(
    "✏️ Prompt (Required)",
    value=st.session_state["prompt_input"],
    placeholder="A futuristic cyberpunk city at night with neon lights, flying cars, cinematic lighting, highly detailed",
    height=110,
    help="Describe the scene, subject, atmosphere, and visual details you wish to see.",
    key="main_prompt_text",
)

# Optional Negative Prompt Area
negative_prompt_text = st.text_input(
    "🚫 Negative Prompt (Optional)",
    placeholder="blurry, low quality, distorted, watermark, text",
    help="Describe visual elements to exclude from the generated image. Only sent to the model when provided.",
)

# Core Control Row
col_style, col_ratio, col_res, col_count = st.columns([1.2, 1, 1, 1])

# Style Selector
style_options = list(ImageStyle)
style_index = (
    style_options.index(st.session_state["selected_style"])
    if st.session_state["selected_style"] in style_options
    else 0
)
with col_style:
    selected_style: ImageStyle = st.selectbox(
        "🎭 Style Preset",
        options=style_options,
        index=style_index,
        format_func=lambda s: s.display_name,
    )

# Aspect Ratio Selector
ratio_options = list(AspectRatio)
ratio_index = (
    ratio_options.index(st.session_state["selected_ratio"])
    if st.session_state["selected_ratio"] in ratio_options
    else 0
)
with col_ratio:
    selected_ratio: AspectRatio = st.selectbox(
        "📐 Aspect Ratio",
        options=ratio_options,
        index=ratio_index,
        format_func=lambda r: r.display_label,
    )

# Resolution Selector
with col_res:
    selected_resolution: ResolutionPreset = st.selectbox(
        "🔍 Resolution",
        options=list(ResolutionPreset),
        format_func=lambda res: res.display_name,
    )

# Generation Count Selector
with col_count:
    generation_count = st.number_input(
        "🔢 Image Count",
        min_value=1,
        max_value=4,
        value=1,
        step=1,
        help="Generate between 1 to 4 variations. Each image is requested individually with controlled concurrency.",
    )

# Expandable Advanced Settings Section
with st.expander("🛠️ Advanced Settings", expanded=False):
    adv_col1, adv_col2, adv_col3 = st.columns(3)
    with adv_col1:
        use_seed = st.checkbox("Specify Seed", value=False)
        seed_value: Optional[int] = None
        if use_seed:
            seed_value = st.number_input(
                "Seed Value",
                min_value=0,
                max_value=2147483647,
                value=42,
                step=1,
                help="A seed can help reproduce similar results with the same model and settings.",
            )

    with adv_col2:
        num_steps = st.slider(
            "Number of Steps",
            min_value=1,
            max_value=20,
            value=20,
            step=1,
            help="Higher values may improve image quality but can increase generation time. (1–20, default: 20)",
        )

    with adv_col3:
        guidance_scale = st.slider(
            "Guidance Scale",
            min_value=1.0,
            max_value=20.0,
            value=7.5,
            step=0.5,
            help="Controls how closely the generated image follows the prompt.",
        )

# Real-time Enhanced Prompt Preview
preview_result = build_enhanced_prompt(
    prompt=prompt_text or "A futuristic cyberpunk city at night with neon lights...",
    style=selected_style,
)
render_enhanced_prompt_preview(
    enhanced_prompt=preview_result.enhanced_prompt,
    applied_modifiers=preview_result.applied_modifiers,
)

# Generation Execution Button
generate_clicked = st.button(
    "🚀 Generate Artwork",
    type="primary",
    use_container_width=True,
)

st.markdown("</div>", unsafe_allow_html=True)

# Process Generation
if generate_clicked:
    # 1. Validate inputs prior to invoking API
    try:
        clean_prompt = sanitize_prompt(prompt_text)
        calc_w, calc_h = get_target_dimensions(selected_ratio, selected_resolution)
        validate_dimensions(calc_w, calc_h)
        validated_steps = validate_num_steps(num_steps)
        validated_guidance = validate_guidance(guidance_scale)
        validated_count = validate_generation_count(int(generation_count))
        validated_seed = validate_seed(seed_value)

        req = ImageGenerationRequest(
            prompt=clean_prompt,
            negative_prompt=negative_prompt_text.strip() if negative_prompt_text and negative_prompt_text.strip() else None,
            style=selected_style,
            aspect_ratio=selected_ratio,
            resolution=selected_resolution,
            width=calc_w,
            height=calc_h,
            generation_count=validated_count,
            seed=validated_seed,
            num_steps=validated_steps,
            guidance=validated_guidance,
        )
    except (ValidationError, ValueError) as exc:
        st.error(f"Validation Error: {exc}")
        st.stop()
    except Exception as exc:
        st.error(f"Input Error: {exc}")
        st.stop()

    # 2. Check credentials
    if not config.is_cloudflare_configured():
        st.error(
            "Cloudflare credentials not configured. Please set `CLOUDFLARE_ACCOUNT_ID` "
            "and `CLOUDFLARE_API_TOKEN` in your `.env` file."
        )
        st.stop()

    # 3. Trigger async generation
    with st.spinner(f"Synthesizing {req.generation_count} image(s) with {config.cloudflare_model}..."):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response: ImageGenerationResponse = loop.run_until_complete(
                cloudflare_service.generate(req)
            )
            loop.close()

            st.session_state["current_response"] = response
            st.session_state["current_debug_info"] = response.debug_info

            # Update session history
            history_record = {
                "request_id": response.request_id,
                "created_at": response.created_at,
                "generation_time_seconds": response.generation_time_seconds,
                "original_prompt": response.original_prompt,
                "enhanced_prompt": response.enhanced_prompt,
                "negative_prompt": response.negative_prompt,
                "style": response.style.display_name,
                "aspect_ratio": response.aspect_ratio.value,
                "resolution": response.resolution.display_name,
                "width": response.width,
                "height": response.height,
                "num_steps": response.num_steps,
                "guidance": response.guidance,
                "seed": response.seed,
                "images": [img.model_dump() for img in response.images],
            }
            st.session_state["history"].insert(0, history_record)
            st.success(f"✨ Artwork generated successfully in {response.generation_time_seconds}s!")
            st.rerun()

        except StudioError as exc:
            st.error(f"❌ {exc.user_friendly_message}")
            if config.debug_mode:
                st.session_state["current_debug_info"] = {
                    "error_type": type(exc).__name__,
                    "error_message": exc.message,
                    "status_code": getattr(exc, "status_code", None),
                    "error_code": getattr(exc, "error_code", None),
                    "response_body": getattr(exc, "response_body", None),
                }
        except Exception as exc:
            st.error(f"❌ An unexpected error occurred: {str(exc)}")
            if config.debug_mode:
                st.session_state["current_debug_info"] = {
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }

# Render Current Results if available
if st.session_state["current_response"]:
    resp = st.session_state["current_response"]
    render_gallery(resp)
    render_metadata_card(resp)

# Render Debug Information Panel if DEBUG_MODE is enabled
if config.debug_mode and st.session_state.get("current_debug_info"):
    render_debug_panel(st.session_state["current_debug_info"])
