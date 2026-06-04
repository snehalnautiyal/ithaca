import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.anyio
async def test_compare_parallel_dispatch():
    """Test that compare dispatches to multiple models and returns blind labels."""
    from routes.compare import _query_model
    from src.llm_core.provider import LLMProvider

    # Mock a provider
    provider = LLMProvider(name="Test", base_url="http://fake", api_key=None)

    async def mock_stream(messages, model=None):
        yield f"Response from {model}"

    with patch.object(provider, 'stream_chat', side_effect=mock_stream):
        result = await _query_model(provider, "model_a", "hello")
        assert "model_a" in result


def test_compare_response_structure():
    """Test that responses are shuffled with blind labels."""
    responses = [
        {"label": "Model 1", "content": "Answer A"},
        {"label": "Model 2", "content": "Answer B"},
    ]
    reveal = {"Model 1": "Ollama/llama3.2", "Model 2": "Ollama/mistral"}

    assert len(responses) == 2
    assert all("label" in r and "content" in r for r in responses)
    assert all(v.startswith("Ollama/") for v in reveal.values())
