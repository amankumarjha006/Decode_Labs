"""Application configuration and environment settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for the project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env file from project root
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# LLM Configuration (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

# Generation Defaults
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_OUTPUT_TOKENS = 500

# Pipeline & Resilience Defaults
DEFAULT_CONCURRENCY = 10
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30.0

# Paths
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


def validate_api_key(api_key: str | None = None) -> bool:
    """Check whether a non-empty Groq API key is configured.
    
    Args:
        api_key: Optional API key string to check. If None, checks GROQ_API_KEY.
        
    Returns:
        True if an API key is set and not a placeholder, False otherwise.
    """
    key = api_key if api_key is not None else GROQ_API_KEY
    if not key or key == "your_groq_api_key_here":
        return False
    return True


def get_api_key_help() -> str:
    """Return friendly guidance on how to configure the Groq API key."""
    return (
        "Groq API key is missing or not configured!\n\n"
        "To configure it:\n"
        "1. Create a `.env` file in the project root by copying `.env.example`:\n"
        "     copy .env.example .env  (on Windows)\n"
        "     cp .env.example .env    (on macOS/Linux)\n"
        "2. Open `.env` and set your real Groq API key:\n"
        "     GROQ_API_KEY=gsk_...\n"
        "3. Alternatively, export it in your terminal:\n"
        "     set GROQ_API_KEY=gsk_...  (CMD)\n"
        "     $env:GROQ_API_KEY='gsk_...' (PowerShell)\n"
    )
