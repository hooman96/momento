"""Open Router API client - single-model completion."""

import time
from typing import Optional

import requests

from .config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL


def complete(
    prompt: str,
    model_id: str,
    system_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> dict:
    """
    Send a prompt to one Open Router model and return the response.

    Args:
        prompt: User message content.
        model_id: Open Router model ID (e.g. openai/gpt-oss-20b:free).
        system_prompt: Optional system message. If None, no system message is sent.
        api_key: Override API key (default: from config).
        base_url: Override base URL (default: from config).

    Returns:
        Dict with:
          - "text": assistant reply text
          - "usage": token counts (prompt_tokens, completion_tokens, total_tokens)
          - "model": model_id used
          - "elapsed_ms": wall-clock time for the API call in milliseconds
          - "tokens_per_second": completion tokens / elapsed seconds (None if unavailable)
        On error, "text" may be empty and "error" will contain the error message.
    """
    key = (api_key or OPENROUTER_API_KEY).strip()
    if not key:
        return {
            "text": "",
            "usage": None,
            "model": model_id,
            "elapsed_ms": 0,
            "tokens_per_second": None,
            "error": "OPENROUTER_API_KEY is not set. Set it in .env or environment.",
        }
    url = (base_url or OPENROUTER_BASE_URL).rstrip("/") + "/chat/completions"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": messages,
    }

    t0 = time.perf_counter()
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        elapsed_ms = round((time.perf_counter() - t0) * 1000)
        err_msg = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                body = e.response.json()
                err_msg = body.get("error", {}).get("message", err_msg)
            except Exception:
                pass
        return {
            "text": "",
            "usage": None,
            "model": model_id,
            "elapsed_ms": elapsed_ms,
            "tokens_per_second": None,
            "error": err_msg,
        }
    elapsed_ms = round((time.perf_counter() - t0) * 1000)

    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = message.get("content") or ""
    usage = data.get("usage")

    tokens_per_second = None
    if usage and elapsed_ms > 0:
        completion_tokens = usage.get("completion_tokens", 0)
        if completion_tokens:
            tokens_per_second = round(completion_tokens / (elapsed_ms / 1000), 1)

    return {
        "text": content,
        "usage": usage,
        "model": data.get("model", model_id),
        "elapsed_ms": elapsed_ms,
        "tokens_per_second": tokens_per_second,
        "error": None,
    }
