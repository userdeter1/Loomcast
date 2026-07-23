from typing import Any

import httpx

from loomcast.common.exceptions import RuntimeExecutionError


def send_openai_compat_chat(
    base_url: str,
    model: str,
    messages: list[dict[str, Any]],
    timeout: float,
    runtime_name: str = "OpenAI-compatible",
) -> str:
    """Send a chat completion request to an OpenAI-compatible /v1/chat/completions endpoint."""
    try:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        response = httpx.post(
            f"{base_url.rstrip('/')}/v1/chat/completions",
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeExecutionError(
                f"Empty choices returned from {runtime_name} chat API."
            )
        return choices[0].get("message", {}).get("content", "")
    except httpx.HTTPError as e:
        raise RuntimeExecutionError(
            f"{runtime_name} chat execution failed for model '{model}': {e}"
        ) from e
