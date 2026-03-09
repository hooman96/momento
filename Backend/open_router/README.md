# Open Router Multi-Model Router

Python service that takes a user prompt and routes it to **3–5 AI models** via [Open Router](https://openrouter.ai) for **customer support** and **onboarding**. Use it from other Python code, from the CLI, or (optionally) via an HTTP API.

## Features

- **Multi-model routing**: Send one prompt to multiple models in one call.
- **Free models**: Default set of 5 free models (OpenAI, Meta Llama, Google Gemma, Qwen, Z.ai GLM).
- **Use-case presets**: Built-in system prompts for customer support and onboarding.
- **Integration-ready**: Import and call from the rest of the project, or run as a script.

## Quick Start

### 1. Install dependencies

From the repo root or from `backend/open_router`:

```bash
cd backend/open_router
pip install -r requirements.txt
```

### 2. Set your API key

Get an API key from [Open Router](https://openrouter.ai/keys) and set it in the environment:

```bash
# Linux/macOS
export OPENROUTER_API_KEY=your_key_here

# Windows (PowerShell)
$env:OPENROUTER_API_KEY = "your_key_here"
```

Or use a `.env` file in `backend/open_router` (do not commit it):

```
OPENROUTER_API_KEY=your_key_here
```

Copy from `.env.example` if provided.

### 3. Run the FastAPI backend (optional)

From the **Backend** directory (parent of `open_router`):

```powershell
cd path\to\momento\Backend
uvicorn open_router.app:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Swagger docs: http://localhost:8000/docs  
- **Testing with Postman:** see [POSTMAN_GUIDE.md](./POSTMAN_GUIDE.md).

### 4. Run from the command line

```bash
# From backend/open_router (after implementation)
python -m open_router.cli "How do I reset my password?"

# With mode and optional model list
python -m open_router.cli "How do I get started?" --mode onboarding --models openai/gpt-oss-20b:free,meta-llama/llama-3.3-70b-instruct:free
```

### 5. Use from Python

```python
from open_router import route_prompt, support_reply

# Route to all default models
responses = route_prompt("What are your opening hours?")
# -> {"openai/gpt-oss-20b:free": "...", "meta-llama/llama-3.3-70b-instruct:free": "...", ...}

# Customer support mode (uses support system prompt)
responses = support_reply("I can't log in.", mode="customer_support")

# Onboarding mode
responses = support_reply("How do I set up my profile?", mode="onboarding")
```

## Default models (free)

| Provider | Model | ID |
|----------|--------|----|
| OpenAI | gpt-oss-20b | `openai/gpt-oss-20b:free` |
| Meta | Llama 3.3 70B Instruct | `meta-llama/llama-3.3-70b-instruct:free` |
| Google | Gemma 3 27B | `google/gemma-3-27b-it:free` |
| Qwen | Qwen3 Coder 480B A35B | `qwen/qwen3-coder:free` |
| Z.ai | GLM 4.5 Air | `z-ai/glm-4.5-air:free` |

You can override the model list via the API or config.

## Project layout (planned)

```
backend/open_router/
├── README.md           # This file
├── REQUIREMENTS.md     # Project requirements
├── requirements.txt    # Python dependencies
├── .env.example       # Example env (no secrets)
├── __init__.py
├── config.py          # Env and model config
├── client.py          # Open Router API client
├── router.py          # Multi-model routing
├── prompts.py         # System prompts (support, onboarding)
└── cli.py             # CLI entrypoint
```

## Integration with the rest of the project

- **Same repo**: Import `open_router` from `backend/open_router` (add `backend` to `PYTHONPATH` or install as package).
- **Other services**: Call the Python functions directly, or add an HTTP layer (e.g. FastAPI) and call `POST /chat` with `prompt`, optional `mode`, optional `model_ids`.

## Documentation

- **Requirements and scope**: See [REQUIREMENTS.md](./REQUIREMENTS.md).
- **Open Router**: [API docs](https://openrouter.ai/docs), [free models](https://openrouter.ai/collections/free-models).
