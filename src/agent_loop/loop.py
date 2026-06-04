"""Agent plan-and-execute loop. Yields SSE events."""
import json
from typing import AsyncGenerator

from src.agent_tools import get_tool_schemas, dispatch_tool
from src.llm_core.provider import get_provider

MAX_ITERATIONS = 10

SYSTEM_PROMPT = """You are Ithaca Agent — an autonomous assistant that can use tools to complete tasks.

Available tools:
{tools}

To use a tool, respond with EXACTLY this JSON format (nothing else):
{{"tool": "tool_name", "args": {{"param": "value"}}}}

When you have enough information to answer, respond normally (no JSON).

Rules:
- Use tools when needed to gather information or take actions.
- Think step by step.
- When done, give a clear final answer.
- Never make up information — use tools to verify."""


def _build_system_prompt() -> str:
    tools = get_tool_schemas()
    tool_desc = "\n".join(
        f"- {t['name']}: {t['description']} | params: {json.dumps(t['parameters'])}"
        for t in tools
    )
    return SYSTEM_PROMPT.format(tools=tool_desc)


def _parse_tool_call(text: str) -> dict | None:
    text = text.strip()
    # Try to find JSON in the response
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end <= start:
        return None
    try:
        data = json.loads(text[start:end])
        if "tool" in data and "args" in data:
            return data
    except json.JSONDecodeError:
        pass
    return None


async def run_agent(task: str, confirmed_tools: list[str] = None) -> AsyncGenerator[str, None]:
    """Run the agent loop, yielding SSE-formatted events."""
    confirmed_tools = confirmed_tools or []
    system_prompt = _build_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]

    for step in range(MAX_ITERATIONS):
        # Get LLM response
        yield f"event: thinking\ndata: {json.dumps({'step': step + 1})}\n\n"

        full_response = ""
        try:
            provider = get_provider()
            async for token in provider.stream_chat(messages):
                full_response += token
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"
            return

        # Check if it's a tool call
        tool_call = _parse_tool_call(full_response)

        if tool_call:
            tool_name = tool_call["tool"]
            tool_args = tool_call["args"]

            yield f"event: tool_call\ndata: {json.dumps({'tool': tool_name, 'args': tool_args, 'step': step + 1})}\n\n"

            # Dispatch tool
            result = await dispatch_tool(tool_name, tool_args, confirmed_tools)

            if result.get("requires_confirm"):
                yield f"event: confirm_required\ndata: {json.dumps({'tool': tool_name, 'args': tool_args, 'step': step + 1})}\n\n"
                # Add denial to context and continue
                messages.append({"role": "assistant", "content": full_response})
                messages.append({"role": "user", "content": f"Tool '{tool_name}' was denied (requires confirmation). Try a different approach or answer without it."})
                continue

            result_text = result.get("result", result.get("error", "No result"))
            yield f"event: tool_result\ndata: {json.dumps({'tool': tool_name, 'result': str(result_text)[:2000], 'step': step + 1})}\n\n"

            # Add to conversation context
            messages.append({"role": "assistant", "content": full_response})
            messages.append({"role": "user", "content": f"Tool result ({tool_name}):\n{str(result_text)[:2000]}"})
        else:
            # Final answer
            yield f"event: answer\ndata: {json.dumps({'content': full_response})}\n\n"
            return

    yield f"event: error\ndata: {json.dumps({'detail': 'Max iterations reached'})}\n\n"
