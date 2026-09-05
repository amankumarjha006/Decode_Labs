# Automated Copywriting & Tone Transformer

A Generative AI application that transforms raw product descriptions into platform-specific marketing copy using dynamic prompt templates, tone customization, parameter tuning, asynchronous processing, and structured validation.

Built as part of a **Generative AI Industrial Training Project**.

---

## Overview

Modern digital marketing requires different communication styles for different platforms.

A LinkedIn audience expects professional and business-oriented content, while Instagram users prefer engaging captions and creative hooks. Email marketing requires structured messaging, and X (Twitter) demands concise content within strict character limits.

The **Automated Copywriting & Tone Transformer** solves this problem by dynamically compiling prompts based on:

- Product information
- Target platform
- Desired tone
- Temperature
- Top-P
- Platform-specific constraints

The application then sends the compiled prompt to a Generative AI model through the Groq API and generates customized marketing copy.

---

# Features

## Dynamic Prompt Compilation

The application dynamically injects:

- Product name
- Product description
- Platform
- Tone
- Platform-specific rules
- Generation parameters

into a structured master prompt.

---

## Platform-Specific Copy Generation

Supports:

- LinkedIn
- Instagram
- Email
- X / Twitter

Each platform has its own writing guidelines and formatting requirements.

---

## Tone Transformation

Supports the following tones:

- Professional
- Witty
- Friendly
- Luxury
- Exciting
- Persuasive
- Casual

---

## Temperature and Top-P Control

Users can control the creativity of generated content using:

- `temperature`
- `top_p`

Default values:

```text
Temperature: 0.7
Top-P: 0.9
```

---

## Pydantic Validation

The application validates user input using Pydantic.

Validation includes:

- Product name validation
- Product description validation
- Platform validation
- Tone validation
- Temperature range validation
- Top-P range validation
- Maximum output token validation

---

## Asynchronous Processing

The application supports asynchronous LLM requests using:

```text
asyncio
```

Concurrency is controlled using:

```python
asyncio.Semaphore
```

This prevents too many API requests from being sent simultaneously.

---

## Bulk CSV Processing

Multiple products can be processed from a CSV file.

The application:

1. Reads the CSV file.
2. Validates each row.
3. Creates generation requests.
4. Processes requests asynchronously.
5. Handles individual failures without stopping the entire batch.
6. Exports results to JSON and CSV files.

---

## Retry and Error Handling

The application handles temporary errors such as:

- Rate limit errors
- Network errors
- Temporary server errors

Retry logic uses exponential backoff with jitter.

Permanent errors such as invalid API keys or invalid input are not repeatedly retried.

---

## Rich Terminal Interface

The application uses the `rich` library to provide:

- Formatted output panels
- Error messages
- Generation metadata
- Tables
- User-friendly CLI output

---

# Architecture

```text
                 +----------------------------------+
                 |      User Input                  |
                 |   CLI / CSV / Interactive Mode   |
                 +-----------------+----------------+
                                   |
                                   v
                 +----------------------------------+
                 |     Pydantic Validation          |
                 |  Types, Bounds, Enums, Rules     |
                 +-----------------+----------------+
                                   |
                                   v
                 +----------------------------------+
                 |    Dynamic Prompt Compilation    |
                 |                                  |
                 | Product + Platform + Tone +      |
                 | Platform Rules + Parameters      |
                 +-----------------+----------------+
                                   |
                    +--------------+--------------+
                    |                             |
                    v                             v

          +------------------+          +------------------+
          | Real-Time Mode   |          |   Bulk Mode      |
          |                  |          |                  |
          | Single Request   |          | CSV Processing   |
          +--------+---------+          +--------+---------+
                   |                             |
                   +--------------+--------------+
                                  |
                                  v
                 +----------------------------------+
                 |       Async LLM Service          |
                 |           Groq API               |
                 |                                  |
                 | Retry + Exponential Backoff      |
                 +-----------------+----------------+
                                   |
                                   v
                 +----------------------------------+
                 |     Output Validation           |
                 |                                  |
                 | Length + Empty Output Checks     |
                 +-----------------+----------------+
                                   |
                                   v
                 +----------------------------------+
                 |      Generated Marketing Copy    |
                 |                                  |
                 | Rich Output / JSON / CSV         |
                 +----------------------------------+
```

---

# Project Structure

```text
automated-copywriting-tone-transformer/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── run.py
│
├── app/
│   ├── __init__.py
│   │
│   ├── config.py
│   ├── models.py
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── master_template.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   └── generator.py
│   │
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── realtime.py
│   │   └── bulk.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── retry.py
│   │   ├── validation.py
│   │   └── display.py
│   │
│   └── cli/
│       ├── __init__.py
│       └── arguments.py
│
├── data/
│   └── sample_products.csv
│
├── outputs/
│   └── .gitkeep
│
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_prompt_template.py
    └── test_validation.py
```

---

# Technology Stack

| Technology              | Purpose                         |
| ----------------------- | ------------------------------- |
| Python                  | Core programming language       |
| Groq API                | Generative AI inference         |
| Groq SDK                | Groq API integration            |
| Pydantic                | Data validation                 |
| asyncio                 | Asynchronous processing         |
| argparse                | Command-line interface          |
| Rich                    | Terminal UI                     |
| python-dotenv           | Environment variable management |
| pytest                  | Unit testing                    |
| Tenacity / Custom Retry | Retry handling                  |

---

# Supported Platforms

## LinkedIn

Designed for:

- Professional audiences
- Business communication
- Brand credibility
- Clear messaging

---

## Instagram

Designed for:

- Engaging captions
- Creative writing
- Short paragraphs
- Optional emojis
- Relevant hashtags

---

## Email

Designed to generate:

- Subject line
- Greeting
- Marketing content
- Call to action

---

## X / Twitter

Designed for:

- Short-form content
- Strong hooks
- Concise messaging

The application validates the generated output against Twitter's approximate character limit.

If the output is too long, the application can request a shorter version.

---

# Supported Tones

| Tone         | Description                        |
| ------------ | ---------------------------------- |
| Professional | Formal and business-oriented       |
| Witty        | Clever and humorous                |
| Friendly     | Warm and approachable              |
| Luxury       | Premium and sophisticated          |
| Exciting     | Energetic and enthusiastic         |
| Persuasive   | Focused on convincing the audience |
| Casual       | Relaxed and conversational         |

---

# Understanding Temperature and Top-P

Generative AI models use sampling parameters to control the style and variation of generated text.

## Temperature

Range:

```text
0.0 to 2.0
```

### Lower Temperature

Produces output that is generally:

- More focused
- More predictable
- More consistent
- Less creative

Example:

```text
Temperature: 0.3
```

Useful for:

- Professional content
- Business communication
- Structured copy

---

### Higher Temperature

Produces output that is generally:

- More creative
- More varied
- More experimental

Example:

```text
Temperature: 1.0
```

Useful for:

- Instagram captions
- Creative campaigns
- Witty marketing copy

---

# Top-P

Range:

```text
0.0 to 1.0
```

Top-P controls how broadly the model considers possible next tokens.

### Lower Top-P

Generally produces:

- More focused output
- Less variation

### Higher Top-P

Generally produces:

- More diverse output
- Greater vocabulary variation

---

> **Note:** The exact behavior of `temperature` and `top_p` may vary depending on the model and provider. These parameters are supported by the application's configuration, but their exact effects depend on the selected Groq model.

Recommended defaults:

```text
Temperature: 0.7
Top-P: 0.9
```

---

# Prerequisites

Before running the project, make sure you have:

- Python 3.10 or later
- pip
- A Groq API key

Check your Python installation:

```bash
python --version
```

---

# Installation

## 1. Navigate to the Project Directory

```bash
cd automated-copywriting-tone-transformer
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If using Command Prompt:

```cmd
venv\Scripts\activate
```

---

### macOS / Linux

```bash
python3 -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Groq API Configuration

The project uses the **Groq API** for Generative AI inference.

## 1. Create a `.env` File

Copy `.env.example`.

### Windows

```powershell
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

---

## 2. Add Your Groq API Key

Open `.env` and add:

```env
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Replace:

```text
your_actual_groq_api_key
```

with your actual Groq API key.

Example:

```env
GROQ_API_KEY=gsk_your_secret_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

---

## Important Security Notice

Never:

- Upload `.env` to GitHub
- Share your API key
- Put your API key inside source code
- Include your API key in screenshots

The `.env` file should be included in `.gitignore`.

---

# Available Models

The project currently works with:

```text
openai/gpt-oss-20b
```

You can change the model using:

```env
GROQ_MODEL=your_model_name
```

Make sure the model is currently available to your Groq API account.

If you receive a model error such as:

```text
model_not_found
```

check the configured model name and replace it with a currently supported Groq model.

---

# CLI Usage

The application provides three main modes:

```text
generate
bulk
interactive
```

---

# Help Documentation

View the main CLI help:

```bash
python run.py --help
```

View help for single generation:

```bash
python run.py generate --help
```

View help for bulk processing:

```bash
python run.py bulk --help
```

---

# Single Generation Mode

Generate marketing copy directly from the command line.

Example:

```bash
python run.py generate \
  --product-name "EcoBottle" \
  --description "A reusable stainless steel water bottle that keeps drinks cold for 24 hours." \
  --platform instagram \
  --tone witty \
  --temperature 0.8 \
  --top-p 0.9
```

---

## Windows PowerShell Note

The command above may need to be written on one line:

```powershell
python run.py generate --product-name "EcoBottle" --description "A reusable stainless steel water bottle that keeps drinks cold for 24 hours." --platform instagram --tone witty --temperature 0.8 --top-p 0.9
```

---

# Additional Generate Options

You can also specify:

```text
--max-output-tokens
```

Example:

```bash
python run.py generate \
  --product-name "EcoBottle" \
  --description "A reusable stainless steel water bottle." \
  --platform instagram \
  --tone witty \
  --temperature 0.8 \
  --top-p 0.9 \
  --max-output-tokens 300
```

---

# Available Platforms

```text
linkedin
instagram
email
twitter
```

Example:

```bash
--platform linkedin
```

---

# Available Tones

```text
professional
witty
friendly
luxury
exciting
persuasive
casual
```

Example:

```bash
--tone professional
```

---

# LinkedIn Example

```bash
python run.py generate \
  --product-name "EcoBottle" \
  --description "A reusable stainless steel water bottle that keeps drinks cold for 24 hours." \
  --platform linkedin \
  --tone professional \
  --temperature 0.5 \
  --top-p 0.8
```

---

# Email Example

```bash
python run.py generate \
  --product-name "EcoBottle" \
  --description "A reusable stainless steel water bottle that keeps drinks cold for 24 hours." \
  --platform email \
  --tone persuasive \
  --temperature 0.7 \
  --top-p 0.9
```

---

# Interactive Mode

Run the interactive wizard:

```bash
python run.py interactive
```

The application will ask for:

```text
Product Name
Product Description
Platform
Tone
Temperature
Top-P
Maximum Output Tokens
```

The input is validated before sending the request to the AI model.

---

# Bulk Processing

Bulk processing allows multiple products to be processed from a CSV file.

Example:

```bash
python run.py bulk --input data/sample_products.csv --concurrency 5
```

---

# CSV Format

The CSV file should contain columns similar to:

```csv
product_name,product_description,platform,tone,temperature,top_p
EcoBottle,"Reusable stainless steel bottle that keeps drinks cold for 24 hours",instagram,witty,0.8,0.9
SmartLamp,"WiFi enabled smart lamp with adjustable brightness",linkedin,professional,0.5,0.8
CoffeeMaster,"Automatic coffee machine for home use",email,persuasive,0.7,0.9
```

The exact CSV requirements should match the fields expected by the project's bulk processing implementation.

---

# Bulk Processing Workflow

The bulk pipeline performs the following steps:

```text
CSV File
   │
   ▼
Read CSV Rows
   │
   ▼
Pydantic Validation
   │
   ▼
Create Generation Requests
   │
   ▼
Async Task Creation
   │
   ▼
Semaphore Concurrency Control
   │
   ▼
Groq API Requests
   │
   ▼
Retry Handling
   │
   ▼
Output Validation
   │
   ▼
JSON and CSV Results
```

---

# Bulk Output

Generated files are saved inside:

```text
outputs/
```

Example:

```text
outputs/bulk_results_YYYYMMDD_HHMMSS.json
outputs/bulk_results_YYYYMMDD_HHMMSS.csv
```

Depending on the implementation, failed rows may also be saved separately.

---

# Testing

Run the unit tests:

```bash
python -m pytest
```

For verbose output:

```bash
python -m pytest -v
```

The test suite should validate:

- Pydantic request validation
- Temperature validation
- Top-P validation
- Platform validation
- Tone validation
- Dynamic prompt compilation
- Platform-specific rules
- Output validation
- Empty output handling
- Twitter length validation
- Mocked LLM service behavior

Tests should run without requiring a real Groq API key.

---

# Validation Testing

You can manually test invalid values.

## Invalid Temperature

```bash
python run.py generate \
  --product-name "Test" \
  --description "This is a test product description." \
  --platform instagram \
  --tone witty \
  --temperature 5 \
  --top-p 0.9
```

The application should reject the invalid temperature.

---

## Invalid Platform

```bash
python run.py generate \
  --product-name "Test" \
  --description "This is a test product description." \
  --platform facebook \
  --tone witty
```

The application should reject the invalid platform.

---

# Example Successful Output

A successful generation displays metadata similar to:

```text
Product:        EcoBottle
Platform:       INSTAGRAM
Tone:           Witty
Temperature:    0.80
Top-P:          0.90
Model Used:     openai/gpt-oss-20b
Timestamp:      2026-09-05

Generated Instagram Caption

Think your water bottle is chill?

Stay frosty for 24 hours.

EcoBottle keeps every drink ice-cold from sunrise to sunset.

Perfect for the gym, office, or your next road trip.

Tap the link in bio to grab yours.

#EcoBottle #StayCool #ReusableStyle #SustainableLiving
```

The exact generated content will vary depending on:

- Product description
- Platform
- Tone
- Temperature
- Top-P
- Selected model

---

# Error Handling

The application handles common errors such as:

- Missing API key
- Invalid API key
- Unsupported model
- Invalid platform
- Invalid tone
- Invalid temperature
- Invalid Top-P
- Missing CSV file
- Invalid CSV columns
- Network errors
- Rate limits
- Temporary API failures

---

# Troubleshooting

## Error: GROQ_API_KEY Missing

Make sure your `.env` file exists and contains:

```env
GROQ_API_KEY=your_actual_api_key
```

Restart the terminal after changing environment configuration if necessary.

---

## Error: Model Not Found

Example:

```text
The model does not exist or you do not have access to it.
```

Check:

```env
GROQ_MODEL=openai/gpt-oss-20b
```

Also make sure the configured model is currently available to your Groq API account.

---

## Error: Module Not Found

Run:

```bash
pip install -r requirements.txt
```

Make sure your virtual environment is activated.

---

## PowerShell Execution Policy Error

If PowerShell blocks virtual environment activation, you can temporarily allow it:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## Pytest Not Found

Run:

```bash
python -m pytest
```

If pytest is missing:

```bash
pip install pytest
```

---

# Development Workflow

Recommended workflow:

## 1. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure `.env`

```env
GROQ_API_KEY=your_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

## 4. Test CLI

```bash
python run.py --help
```

## 5. Run Tests

```bash
python -m pytest
```

## 6. Test Interactive Mode

```bash
python run.py interactive
```

## 7. Test Single Generation

```bash
python run.py generate --product-name "EcoBottle" --description "A reusable stainless steel water bottle that keeps drinks cold for 24 hours." --platform instagram --tone witty --temperature 0.8 --top-p 0.9
```

## 8. Test Bulk Processing

```bash
python run.py bulk --input data/sample_products.csv --concurrency 5
```

---

# Security

The project follows basic API security practices:

- API keys are stored in `.env`
- `.env` is excluded from version control
- API keys are never hardcoded
- API keys should never be shared publicly

---

# Future Improvements

Possible future improvements include:

- Web interface using Streamlit or FastAPI
- Support for additional AI providers
- User authentication
- Saved generation history
- Database integration
- Brand profile customization
- Custom prompt templates
- More social media platforms
- Image generation integration
- Content scheduling
- Analytics dashboard
- A/B copy generation
- Multi-language copy generation

---

# Screenshots

Add screenshots of the following features here:

- CLI help screen
- Interactive mode
- Instagram generation
- LinkedIn generation
- Email generation
- Bulk processing results
- Test results

Example screenshot structure:

```text
screenshots/

├── cli-help.png
├── instagram-generation.png
├── linkedin-generation.png
├── email-generation.png
├── bulk-processing.png
└── tests-passed.png
```

---

# Project Requirements Covered

This project demonstrates the following Generative AI engineering concepts:

- Dynamic prompt engineering
- Prompt template compilation
- Variable injection
- Generative AI inference
- Temperature tuning
- Top-P tuning
- Platform-specific content generation
- Tone transformation
- Structured input validation
- Pydantic models
- CLI development
- Async programming
- Concurrency control
- Retry mechanisms
- Exponential backoff
- Bulk AI processing
- CSV ingestion
- Structured JSON and CSV outputs
- Error handling
- Automated testing

---

# License

This project is developed for educational and internship purposes.

You may add an MIT License file if you plan to publish the project publicly.

---

# Author

Developed as part of a Generative AI Industrial Training Project.

---

## Final Testing Checklist

Before submitting the project, verify:

- [ ] Virtual environment is working
- [ ] Dependencies install successfully
- [ ] `.env` file is configured
- [ ] Groq API key works
- [ ] `python run.py --help` works
- [ ] Single generation works
- [ ] Instagram generation works
- [ ] LinkedIn generation works
- [ ] Email generation works
- [ ] Interactive mode works
- [ ] Invalid input validation works
- [ ] Bulk CSV processing works
- [ ] Output files are generated
- [ ] Unit tests pass
- [ ] `.env` is ignored by Git
- [ ] README is updated
- [ ] Screenshots are added if required for submission

---

**Automated Copywriting & Tone Transformer**

Built using **Python, Groq API, Pydantic, AsyncIO, and Generative AI Prompt Engineering**.