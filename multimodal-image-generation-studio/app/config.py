"""Application configuration management using python-dotenv and environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load .env file if it exists
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """Application settings loaded from environment with sensible defaults."""

    # Cloudflare Credentials & Endpoint Settings
    cloudflare_account_id: str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    cloudflare_api_token: str = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    cloudflare_model: str = os.getenv(
        "CLOUDFLARE_MODEL", "@cf/stabilityai/stable-diffusion-xl-base-1.0"
    ).strip()

    # Network & Concurrency Settings
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "120.0"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    default_generation_count: int = int(os.getenv("DEFAULT_GENERATION_COUNT", "1"))
    max_concurrent_generations: int = int(os.getenv("MAX_CONCURRENT_GENERATIONS", "2"))
    debug_mode: bool = os.getenv("DEBUG_MODE", "false").strip().lower() in ("true", "1", "yes")

    # File Storage Paths
    output_directory: Path = PROJECT_ROOT / "outputs"
    generated_images_dir: Path = PROJECT_ROOT / "outputs" / "generated_images"
    metadata_dir: Path = PROJECT_ROOT / "outputs" / "metadata"
    sample_prompts_file: Path = PROJECT_ROOT / "data" / "sample_prompts.json"

    def is_cloudflare_configured(self) -> bool:
        """Check if Cloudflare credentials are configured and not placeholder values."""
        account_valid = bool(
            self.cloudflare_account_id
            and self.cloudflare_account_id != "your_cloudflare_account_id"
        )
        token_valid = bool(
            self.cloudflare_api_token
            and self.cloudflare_api_token != "your_cloudflare_api_token"
        )
        return account_valid and token_valid

    def get_masked_token(self) -> str:
        """Return masked token for secure UI display without leaking secrets."""
        if not self.cloudflare_api_token:
            return "Not Set"
        if len(self.cloudflare_api_token) <= 8:
            return "••••••••"
        return f"{self.cloudflare_api_token[:4]}••••••••{self.cloudflare_api_token[-4:]}"

    def get_masked_account_id(self) -> str:
        """Return masked account ID for secure display."""
        if not self.cloudflare_account_id:
            return "Not Set"
        if len(self.cloudflare_account_id) <= 6:
            return "••••••"
        return f"{self.cloudflare_account_id[:4]}••••{self.cloudflare_account_id[-4:]}"

    def ensure_directories(self) -> None:
        """Ensure necessary output directories exist."""
        self.generated_images_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)


# Global config instance
config = AppConfig()
config.ensure_directories()
