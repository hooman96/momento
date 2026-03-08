# Open Router Multi-Model Router — Project Requirements

## 1. Overview

### 1.1 Purpose
Python service that accepts user prompts and routes them to multiple AI models via [Open Router](https://openrouter.ai), for **customer support** and **onboarding** use cases. Responses from 3–5 models can be used for comparison, fallback, or ensemble workflows.

### 1.2 Scope (Initial Start)
- **In scope**: Open Router client, model registry, prompt routing, preset system prompts for support/onboarding, CLI and/or HTTP API, integration-ready Python package.
- **Out of scope (initial)**: Frontend UI changes, persistence of conversations, authentication, billing/usage tracking.

---

## 2. Functional Requirements

### 2.1 Core Routing
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Accept a user prompt (string) as input. | Must |
| FR-2 | Support routing to **3–5 models** per request (configurable). | Must |
| FR-3 | Call Open Router API (`POST /api/v1/chat/completions`) for each selected model. | Must |
| FR-4 | Return responses keyed by model ID (e.g. `{ "model_id": "response_text" }`). | Must |
| FR-5 | Support optional system prompt per request (e.g. for customer_support vs onboarding). | Must |

### 2.2 Models (Free Tier)
Use free models from [Open Router Free Models](https://openrouter.ai/collections/free-models):

| Provider | Model | Open Router Model ID |
|----------|--------|----------------------|
| OpenAI | gpt-oss-20b (free) | `openai/gpt-oss-20b:free` |
| Meta | Llama 3.3 70B Instruct (free) | `meta-llama/llama-3.3-70b-instruct:free` |
| Google | Gemma 3 27B (free) | `google/gemma-3-27b-it:free` |
| Qwen | Qwen3 Coder 480B A35B (free) | `qwen/qwen3-coder:free` |
| Z.ai | GLM 4.5 Air (free) | `z-ai/glm-4.5-air:free` |

- Default behavior: route to all 5 models unless a subset is specified.
- Model list must be configurable (e.g. via config file or env).

### 2.3 Use Cases
| ID | Use Case | Description |
|----|----------|-------------|
| UC-1 | **Customer support** | Preset system prompt instructing the model to answer support questions helpfully and concisely. |
| UC-2 | **Onboarding** | Preset system prompt for guiding new users (product/feature explanation, next steps). |

### 2.4 Interfaces
| ID | Interface | Description |
|----|-----------|-------------|
| IF-1 | **Python API** | Functions callable from other Python code (e.g. `route_prompt()`, `support_reply()`). | Must |
| IF-2 | **CLI** | Script runnable as `python -m open_router.cli "user question"` with optional `--mode`, `--models`. | Should |
| IF-3 | **HTTP API** (optional) | REST endpoint (e.g. `POST /chat`) for frontend or other services. | Could |

---

## 3. Non-Functional Requirements

### 3.1 Technology
- **Language**: Python 3.x (compatible with project integration).
- **Dependencies**: Minimal; e.g. `requests` or `httpx`, `python-dotenv`. No framework required for core client; FastAPI/Flask only if HTTP API is added.

### 3.2 Configuration
- **Open Router API key**: Loaded from environment (e.g. `OPENROUTER_API_KEY`). Never committed.
- **Base URL**: Configurable (default `https://openrouter.ai/api/v1`).
- **Model list**: Default to the 5 free models above; overridable via config or function arguments.

### 3.3 Error Handling
- Network and API errors per model must not fail the entire request; return partial results and errors keyed by model (e.g. `{"model_id": "error message"}` or structured error object).
- Log errors for debugging; do not expose raw API keys in logs.

### 3.4 Security
- API key only in environment or secret store, not in code or config files in repo.
- `.env` in `.gitignore`; provide `.env.example` with placeholder keys.

---

## 4. Deliverables

| # | Deliverable | Format |
|---|-------------|--------|
| 1 | Project requirements | This document |
| 2 | Python package layout | `backend/open_router/` with `__init__.py`, modules |
| 3 | Dependency list | `requirements.txt` |
| 4 | Config / env loading | Module + `.env.example` |
| 5 | Open Router client (single-model) | Function `complete(prompt, model_id, system_prompt?)` |
| 6 | Model registry | Constants/config for 5 free model IDs and display names |
| 7 | Router (multi-model) | Function `route_prompt(prompt, model_ids?, system_prompt?)` |
| 8 | Preset system prompts | Customer support + onboarding |
| 9 | High-level API | e.g. `support_reply(prompt, mode, model_ids?)` |
| 10 | CLI | `python -m open_router.cli` with args |
| 11 | README | Setup, usage, integration notes |

---

## 5. Acceptance Criteria

- Given a valid `OPENROUTER_API_KEY`, the service can send one prompt to the 5 free models and return 5 response texts (or errors for failed calls).
- Customer support and onboarding modes use distinct system prompts and the same routing mechanism.
- Another part of the project can import the Python package and call the routing API without running a separate server (unless HTTP is added).
- Documentation (README) explains how to set the API key, install dependencies, and run the CLI.

---

## 6. References

- [Open Router API](https://openrouter.ai/docs)
- [Open Router Free Models](https://openrouter.ai/collections/free-models)
