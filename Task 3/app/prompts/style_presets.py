"""Curated artistic style presets and modifier tags."""

from typing import Dict, List
from app.models import ImageStyle

STYLE_PRESETS: Dict[ImageStyle, List[str]] = {
    ImageStyle.NONE: [],
    ImageStyle.PHOTOREALISTIC: [
        "photorealistic",
        "realistic lighting",
        "high detail",
        "professional 35mm photography",
        "sharp focus",
        "natural texture",
    ],
    ImageStyle.DIGITAL_ART: [
        "digital art",
        "concept art illustration",
        "smooth digital painting",
        "vibrant color palette",
        "artstation trending",
    ],
    ImageStyle.ANIME: [
        "anime aesthetic",
        "makoto shinkai inspired",
        "cel shaded",
        "clean lineart",
        "expressive vibrant colors",
        "studio anime key visual",
    ],
    ImageStyle.CYBERPUNK: [
        "cyberpunk aesthetic",
        "neon lights",
        "futuristic city atmosphere",
        "high contrast chromatic reflections",
        "cinematic volumetric smoke",
    ],
    ImageStyle.FANTASY: [
        "fantasy artwork",
        "magical atmosphere",
        "epic mythological environment",
        "ethereal glowing particles",
        "highly detailed fantasy illustration",
    ],
    ImageStyle.MINIMALIST: [
        "minimalist composition",
        "clean elegant lines",
        "subtle negative space",
        "understated color harmony",
        "modern aesthetic",
    ],
    ImageStyle.WATERCOLOR: [
        "delicate watercolor painting",
        "soft pigment dispersion",
        "textured cold-press paper",
        "loose expressive wet-on-wet brushstrokes",
    ],
    ImageStyle.OIL_PAINTING: [
        "traditional oil painting",
        "visible impasto brush strokes",
        "rich heavy textures",
        "classic chiaroscuro lighting",
        "museum masterpiece",
    ],
    ImageStyle.THREE_D_RENDER: [
        "octane render 3D",
        "unreal engine 5 look",
        "physically based rendering (PBR)",
        "subsurface scattering",
        "raytraced global illumination",
    ],
    ImageStyle.CINEMATIC: [
        "cinematic still frame",
        "anamorphic widescreen lens",
        "dramatic rim lighting",
        "atmospheric depth of field",
        "color graded film look",
    ],
}


def get_style_modifiers(style: ImageStyle | str) -> List[str]:
    """Retrieve list of style modifier keywords for a given style."""
    if isinstance(style, str):
        try:
            style = ImageStyle(style.lower())
        except ValueError:
            return []
    return STYLE_PRESETS.get(style, [])
