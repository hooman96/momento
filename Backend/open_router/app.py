"""FastAPI backend service for Open Router multi-model routing."""

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .router import route_prompt, support_reply
from .config import DEFAULT_MODELS, MODEL_DISPLAY_NAMES

app = FastAPI(
    title="Open Router Backend",
    description="Multi-model routing for customer support and onboarding.",
    version="0.1.0",
)

# Allow browser/frontend calls from any origin (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response models ---

class ChatRequest(BaseModel):
    """Generic chat: one prompt, optional system prompt, optional model list."""
    prompt: str = Field(..., min_length=1, description="User message")
    system_prompt: Optional[str] = Field(None, description="Optional system instruction")
    model_ids: Optional[List[str]] = Field(None, description="Model IDs; default = all 5 free models")


class SupportRequest(BaseModel):
    """Support/onboarding: prompt + mode."""
    prompt: str = Field(..., min_length=1, description="User message")
    mode: str = Field(
        "customer_support",
        description="customer_support | onboarding",
    )
    model_ids: Optional[List[str]] = Field(None, description="Model IDs; default = all 5 free models")


class TokenUsage(BaseModel):
    """Token counts returned by the model."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ModelResult(BaseModel):
    """Full result for a single model completion."""
    text: str = ""
    usage: Optional[TokenUsage] = None
    elapsed_ms: int = 0
    tokens_per_second: Optional[float] = None
    error: Optional[str] = None


class ChatResponse(BaseModel):
    """Responses keyed by model_id with text, usage, and speed metrics."""
    responses: dict = Field(..., description="model_id -> ModelResult")


# --- Endpoints ---

@app.get("/")
def root():
    """Health check and service info."""
    return {
        "service": "Open Router Backend",
        "status": "ok",
        "endpoints": {
            "POST /chat": "Route prompt to models (optional system_prompt, model_ids)",
            "POST /support": "Support/onboarding reply (prompt, mode: customer_support|onboarding)",
            "GET /models": "List default model IDs and display names",
        },
    }


@app.get("/models")
def list_models():
    """List default models and their display names."""
    return {
        "default_model_ids": DEFAULT_MODELS,
        "display_names": MODEL_DISPLAY_NAMES,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Send a prompt to one or more models. Optional system prompt and model list."""
    try:
        responses = route_prompt(
            request.prompt,
            model_ids=request.model_ids,
            system_prompt=request.system_prompt,
        )
        return ChatResponse(responses=responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/support", response_model=ChatResponse)
def support(request: SupportRequest):
    """Send a support or onboarding prompt. Uses preset system prompts."""
    if request.mode not in ("customer_support", "onboarding"):
        raise HTTPException(
            status_code=400,
            detail="mode must be 'customer_support' or 'onboarding'",
        )
    try:
        responses = support_reply(
            request.prompt,
            mode=request.mode,
            model_ids=request.model_ids,
        )
        return ChatResponse(responses=responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "open_router.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
