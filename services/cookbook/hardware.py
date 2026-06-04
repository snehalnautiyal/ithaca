"""Hardware detection for Apple Silicon / general systems."""
import os
import platform
import subprocess
from dataclasses import dataclass


@dataclass
class HardwareInfo:
    cpu: str
    cpu_cores: int
    ram_gb: float
    gpu: str
    unified_memory: bool
    metal_support: bool
    os_name: str
    arch: str


def detect_hardware() -> HardwareInfo:
    os_name = platform.system()
    arch = platform.machine()
    cpu = platform.processor() or "Unknown"
    cpu_cores = os.cpu_count() or 1
    ram_gb = _get_ram_gb()
    gpu = "None"
    unified_memory = False
    metal_support = False

    if os_name == "Darwin" and arch == "arm64":
        # Apple Silicon
        chip = _run_cmd("sysctl -n machdep.cpu.brand_string").strip()
        if chip:
            cpu = chip
        gpu = f"{cpu} (Metal GPU)"
        unified_memory = True
        metal_support = True
    elif os_name == "Darwin":
        gpu = _run_cmd("system_profiler SPDisplaysDataType 2>/dev/null | grep 'Chipset Model'").strip()

    return HardwareInfo(
        cpu=cpu, cpu_cores=cpu_cores, ram_gb=ram_gb,
        gpu=gpu, unified_memory=unified_memory, metal_support=metal_support,
        os_name=os_name, arch=arch,
    )


def _get_ram_gb() -> float:
    system = platform.system()
    if system == "Darwin":
        mem_bytes = _run_cmd("sysctl -n hw.memsize").strip()
        if mem_bytes.isdigit():
            return int(mem_bytes) / (1024 ** 3)
    elif system == "Linux":
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) / (1024 ** 2)
    return 0.0


def _run_cmd(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, timeout=5)
    except Exception:
        return ""
