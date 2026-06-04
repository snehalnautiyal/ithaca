"""Shell execution tool — admin-only, requires confirmation."""
import asyncio
from src.agent_tools.registry import register_tool


async def shell_exec(command: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd="data",
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
    output = stdout.decode()[:5000]
    if stderr:
        output += f"\nSTDERR: {stderr.decode()[:2000]}"
    output += f"\nExit code: {proc.returncode}"
    return output


register_tool(
    name="shell_exec",
    description="Execute a shell command. Admin-only, requires confirmation. Working dir is data/.",
    parameters={"command": "string"},
    handler=shell_exec,
    requires_confirm=True,
    admin_only=True,
)
