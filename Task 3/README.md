# 🖼️ Multimodal Image Generation Studio

A production-grade visual Generative AI application built with **Streamlit**, **Pydantic**, and **Cloudflare Workers AI** featuring **Stable Diffusion XL** (`@cf/stabilityai/stable-diffusion-xl-base-1.0`). It transforms natural-language prompts into high-resolution digital artwork with non-destructive style enhancement, aspect-ratio tuning, controlled concurrency, robust retry semantics, and a zero-credential-leak architecture.

---

## 📌 Project Overview

Multimodal Image Generation Studio demonstrates end-to-end integration of modern diffusion foundation models via secure REST endpoints. The application features comprehensive input validation, provider abstraction, asynchronous concurrent execution, Pillow image integrity verification, local persistence, responsive gallery presentation, and sanitized debugging.

### Key Capabilities
- **Model:** `@cf/stabilityai/stable-diffusion-xl-base-1.0` hosted on Cloudflare Workers AI.
- **Supported Parameters:** `prompt`, `negative_prompt`, `width`, `height`, `num_steps`, `guidance`, `seed`.
- **Resolution & Aspect Ratio:** Centralized resolution presets (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`) in Standard and High quality, strictly validated within 256–2048 pixels.
- **Safe Concurrency (1 to 4 Images):** Asynchronous generation throttled via `asyncio.Semaphore(2)` to generate multi-image variations safely without exceeding rate limits.
- **Pillow Verification & Local Storage:** Validates image integrity and format before saving to `outputs/generated_images/` with collision-proof timestamped filenames.
- **Structured Error Handling:** Structured `CloudflareAPIError` capturing HTTP status codes, error codes, and responses with granular troubleshooting guidance.
- **Sanitized Debug Mode:** Collapsible `🔧 Debug Information` panel enabled via `DEBUG_MODE=true` with all secrets redacted.
- **Zero-Credential-Leak Security:** Credentials are kept exclusively in `.env`. API tokens and authorization headers are strictly excluded from UI, logs, and metadata.

---

## 🏗️ Architecture

```text
User Prompt & Controls (Streamlit UI)
    ↓
Semantic Validation (app/utils/validation.py & app/models.py)
    ↓
Prompt Enhancement Engine (app/prompts/prompt_builder.py)
    ↓
Centralized Payload Construction (app/services/cloudflare_service.py)
    ↓
Cloudflare Workers AI REST API (asyncio.Semaphore(2) Concurrency)
    ↓
Response Parsing (Binary PNG / JPEG or Base64 JSON)
    ↓
Pillow Image Verification (app/utils/image_utils.py)
    ↓
Local Storage & JSON Metadata (app/services/image_storage_service.py)
    ↓
Streamlit Gallery, Download Buttons & Telemetry (app/ui/components.py)
```

---

## 📁 Project Structure

```
multimodal-image-generation-studio/
├── README.md                           # Comprehensive documentation
├── requirements.txt                    # Project dependencies
├── .env.example                        # Template for environment configuration
├── .gitignore                          # Excludes credentials and output files
├── run.py                              # Entrypoint runner script
├── streamlit_app.py                    # Main Streamlit web application
│
├── app/
│   ├── __init__.py                     # Package initialization
│   ├── config.py                       # App configuration & credential masking
│   ├── models.py                       # Domain models & Pydantic validation
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── prompt_builder.py           # Style injection & deduplication
│   │   └── style_presets.py            # Artistic style presets dictionary
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_generation_service.py # Provider abstract interface
│   │   ├── cloudflare_service.py       # Cloudflare Workers AI client (SDXL)
│   │   └── image_storage_service.py    # Pillow verification & disk persistence
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── image_utils.py              # Resolution presets & dimension validation
│   │   ├── validation.py               # Input validation & boundary checks
│   │   ├── retry.py                    # Exponential backoff with jitter
│   │   └── errors.py                   # Custom exceptions & debug sanitization
│   │
│   └── ui/
│       ├── __init__.py
│       └── components.py               # Gallery, metadata card, debug panel, styling
│
├── data/
│   └── sample_prompts.json             # Curated sample prompts
│
├── outputs/
│   ├── generated_images/               # Destination for generated PNG files
│   └── metadata/                       # Destination for JSON metadata files
│
└── tests/
    ├── __init__.py
    ├── test_cloudflare_service.py      # Mocked API, SDXL payload & error parsing tests
    ├── test_image_utils.py             # PIL image validation & resolution tests
    ├── test_models.py                  # Pydantic constraint validation tests
    ├── test_prompt_builder.py          # Prompt enhancement & style tests
    └── test_validation.py              # Dimension, step, count & sanitization tests
```

---

## 🔑 Cloudflare API Configuration

### 1. Obtain Cloudflare API Credentials
1. Log into your [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Select your account and locate your **Account ID** in the right-hand sidebar.
3. Navigate to **My Profile > API Tokens > Create Token**.
4. Select the **Workers AI** template (or create a custom token granting `Workers AI: Read` permissions).
5. Copy your generated API Token.

> ⚠️ **IMPORTANT SECURITY NOTICE:**
> Never commit your `.env` file or share your API token. The application strictly masks tokens in the UI and redacts them from debug views and logs.

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env` in the project root:

```ini
# Cloudflare Workers AI Credentials
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
CLOUDFLARE_MODEL=@cf/stabilityai/stable-diffusion-xl-base-1.0

# Runtime Configuration
REQUEST_TIMEOUT=120
MAX_RETRIES=3
MAX_CONCURRENT_GENERATIONS=2
DEBUG_MODE=false
```

---

## ⚙️ Model Parameters & Constraints

The application targets `@cf/stabilityai/stable-diffusion-xl-base-1.0` via the Cloudflare Workers AI endpoint:
`https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0`

| Parameter | Type | Allowed Values | Default | Description |
|---|---|---|---|---|
| `prompt` | String | 3–2000 chars | *Required* | Main scene description (enhanced with selected style modifiers) |
| `negative_prompt` | String | Optional | `None` | Elements to exclude (only sent to API when entered) |
| `width` | Integer | 256–2048 px | Presets | Pixel width calculated from aspect ratio and resolution preset |
| `height` | Integer | 256–2048 px | Presets | Pixel height calculated from aspect ratio and resolution preset |
| `num_steps` | Integer | 1–20 | 20 | Inference denoising steps (higher values increase detail/time) |
| `guidance` | Float | 1.0–20.0 | 7.5 | Classifier-Free Guidance scale (prompt adherence) |
| `seed` | Integer | 0–2,147,483,647 | Optional (`None`) | Seed for deterministic/reproducible generations |

### Dimension Limits & Resolution Presets
All image dimensions are strictly validated prior to dispatch:
`256 <= width <= 2048` and `256 <= height <= 2048`.

```python
RESOLUTION_PRESETS = {
    "standard": {
        "1:1": (512, 512),
        "16:9": (768, 432),
        "9:16": (432, 768),
        "4:3": (640, 480),
        "3:4": (480, 640),
    },
    "high": {
        "1:1": (1024, 1024),
        "16:9": (1024, 576),
        "9:16": (576, 1024),
        "4:3": (1024, 768),
        "3:4": (768, 1024),
    },
}
```

---

## 🚦 Concurrency & Multi-Image Generation

Cloudflare Workers AI processes one image per REST invocation. When generating multiple images (1 to 4):
- Individual requests are dispatched with independent seeds (`seed + index * 7919`).
- Simultaneous requests are throttled using `asyncio.Semaphore(2)`.
- If one request fails, successfully generated images are preserved and displayed, while the error is clearly reported in session warnings.

---

## 🔧 Debug Mode & Troubleshooting

Enable debug mode in `.env`:
```ini
DEBUG_MODE=true
```

When enabled, a collapsible `🔧 Debug Information` section appears in the UI displaying sanitized telemetry:
- Request ID & Model ID
- Safe API endpoint with masked account ID
- Sanitized payload parameters
- HTTP response code & Content-Type
- Generation duration & Image byte size
- Cloudflare error code & message

### Troubleshooting Common Errors

| Status | Cause | Application Response / Action |
|---|---|---|
| **400** | Invalid dimensions, steps > 20, or prompt issue | Displays exact Cloudflare parameter error: `"Cloudflare API Error (400): Invalid parameter: num_steps must be less than or equal to 20."` |
| **401** | Invalid or revoked API token | `"Authentication failed. Please check your Cloudflare API token."` |
| **403** | Missing Workers AI permissions or wrong Account ID | `"Access to Cloudflare Workers AI was denied. Check your API token permissions and Cloudflare account access."` |
| **404** | Invalid model ID or account endpoint | Displays: `"The requested Cloudflare model or API endpoint could not be found. Current Model: @cf/stabilityai/stable-diffusion-xl-base-1.0"` |
| **408** | Request timed out on Cloudflare | `"The image generation request timed out. Try reducing the image resolution or retrying the request."` |
| **413** | Payload too large | `"The request was too large. Try reducing the image size or prompt complexity."` |
| **429 (Daily Quota)** | Free tier 10,000 neurons exhausted | Automatically detected. Displays: `"Daily Cloudflare Workers AI free allocation has been exhausted. The free allocation resets at 00:00 UTC."` Does not loop retries. |
| **429 (Rate Limit)** | Temporary rate limit exceeded | Automatically retried with exponential backoff and random jitter. Displays: `"Cloudflare is currently rate limiting requests. Please wait a moment and try again."` |
| **500–599** | Temporary Workers AI compute failure | Automatically retried up to `MAX_RETRIES=3`. Displays user-friendly retry status. |
| **Timeout / Network** | Network connectivity or DNS error | Handled via `httpx.TimeoutException` and `httpx.NetworkError`. Displays: `"Unable to connect to Cloudflare Workers AI. Please check your internet connection and try again."` |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (Python 3.11, 3.12, 3.13, 3.14 supported)
- Cloudflare Account with Workers AI enabled

### 2. Virtual Environment Setup

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` and provide your `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`.

### 5. Run the Test Suite
```bash
python -m pytest -v
```
All 50 tests run fully offline with mocks without requiring real credentials or consuming Cloudflare credits.

### 6. Start the Application
```bash
python run.py
```
Or directly via Streamlit:
```bash
streamlit run streamlit_app.py
```
The studio will be available in your browser at `http://localhost:8501`.

---

## 🔒 Zero-Leak Security Architecture
- Credentials (`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`) are loaded from `.env` or system environment variables only.
- The sidebar displays **Model Constraints & Usage Limits** instead of API keys or provider inputs.
- All debug dumps and log statements pass through `sanitize_debug_data()` which automatically strips and redacts keys containing `token`, `authorization`, `secret`, `password`, or `api_key`.
- Image metadata persisted to `outputs/metadata/` never stores authentication headers or credentials.

---

## 📄 License
MIT License. Built for Generative AI engineering and production demonstration.
