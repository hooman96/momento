"""Multi-model routing: send one prompt to multiple Open Router models."""

from typing import List, Optional

from .client import complete
from .config import DEFAULT_MODELS


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
        Dict mapping model_id -> response:
          - On success: model_id -> response text (str).
          - On error: model_id -> error message (str), so callers can distinguish.
        So values are always strings (either the reply or an error message).
    """
    models = model_ids if model_ids is not None else DEFAULT_MODELS
    results = {}

    for model_id in models:
        out = complete(prompt, model_id, system_prompt=system_prompt)
        if out.get("error"):
            results[model_id] = out["error"]
        else:
            results[model_id] = out.get("text") or ""

    return results
