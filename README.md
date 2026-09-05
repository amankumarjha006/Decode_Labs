# 🚀 Decode Labs Internship Projects

A collection of Artificial Intelligence and Generative AI projects developed as part of my internship at Decode Labs.

This repository contains practical AI applications built using Python, Generative AI, Large Language Models, Natural Language Processing, Cloud APIs, and Multimodal AI.

## 📌 Repository Overview

Task

Project

Description

## 🤖 Task 1

AI ChatBot

An AI-powered chatbot for conversational interactions

## 🎭 Task 2

Tone Transformer

An AI application that transforms text into different tones and writing styles

## 🖼️ Task 3

Image Generator

A multimodal AI application that generates images from text prompts

📂 Repository Structure

Decode_Labs
│
├── Task 1 (AI ChatBot)
│   ├── Source Code
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── Task 2 (Tone Transformer)
│   ├── Source Code
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── Task 3 (Image Generator)
│   ├── Source Code
│   ├── outputs/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
└── README.md

Each project is independent and can be installed and run separately.

## 🤖 Task 1: AI ChatBot

An AI-powered chatbot application designed to interact with users and generate intelligent responses.

✨ Key Features

💬 Conversational AI

🧠 Natural language interaction

⚡ AI-powered responses

🔗 API integration

🖥️ User-friendly interface

📁 Project Folder: Task 1 (AI ChatBot)

Refer to the project's individual README for setup and usage instructions.

## 🎭 Task 2: Tone Transformer

Tone Transformer is an AI-powered application that transforms user-provided text into different tones and writing styles.

✨ Key Features

✍️ AI-powered text transformation

🎨 Multiple writing tones

🧠 Natural Language Processing

⚡ Fast AI-generated responses

🔗 API integration

🖥️ User-friendly interface

📁 Project Folder: Task 2 (Tone Transformer)

Refer to the project's individual README for detailed setup and usage instructions.

## 🖼️ Task 3: Multimodal Image Generation Studio

Multimodal Image Generation Studio is an AI-powered text-to-image generation application.

Users can enter a text prompt and generate AI images using Cloudflare Workers AI and Stable Diffusion XL.

🤖 AI Model

@cf/stabilityai/stable-diffusion-xl-base-1.0

Provider

Cloudflare Workers AI

✨ Key Features

🎨 Text-to-Image Generation

Generate AI images using natural language prompts.

Example:

A futuristic cyberpunk city at night with neon lights,
flying cars, cinematic lighting, highly detailed

🚫 Negative Prompts

Users can specify elements they do not want in the generated image.

Example:

blurry, low quality, distorted, watermark, text

📐 Aspect Ratio Selection

Supported aspect ratios include:

1:1

16:9

9:16

4:3

3:4

🖼️ Resolution Selection

The selected resolution and aspect ratio are converted into valid width and height values before sending the request to the AI model.

⚙️ Advanced Generation Settings

Users can configure:

Seed

Number of Steps

Guidance Scale

🖼️ Multiple Image Generation

Users can generate multiple images from the same prompt.

Supported range:

1–4 images

Multiple images are generated through separate API requests with controlled concurrency.

💾 Image Storage

Generated images are automatically saved locally:

outputs/generated_images/

Generation metadata is stored in:

outputs/metadata/

🛡️ Error Handling and Debugging

The application includes structured error handling for:

Invalid requests

Authentication failures

Permission errors

Rate limiting

Cloudflare server errors

Network errors

Request timeouts

Debug mode can be configured using:

DEBUG_MODE=false

To enable debugging:

DEBUG_MODE=true

Sensitive credentials such as API tokens are never displayed.

📁 Project Folder: Task 3 (Image Generator)

🛠️ Technologies Used

Programming Language

Python

Artificial Intelligence

Generative AI

Large Language Models

Natural Language Processing

Multimodal AI

Text-to-Image Generation

AI Services and APIs

Groq API

Cloudflare Workers AI

Stable Diffusion XL

Frameworks and Tools

Streamlit

Pillow

REST APIs

Git

GitHub

Python Virtual Environments

⚙️ Getting Started

1️⃣ Clone the Repository

git clone https://github.com/amankumrjha06/Decode_Labs.git

Navigate to the repository:

cd Decode_Labs

2️⃣ Choose a Project

cd "Task 1 (AI ChatBot)"

or:

cd "Task 2 (Tone Transformer)"

or:

cd "Task 3 (Image Generator)"

3️⃣ Create a Virtual Environment

python -m venv venv

4️⃣ Activate the Virtual Environment

Windows PowerShell

.\venv\Scripts\Activate.ps1

Windows Command Prompt

venv\Scripts\activate

Linux / macOS

source venv/bin/activate

5️⃣ Install Dependencies

pip install -r requirements.txt

6️⃣ Configure Environment Variables

Some projects require API keys.

Create a .env file using the provided .env.example:

copy .env.example .env

Example:

API_KEY=your_api_key_here

For the Image Generator project:

CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
CLOUDFLARE_MODEL=@cf/stabilityai/stable-diffusion-xl-base-1.0

REQUEST_TIMEOUT=120
MAX_RETRIES=3
MAX_CONCURRENT_GENERATIONS=2
DEBUG_MODE=false

▶️ Running the Projects

Each project may have its own startup command.

For Streamlit-based applications:

streamlit run streamlit_app.py

Or:

python run.py

Follow the instructions inside each project's README.

🧪 Running Tests

Some projects may include automated tests.

python -m pytest -v

Tests should not require real API credentials.

🔐 Security

Never upload API keys or secrets to GitHub.

Make sure your .gitignore contains:

.env
venv/
__pycache__/
*.pyc

Do not commit:

API keys

API tokens

Passwords

Secret configuration files

Personal credentials

🐛 Debugging

If a project encounters an error, check:

Python version

Virtual environment activation

Installed dependencies

Environment variables

API credentials

Internet connection

Restart the application after changing environment variables.

📁 Project Documentation

Each task contains its own README:

Project

Documentation

🤖 AI ChatBot

Task 1 (AI ChatBot)/README.md

🎭 Tone Transformer

Task 2 (Tone Transformer)/README.md

🖼️ Image Generator

Task 3 (Image Generator)/README.md

🎯 Learning Objectives

These internship projects focus on gaining practical experience with:

Artificial Intelligence application development

Generative AI

Large Language Models

Prompt Engineering

Natural Language Processing

AI API integration

REST APIs

Multimodal AI

Text transformation

Image generation

Error handling and debugging

Git and GitHub

👨‍💻 Author

Aman Kumar

B.Tech Computer Science Engineering
Specialization: Artificial Intelligence and Machine Learning

GitHub: https://github.com/amankumrjha06

📚 About This Repository

This repository serves as a collection of projects developed during my internship at Decode Labs.

Each project explores a different area of Artificial Intelligence and Generative AI development and is independently documented.

⭐ Explore the Projects

🤖 Task 1: AI ChatBot

🎭 Task 2: Tone Transformer

🖼️ Task 3: Multimodal Image Generation Studio

Happy coding! 🚀
