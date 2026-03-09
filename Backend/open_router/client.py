"""Open Router API client - single-model completion."""

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
          - "usage": optional dict with input_tokens, output_tokens (if present)
          - "model": model_id used
        On error, "text" may be empty and "error" will contain the error message.
    """
    key = (api_key or OPENROUTER_API_KEY).strip()
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

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
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
            "error": err_msg,
        }

    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = message.get("content") or ""
    usage = data.get("usage")

    return {
        "text": content,
        "usage": usage,
        "model": data.get("model", model_id),
        "error": None,
    }
