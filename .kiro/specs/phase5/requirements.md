# Phase 5 Requirements — Autonomous Agent

## REQ-1: Agent loop
- WHEN a user submits a task to the agent, THEN it plans steps and executes tools iteratively until done.
- The agent MUST stream its reasoning, tool calls, and results back to the UI via SSE.
- Maximum iterations: 10 (configurable). If exceeded, stop and report.

## REQ-2: Tools
- web_search: query SearXNG, return results (title, url, snippet).
- file_read: read a file within `data/` (sandboxed).
- file_write: write a file within `data/` (requires user confirmation).
- shell_exec: run a shell command (admin-only, requires user confirmation).
- memory_read: search memories.
- memory_write: store a new memory.

## REQ-3: Safety gates
- shell_exec and file_write MUST require explicit per-run user confirmation before executing.
- Non-admin users get NO access to shell or file tools.
- The agent endpoint is admin-only.

## REQ-4: Streaming trace
- Stream each step: thinking, tool_call (name + args), tool_result, final_answer.
- Frontend shows a collapsible trace of all steps.

## REQ-5: MCP support (basic)
- Register external MCP servers from settings.
- If registered, list their tools alongside built-in tools.
