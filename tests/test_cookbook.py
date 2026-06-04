from services.cookbook.hardware import detect_hardware
from services.cookbook.models import compute_fit, CATALOG


def test_hardware_detection():
    hw = detect_hardware()
    assert hw.cpu_cores > 0
    assert hw.ram_gb > 0
    assert hw.os_name in ("Darwin", "Linux", "Windows")


def test_fit_scoring():
    results = compute_fit()
    assert len(results) == len(CATALOG)
    for r in results:
        assert r["score"] in ("excellent", "good", "tight", "too_large")
        assert isinstance(r["can_run"], bool)


def test_small_models_can_run():
    results = compute_fit()
    # 1B model should always fit on any modern machine
    tiny = next(r for r in results if r["id"] == "llama3.2:1b")
    assert tiny["can_run"] is True
    assert tiny["score"] in ("excellent", "good")
