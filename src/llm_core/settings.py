import json
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path("data/settings.json")

DEFAULT_SETTINGS = {
    "providers": [
        {"name": "Ollama", "base_url": "http://localhost:11434/v1", "api_key": None}
    ],
    "active_provider": "Ollama",
    "active_model": "llama3.2",
}


def load_settings() -> dict[str, Any]:
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)


def save_settings(data: dict[str, Any]) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_active_provider() -> dict | None:
    s = load_settings()
    name = s.get("active_provider")
    for p in s.get("providers", []):
        if p["name"] == name:
            return p
    return None


def get_active_model() -> str:
    return load_settings().get("active_model", "llama3.2")
