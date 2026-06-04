from fastapi import APIRouter
from pydantic import BaseModel

from src.llm_core.provider import LLMProvider
from src.llm_core.settings import load_settings, save_settings

router = APIRouter(prefix="/api/models", tags=["models"])


class SettingsUpdate(BaseModel):
    providers: list[dict] | None = None
    active_provider: str | None = None
    active_model: str | None = None


@router.get("/settings")
def get_settings():
    return load_settings()


@router.put("/settings")
def update_settings(body: SettingsUpdate):
    current = load_settings()
    if body.providers is not None:
        current["providers"] = body.providers
    if body.active_provider is not None:
        current["active_provider"] = body.active_provider
    if body.active_model is not None:
        current["active_model"] = body.active_model
    save_settings(current)
    return current


@router.get("")
async def list_models():
    s = load_settings()
    active = s.get("active_provider")
    for p in s.get("providers", []):
        if p["name"] == active:
            provider = LLMProvider(name=p["name"], base_url=p["base_url"], api_key=p.get("api_key"))
            models = await provider.list_models()
            return {"provider": active, "models": models, "active_model": s.get("active_model")}
    return {"provider": None, "models": [], "active_model": None}
