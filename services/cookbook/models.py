"""Model catalog, fit scoring, download and serve management via Ollama."""
import subprocess
import json
from dataclasses import dataclass
from services.cookbook.hardware import detect_hardware, HardwareInfo

# Model catalog: popular GGUF models with their approximate RAM requirements
CATALOG = [
    {"id": "llama3.2", "name": "Llama 3.2 (3B)", "params": "3B", "ram_gb": 2.5, "quant": "Q4_K_M"},
    {"id": "llama3.2:1b", "name": "Llama 3.2 (1B)", "params": "1B", "ram_gb": 1.2, "quant": "Q4_K_M"},
    {"id": "mistral", "name": "Mistral 7B", "params": "7B", "ram_gb": 5.0, "quant": "Q4_K_M"},
    {"id": "gemma2:2b", "name": "Gemma 2 (2B)", "params": "2B", "ram_gb": 2.0, "quant": "Q4_K_M"},
    {"id": "gemma2", "name": "Gemma 2 (9B)", "params": "9B", "ram_gb": 6.5, "quant": "Q4_K_M"},
    {"id": "phi3", "name": "Phi-3 Mini (3.8B)", "params": "3.8B", "ram_gb": 3.0, "quant": "Q4_K_M"},
    {"id": "qwen2.5:7b", "name": "Qwen 2.5 (7B)", "params": "7B", "ram_gb": 5.0, "quant": "Q4_K_M"},
    {"id": "qwen2.5:14b", "name": "Qwen 2.5 (14B)", "params": "14B", "ram_gb": 9.5, "quant": "Q4_K_M"},
    {"id": "codellama", "name": "Code Llama (7B)", "params": "7B", "ram_gb": 5.0, "quant": "Q4_K_M"},
    {"id": "deepseek-coder-v2:16b", "name": "DeepSeek Coder V2 (16B)", "params": "16B", "ram_gb": 11.0, "quant": "Q4_K_M"},
    {"id": "llama3.1:8b", "name": "Llama 3.1 (8B)", "params": "8B", "ram_gb": 5.5, "quant": "Q4_K_M"},
    {"id": "llama3.1:70b", "name": "Llama 3.1 (70B)", "params": "70B", "ram_gb": 42.0, "quant": "Q4_K_M"},
]


@dataclass
class FitScore:
    model_id: str
    score: str  # "excellent", "good", "tight", "too_large"
    ram_needed: float
    ram_available: float
    can_run: bool


def compute_fit(hw: HardwareInfo = None) -> list[dict]:
    """Score each catalog model against available hardware."""
    if hw is None:
        hw = detect_hardware()
    available = hw.ram_gb * 0.75  # leave 25% for OS/other apps

    results = []
    for m in CATALOG:
        needed = m["ram_gb"]
        if needed <= available * 0.5:
            score = "excellent"
        elif needed <= available * 0.75:
            score = "good"
        elif needed <= available:
            score = "tight"
        else:
            score = "too_large"

        results.append({
            **m,
            "score": score,
            "can_run": score != "too_large",
            "ram_needed_gb": needed,
            "ram_available_gb": round(available, 1),
        })
    return results


def list_installed_models() -> list[dict]:
    """List models currently available in Ollama."""
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, timeout=10)
        models = []
        for line in out.strip().split("\n")[1:]:  # skip header
            parts = line.split()
            if parts:
                models.append({"id": parts[0], "size": parts[2] if len(parts) > 2 else "?"})
        return models
    except Exception:
        return []


def pull_model(model_id: str) -> subprocess.Popen:
    """Start pulling a model via Ollama (returns immediately, runs in background)."""
    return subprocess.Popen(
        ["ollama", "pull", model_id],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def delete_model(model_id: str) -> bool:
    """Delete a model from Ollama."""
    try:
        subprocess.check_call(["ollama", "rm", model_id], timeout=10)
        return True
    except Exception:
        return False
