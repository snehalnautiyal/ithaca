import json
from typing import AsyncGenerator

import httpx

from src.llm_core.settings import get_active_model, get_active_provider


class LLMProvider:
    def __init__(self, name: str, base_url: str, api_key: str | None = None):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def stream_chat(
        self, messages: list[dict], model: str | None = None
    ) -> AsyncGenerator[str, None]:
        model = model or get_active_model()
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"model": model, "messages": messages, "stream": True}

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    raise RuntimeError(f"Provider error ({resp.status_code}): {body.decode()}")
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        return
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    async def list_models(self) -> list[str]:
        url = f"{self.base_url}/models"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        return []


def get_provider() -> LLMProvider:
    cfg = get_active_provider()
    if not cfg:
        raise RuntimeError("No active provider configured")
    return LLMProvider(
        name=cfg["name"],
        base_url=cfg["base_url"],
        api_key=cfg.get("api_key"),
    )
