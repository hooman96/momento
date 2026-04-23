"""Multi-model routing: send one prompt to multiple Open Router models."""

import time
from typing import List, Optional

from .client import complete
from .config import DEFAULT_MODELS
from .prompts import SYSTEM_PROMPTS


def support_reply(
    prompt: str,
    mode: str = "customer_support",
    model_ids: Optional[List[str]] = None,
) -> dict:
    """
    Route a prompt with a preset system prompt for support or onboarding.

    Args:
        prompt: User message content.
        mode: "customer_support" or "onboarding". Chooses the system prompt.
        model_ids: Optional list of model IDs. If None, uses DEFAULT_MODELS.

    Returns:
        Same as route_prompt: dict mapping model_id -> response text or error string.
    """
    system_prompt = SYSTEM_PROMPTS.get(mode) or SYSTEM_PROMPTS["customer_support"]
    return route_prompt(prompt, model_ids=model_ids, system_prompt=system_prompt)


def route_prompt(
    prompt: str,
    model_ids: Optional[List[str]] = None,
    system_prompt: Optional[str] = None,
) -> dict:
    """
    Send a prompt to multiple Open Router models and return responses keyed by model.

    Args:
        prompt: User message content.
        model_ids: List of Open Router model IDs. If None, uses DEFAULT_MODELS (all 5 free).
        system_prompt: Optional system message applied to every model.

    Returns:
        Dict mapping model_id -> result dict with keys:
          - text: response text (str)
          - usage: {prompt_tokens, completion_tokens, total_tokens} or None
          - elapsed_ms: wall-clock time in ms
          - tokens_per_second: completion tok/s or None
          - error: error message or None
    """
    models = model_ids if model_ids is not None else DEFAULT_MODELS
    results = {}
    max_attempts = 3
    initial_backoff_s = 0.5

    for model_id in models:
        out = {}
        for attempt in range(max_attempts):
            try:
                out = complete(prompt, model_id, system_prompt=system_prompt)
                # `complete` usually reports request failures via the "error"
                # field. Retry transient failures with exponential backoff.
                if out.get("error") and attempt < max_attempts - 1:
                    time.sleep(initial_backoff_s * (2**attempt))
                    continue
                break
            except Exception as exc:
                if attempt < max_attempts - 1:
                    time.sleep(initial_backoff_s * (2**attempt))
                    continue
                out = {
                    "text": "",
                    "usage": None,
                    "elapsed_ms": 0,
                    "tokens_per_second": None,
                    "error": str(exc),
                }

        results[model_id] = {
            "text": out.get("text") or "",
            "usage": out.get("usage"),
            "elapsed_ms": out.get("elapsed_ms", 0),
            "tokens_per_second": out.get("tokens_per_second"),
            "error": out.get("error"),
        }

    return results
