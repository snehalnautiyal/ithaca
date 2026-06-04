from fastapi import APIRouter
from services.cookbook.hardware import detect_hardware
from services.cookbook.models import compute_fit, list_installed_models, pull_model, delete_model

router = APIRouter(prefix="/api/cookbook", tags=["cookbook"])


@router.get("/hardware")
def get_hardware():
    hw = detect_hardware()
    return {"cpu": hw.cpu, "cores": hw.cpu_cores, "ram_gb": round(hw.ram_gb, 1),
            "gpu": hw.gpu, "unified_memory": hw.unified_memory, "metal": hw.metal_support,
            "os": hw.os_name, "arch": hw.arch}


@router.get("/catalog")
def get_catalog():
    return compute_fit()


@router.get("/installed")
def get_installed():
    return list_installed_models()


@router.post("/pull/{model_id:path}")
def pull(model_id: str):
    pull_model(model_id)
    return {"status": "pulling", "model": model_id}


@router.delete("/models/{model_id:path}")
def delete(model_id: str):
    ok = delete_model(model_id)
    return {"deleted": ok, "model": model_id}
