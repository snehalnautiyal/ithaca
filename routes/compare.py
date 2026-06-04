import asyncio
import random
from fastapi import APIRouter
from pydantic import BaseModel

from src.llm_core.provider import LLMProvider, get_provider
from src.llm_core.settings import load_settings

router = APIRouter(prefix="/api/compare", tags=["compare"])


class ModelSpec(BaseModel):
    provider: str
    model: str


class CompareRequest(BaseModel):
    prompt: str
    models: list[ModelSpec]


class SynthesizeRequest(BaseModel):
    prompt: str
    responses: list[str]


def _get_provider_by_name(name: str) -> LLMProvider | None:
    settings = load_settings()
    for p in settings.get("providers", []):
        if p["name"] == name:
            return LLMProvider(name=p["name"], base_url=p["base_url"], api_key=p.get("api_key"))
    return None


async def _query_model(provider: LLMProvider, model: str, prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    result = ""
    try:
        async for token in provider.stream_chat(messages, model=model):
            result += token
    except Exception as e:
        result = f"[Error: {str(e)}]"
    return result


@router.post("")
async def compare(body: CompareRequest):
    if len(body.models) < 2 or len(body.models) > 4:
        return {"error": "Provide 2-4 models"}

    # Dispatch all in parallel
    tasks = []
    model_info = []
    for spec in body.models:
        provider = _get_provider_by_name(spec.provider)
        if not provider:
            # Fallback to active provider
            provider = get_provider()
        tasks.append(_query_model(provider, spec.model, body.prompt))
        model_info.append(f"{spec.provider}/{spec.model}")

    results = await asyncio.gather(*tasks)

    # Shuffle for blind comparison
    indices = list(range(len(results)))
    random.shuffle(indices)

    responses = []
    reveal_map = {}
    for i, idx in enumerate(indices):
        label = f"Model {i + 1}"
        responses.append({"label": label, "content": results[idx]})
        reveal_map[label] = model_info[idx]

    return {"responses": responses, "reveal": reveal_map}


@router.post("/synthesize")
async def synthesize(body: SynthesizeRequest):
    provider = get_provider()
    responses_text = "\n\n".join(
        f"--- Response {i+1} ---\n{r}" for i, r in enumerate(body.responses)
    )
    messages = [
        {"role": "system", "content": "You are a synthesis expert. Merge the best parts of multiple AI responses into one optimal answer. Be concise."},
        {"role": "user", "content": f"Original prompt: {body.prompt}\n\nResponses to merge:\n{responses_text}\n\nSynthesize the best combined answer:"},
    ]
    result = ""
    async for token in provider.stream_chat(messages):
        result += token
    return {"synthesis": result}
