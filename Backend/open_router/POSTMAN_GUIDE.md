# Testing the Open Router Backend with Postman

This guide shows how to run the FastAPI backend and test it with Postman.

---

## 1. Start the backend

From the **Backend** directory (so `open_router` is importable):

```powershell
cd D:\RGC\momento\Backend
pip install -r open_router/requirements.txt
$env:OPENROUTER_API_KEY = "your-key-here"   # or use .env in open_router/
uvicorn open_router.app:app --reload --host 0.0.0.0 --port 8000
```

- **Base URL:** `http://localhost:8000`
- **Docs (Swagger):** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc  

Leave this terminal running while you test.

---

## 2. Postman setup

1. Open **Postman**.
2. Create a new **Collection** (e.g. "Open Router Backend").
3. Set **Collection variable** (optional):  
   - Variable: `base_url`  
   - Value: `http://localhost:8000`  
   So you can use `{{base_url}}` in requests.

---

## 3. Health check

**Request:** `GET {{base_url}}/` or `GET http://localhost:8000/`

- **Headers:** none required.
- **Expected (200):** JSON with `"status": "ok"` and list of endpoints.

---

## 4. List default models

**Request:** `GET {{base_url}}/models` or `GET http://localhost:8000/models`

- **Expected (200):** JSON with `default_model_ids` and `display_names`.

---

## 5. Generic chat (POST /chat)

Sends your prompt to all default models (or the ones you specify). Optional system prompt.

**Request:** `POST {{base_url}}/chat` or `POST http://localhost:8000/chat`

**Headers:**

| Key           | Value            |
|---------------|------------------|
| Content-Type  | application/json |

**Body (raw JSON):**

**Example 1 – minimal (all 5 models, no system prompt):**
```json
{
  "prompt": "What are your opening hours?"
}
```

**Example 2 – with system prompt and specific models:**
```json
{
  "prompt": "How do I reset my password?",
  "system_prompt": "You are a helpful assistant. Answer in one short paragraph.",
  "model_ids": ["openai/gpt-oss-20b:free", "meta-llama/llama-3.3-70b-instruct:free"]
}
```

**Expected (200):**
```json
{
  "responses": {
    "openai/gpt-oss-20b:free": "Our opening hours are...",
    "meta-llama/llama-3.3-70b-instruct:free": "...",
    ...
  }
}
```

If a model errors, its value in `responses` will be an error message string.

---

## 6. Support / onboarding (POST /support)

Uses built-in system prompts for **customer_support** or **onboarding**.

**Request:** `POST {{base_url}}/support` or `POST http://localhost:8000/support`

**Headers:**

| Key           | Value            |
|---------------|------------------|
| Content-Type  | application/json |

**Body (raw JSON):**

**Example 1 – customer support (default):**
```json
{
  "prompt": "I can't log in. What should I do?",
  "mode": "customer_support"
}
```

**Example 2 – onboarding:**
```json
{
  "prompt": "How do I set up my profile?",
  "mode": "onboarding"
}
```

**Example 3 – onboarding with specific models:**
```json
{
  "prompt": "What are the first steps after signup?",
  "mode": "onboarding",
  "model_ids": ["google/gemma-3-27b-it:free", "z-ai/glm-4.5-air:free"]
}
```

**Expected (200):**
```json
{
  "responses": {
    "openai/gpt-oss-20b:free": "...",
    "meta-llama/llama-3.3-70b-instruct:free": "...",
    ...
  }
}
```

**Invalid mode (400):**  
If `mode` is not `customer_support` or `onboarding`, you get `400` with a message like:  
`"mode must be 'customer_support' or 'onboarding'"`.

---

## 7. Quick reference

| Method | Endpoint   | Purpose |
|--------|------------|--------|
| GET    | /          | Health check, endpoint list |
| GET    | /models    | Default model IDs and display names |
| POST   | /chat      | Generic chat (prompt, optional system_prompt, optional model_ids) |
| POST   | /support   | Support or onboarding (prompt, mode, optional model_ids) |

**Body for POST:** always **raw** → **JSON**.

---

## 8. Troubleshooting

- **Connection refused:** Ensure the backend is running (`uvicorn ... --port 8000`) and nothing else is using port 8000.
- **500 or empty responses:** Check that `OPENROUTER_API_KEY` is set and valid. Look at the backend terminal for tracebacks.
- **Empty prompt / validation error:** Send a non-empty `prompt` string in the JSON body.
