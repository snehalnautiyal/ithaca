import pytest
from src.agent_tools.registry import TOOLS, dispatch_tool, get_tool_schemas


def test_tools_registered():
    schemas = get_tool_schemas()
    names = [t["name"] for t in schemas]
    assert "web_search" in names
    assert "file_read" in names
    assert "file_write" in names
    assert "shell_exec" in names
    assert "memory_read" in names
    assert "memory_write" in names


def test_file_write_requires_confirm():
    tool = TOOLS["file_write"]
    assert tool["requires_confirm"] is True
    assert tool["admin_only"] is True


def test_shell_exec_requires_confirm():
    tool = TOOLS["shell_exec"]
    assert tool["requires_confirm"] is True
    assert tool["admin_only"] is True


@pytest.mark.anyio
async def test_dispatch_unknown_tool():
    result = await dispatch_tool("nonexistent", {})
    assert "error" in result
    assert "Unknown tool" in result["error"]


@pytest.mark.anyio
async def test_dispatch_denied_without_confirm():
    result = await dispatch_tool("shell_exec", {"command": "ls"}, confirmed_tools=[])
    assert result.get("requires_confirm") is True


@pytest.mark.anyio
async def test_dispatch_file_read(tmp_path, monkeypatch):
    # Patch sandbox
    monkeypatch.setattr("src.agent_tools.file_ops.SANDBOX", tmp_path)
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    result = await dispatch_tool("file_read", {"filepath": "test.txt"}, confirmed_tools=[])
    assert result["result"] == "hello world"


@pytest.mark.anyio
async def test_dispatch_file_write_confirmed(tmp_path, monkeypatch):
    monkeypatch.setattr("src.agent_tools.file_ops.SANDBOX", tmp_path)
    result = await dispatch_tool("file_write", {"filepath": "out.txt", "content": "data"}, confirmed_tools=["file_write"])
    assert "Written" in result["result"]
    assert (tmp_path / "out.txt").read_text() == "data"


@pytest.mark.anyio
async def test_dispatch_shell_confirmed(monkeypatch):
    result = await dispatch_tool("shell_exec", {"command": "echo hi"}, confirmed_tools=["shell_exec"])
    assert "hi" in result["result"]


def test_parse_tool_call():
    from src.agent_loop.loop import _parse_tool_call
    # Valid tool call
    result = _parse_tool_call('{"tool": "web_search", "args": {"query": "test"}}')
    assert result == {"tool": "web_search", "args": {"query": "test"}}

    # Not a tool call
    result = _parse_tool_call("Here is my answer to your question.")
    assert result is None

    # Tool call embedded in text
    result = _parse_tool_call('Let me search for that.\n{"tool": "web_search", "args": {"query": "python"}}')
    assert result["tool"] == "web_search"
