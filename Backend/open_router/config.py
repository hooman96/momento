"""Configuration and model registry for Open Router."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from package directory or current working directory
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)
load_dotenv()

# Open Router API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
).rstrip("/")

# Default free models (Open Router free tier)
DEFAULT_MODELS = [
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen3-coder:free",
    "z-ai/glm-4.5-air:free",
]

MODEL_DISPLAY_NAMES = {
    "openai/gpt-oss-20b:free": "OpenAI gpt-oss-20b",
    "meta-llama/llama-3.3-70b-instruct:free": "Meta Llama 3.3 70B Instruct",
    "google/gemma-3-27b-it:free": "Google Gemma 3 27B",
    "qwen/qwen3-coder:free": "Qwen Qwen3 Coder 480B A35B",
    "z-ai/glm-4.5-air:free": "Z.ai GLM 4.5 Air",
}
