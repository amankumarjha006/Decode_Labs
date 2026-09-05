"""Reusable Streamlit UI components and modern styling for Multimodal Image Generation Studio."""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import streamlit as st

from app.config import config
from app.models import (
    AspectRatio,
    ImageGenerationResponse,
    ImageStyle,
    ResolutionPreset,
)
from app.utils.errors import sanitize_debug_data


def inject_custom_css() -> None:
    """Inject polished, modern CSS styling for a state-of-the-art UI."""
    st.markdown(
        """
        <style>
        /* Font & Global reset */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Hero Header Styling */
        .studio-header {
            text-align: center;
            padding: 1.5rem 1rem 1rem 1rem;
            margin-bottom: 1.5rem;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        .studio-title {
            font-size: 2.3rem;
            font-weight: 700;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.3rem;
        }
        .studio-subtitle {
            font-size: 1.05rem;
            color: #94a3b8;
            font-weight: 400;
        }

        /* Status Badges */
        .badge-container {
            display: flex;
            gap: 0.5rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 0.8rem;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .badge-success {
            background-color: rgba(34, 197, 94, 0.15);
            color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .badge-warning {
            background-color: rgba(234, 179, 8, 0.15);
            color: #facc15;
            border: 1px solid rgba(234, 179, 8, 0.3);
        }
        .badge-info {
            background-color: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        /* Card Container */
        .glass-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1.25rem;
        }

        /* Enhanced prompt preview box */
        .prompt-preview-box {
            background: rgba(15, 23, 42, 0.6);
            border-left: 4px solid #818cf8;
            border-radius: 0 8px 8px 0;
            padding: 0.85rem 1.1rem;
            font-size: 0.9rem;
            color: #e2e8f0;
            margin-top: 0.75rem;
            margin-bottom: 1.25rem;
            word-break: break-word;
        }

        /* Image Gallery Card */
        .image-card {
            border-radius: 12px;
            overflow: hidden;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 0.6rem;
            text-align: center;
            margin-bottom: 1rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .image-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }
        .image-meta-tag {
            font-size: 0.8rem;
            color: #94a3b8;
            margin: 0.4rem 0;
        }

        /* Sidebar Info Box */
        .sidebar-section {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
            margin-bottom: 0.75rem;
            font-size: 0.85rem;
        }
        .sidebar-section h4 {
            margin: 0 0 0.4rem 0;
            font-size: 0.9rem;
            color: #e2e8f0;
            font-weight: 600;
        }
        .sidebar-section p, .sidebar-section li {
            color: #94a3b8;
            font-size: 0.8rem;
            margin-bottom: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(is_configured: bool) -> None:
    """Render top brand header with status chips."""
    status_class = "badge-success" if is_configured else "badge-warning"
    status_icon = "🟢" if is_configured else "🟡"
    status_text = "Cloudflare Connected" if is_configured else "Config Required (.env)"

    st.markdown(
        f"""
        <div class="studio-header">
            <div class="studio-title">🖼️ Multimodal Image Generation Studio</div>
            <div class="studio-subtitle">Transform your ideas into AI-generated artwork with Stable Diffusion XL</div>
            <div class="badge-container">
                <span class="status-badge {status_class}">{status_icon} {status_text}</span>
                <span class="status-badge badge-info">⚡ Stable Diffusion XL</span>
                <span class="status-badge badge-info">🔒 Zero-Leak Architecture</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_constraints() -> None:
    """Render clean Model Constraints & Usage Limits in sidebar. No API credentials displayed."""
    st.sidebar.markdown("## ⚙️ Model Constraints & Usage Limits")

    with st.sidebar.expander("ℹ️ Model Information", expanded=True):
        st.markdown(
            """
            **Model:** Stable Diffusion XL  
            **Model ID:** `@cf/stabilityai/stable-diffusion-xl-base-1.0`  
            **Status:** Beta  
            **Provider:** Cloudflare Workers AI  
            """
        )

    with st.sidebar.expander("📐 Image Dimensions", expanded=True):
        st.markdown(
            """
            **Minimum:** 256 × 256 pixels  
            **Maximum:** 2048 × 2048 pixels  

            *Both width and height must remain within the supported range.*
            """
        )

    with st.sidebar.expander("🎨 Generation Settings", expanded=True):
        st.markdown(
            """
            **Steps:** 1–20 (Default: 20)  
            **Guidance:** Controls prompt adherence  
            **Seed:** Optional integer for reproducible results  
            """
        )

    with st.sidebar.expander("🖼️ Application Limits", expanded=False):
        st.markdown(
            """
            **Max images per generation:** 4  
            **Max simultaneous generations:** 2  

            *Multiple images are generated through separate API requests with controlled concurrency.*
            """
        )

    with st.sidebar.expander("☁️ Cloudflare Free Usage", expanded=False):
        st.markdown(
            """
            **Free Allocation:** 10,000 Neurons per day  
            **Reset Time:** 00:00 UTC  
            **Text-to-Image Rate Limit:** Up to 720 requests per minute  

            *Actual image capacity depends on image dimensions and generation settings. Higher resolutions and more inference steps consume more compute.*
            """
        )

    st.sidebar.warning(
        "⚠️ If the Cloudflare daily free allocation is exhausted, image generation requests may fail."
    )


def render_sample_prompts_selector(
    sample_prompts_path: Path,
) -> Optional[Dict[str, Any]]:
    """Dropdown for loading curated sample prompts."""
    if not sample_prompts_path.exists():
        return None

    try:
        with open(sample_prompts_path, "r", encoding="utf-8") as f:
            samples = json.load(f)
    except Exception:
        return None

    options = ["-- Choose an inspiration prompt --"] + [s["title"] for s in samples]
    selected_title = st.selectbox(
        "💡 Quick Inspiration / Sample Prompts",
        options=options,
        index=0,
        help="Quickly load pre-configured prompts with matching styles and ratios.",
    )

    if selected_title and selected_title != "-- Choose an inspiration prompt --":
        for s in samples:
            if s["title"] == selected_title:
                return s
    return None


def render_enhanced_prompt_preview(
    enhanced_prompt: str, applied_modifiers: List[str]
) -> None:
    """Display real-time preview of the enhanced prompt with style modifier badges."""
    mod_html = ""
    if applied_modifiers:
        tags = "".join(
            f'<span style="background:rgba(99,102,241,0.25); color:#a5b4fc; border-radius:4px; padding:2px 6px; margin:2px; font-size:0.75rem; display:inline-block;">+{m}</span>'
            for m in applied_modifiers
        )
        mod_html = f'<div style="margin-top: 6px;"><strong>Active Style Tags:</strong> {tags}</div>'

    st.markdown(
        f"""
        <div style="font-size:0.85rem; font-weight:600; color:#cbd5e1; margin-bottom:4px;">
            ✨ Enhanced Prompt Preview
        </div>
        <div class="prompt-preview-box">
            {enhanced_prompt}
            {mod_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_gallery(response: ImageGenerationResponse) -> None:
    """Display generated images in a clean responsive grid with download buttons."""
    st.markdown("### 🎨 Generated Images")

    if not response.images:
        st.info("No images generated.")
        return

    # Dynamic column layout based on number of images
    num_images = len(response.images)
    cols = st.columns(num_images if num_images in (1, 2) else 2)

    for idx, item in enumerate(response.images):
        col = cols[idx % len(cols)]
        with col:
            st.markdown('<div class="image-card">', unsafe_allow_html=True)

            img_path = Path(item.local_path)
            if img_path.exists():
                st.image(
                    str(img_path),
                    use_container_width=True,
                    caption=f"Image #{idx+1} ({item.width} × {item.height})",
                )

                st.markdown(
                    f'<div class="image-meta-tag">📄 <code>{item.file_name}</code> &nbsp;•&nbsp; 📦 {round(item.file_size_bytes / 1024, 1)} KB</div>',
                    unsafe_allow_html=True,
                )

                # Download button with binary data
                try:
                    with open(img_path, "rb") as file_data:
                        bytes_content = file_data.read()
                    st.download_button(
                        label=f"⬇️ Download Image #{idx+1}",
                        data=bytes_content,
                        file_name=item.file_name,
                        mime=item.mime_type,
                        key=f"dl_btn_{response.request_id}_{idx}",
                        use_container_width=True,
                    )
                except Exception as exc:
                    st.warning(f"Could not prepare download: {exc}")
            else:
                st.error("Image file missing from storage.")

            st.markdown("</div>", unsafe_allow_html=True)


def render_metadata_card(response: ImageGenerationResponse) -> None:
    """Display generation parameters and telemetry summary."""
    with st.expander("📊 Generation Details & Telemetry", expanded=True):
        col1, col2, col3 = st.columns(3)
        col1.markdown("**Model:** Stable Diffusion XL")
        col1.caption(f"ID: `{response.model_used}`")
        col2.markdown(f"**Dimensions:** {response.width} × {response.height}")
        col2.caption(f"Ratio: {response.aspect_ratio.value} ({response.resolution.display_name})")
        col3.markdown(f"**Generation Time:** {response.generation_time_seconds}s")
        col3.caption(f"Images: {len(response.images)}")

        st.markdown("---")
        col4, col5, col6 = st.columns(3)
        col4.markdown(f"**Style:** {response.style.display_name}")
        col5.markdown(f"**Steps:** {response.num_steps}")
        col5.caption(f"Guidance Scale: {response.guidance}")
        seed_label = str(response.seed) if response.seed is not None else "Random"
        col6.markdown(f"**Seed:** {seed_label}")

        if response.negative_prompt:
            st.markdown(f"**Negative Prompt:** *{response.negative_prompt}*")

        if response.warnings:
            st.markdown("---")
            for warn in response.warnings:
                st.caption(f"⚠️ *{warn}*")


def render_debug_panel(debug_info: Optional[Dict[str, Any]]) -> None:
    """Render safe debugging information panel when DEBUG_MODE is enabled."""
    if not debug_info:
        return

    with st.expander("🔧 Debug Information", expanded=False):
        st.markdown("##### Safe Request & Telemetry Details")
        st.json(debug_info)


def render_sidebar_history(
    history_items: List[Dict[str, Any]],
) -> None:
    """Render generation history in sidebar."""
    st.sidebar.markdown("### 🕒 Recent Generations")

    if not history_items:
        st.sidebar.caption("No images generated yet in this session.")
        return

    for idx, record in enumerate(history_items):
        time_str = record.get("created_at", "")[:19].replace("T", " ")
        prompt_snippet = record.get("original_prompt", "")[:35] + (
            "..." if len(record.get("original_prompt", "")) > 35 else ""
        )
        style_name = record.get("style", "None")
        ratio = record.get("aspect_ratio", "1:1")
        img_count = len(record.get("images", []))

        with st.sidebar.expander(f"🖼️ #{idx+1} {prompt_snippet}", expanded=(idx == 0)):
            st.caption(f"📅 **{time_str}**")
            st.caption(f"🎭 Style: `{style_name}` | 📐 Ratio: `{ratio}`")
            st.caption(f"🖼️ Images: `{img_count}`")

            # Thumbnail previews
            images = record.get("images", [])
            if images:
                first_img = images[0]
                local_path = first_img.get("local_path")
                if local_path and Path(local_path).exists():
                    st.image(local_path, use_container_width=True)
