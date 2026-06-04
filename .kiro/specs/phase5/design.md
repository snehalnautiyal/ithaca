# Phase 5 Design — Autonomous Agent

## Architecture

```
src/agent_tools/
├── __init__.py
├── registry.py       # Tool registry, dispatch
├── web_search.py     # SearXNG query
├── file_ops.py       # file_read, file_write (sandboxed to data/)
├── shell.py          # shell_exec (admin + confirm)
└── memory_tools.py   # memory_read, memory_write

src/agent_loop/
├── __init__.py
└── loop.py           # Plan-execute loop, yields SSE events

routes/agent.py       # POST /api/agent (SSE stream)
```

## Tool schema
Each tool is a dict:
```python
{
  "name": "web_search",
  "description": "Search the web via SearXNG",
  "parameters": {"query": "string"},
  "requires_confirm": False,
  "admin_only": False,
}
```

## Agent loop logic
1. Send user task + tool descriptions to LLM
2. LLM returns either a tool_call JSON or a final answer
3. If tool_call: dispatch tool, collect result, add to context, loop
4. If final answer or max iterations: stop
5. Each step yields an SSE event

## SSE events
```
event: thinking
data: {"content": "I need to search for..."}

event: tool_call
data: {"tool": "web_search", "args": {"query": "..."}, "requires_confirm": false}

event: tool_result
data: {"tool": "web_search", "result": "..."}

event: answer
data: {"content": "Here's what I found..."}

event: error
data: {"detail": "Max iterations reached"}

event: confirm_required
data: {"tool": "shell_exec", "args": {"command": "ls"}, "step": 3}
```

## Confirmation flow
- When a tool requires confirmation, yield `confirm_required` event and pause.
- Frontend shows a confirm/deny dialog.
- User responds via POST `/api/agent/confirm` with `{confirmed: bool, step: N}`.
- For simplicity in v1: tools requiring confirmation are auto-denied unless the request includes `confirmed_tools: ["shell_exec", "file_write"]`.

## API
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/agent | Start agent task (SSE stream). Body: `{task, confirmed_tools?: []}` |
