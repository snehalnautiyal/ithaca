"""Memory hooks: extraction after reply, injection before reply."""
import json
from typing import AsyncGenerator

from services.memory import add_memory, search_memories
from src.llm_core.provider import get_provider

EXTRACTION_PROMPT = """Extract facts worth remembering about the user from this exchange.
Return a JSON array of short factual strings. Return [] if nothing notable.
Only extract clear preferences, facts about the user, or important context.
Do NOT extract generic conversation or greetings."""

MEMORY_CONTEXT_TEMPLATE = """Relevant memories about the user:
{memories}
Use these to personalize your response, but don't explicitly mention you're reading memories unless asked."""


async def extract_memories(user_msg: str, assistant_msg: str, session_id: str) -> list[str]:
    """Extract memorable facts from an exchange using the LLM."""
    try:
        provider = get_provider()
        messages = [
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": f"User said: {user_msg}\nAssistant replied: {assistant_msg}"},
        ]
        full_response = ""
        async for token in provider.stream_chat(messages):
            full_response += token

        # Parse JSON array from response
        # Try to find JSON array in the response
        start = full_response.find("[")
        end = full_response.rfind("]") + 1
        if start != -1 and end > start:
            facts = json.loads(full_response[start:end])
            if isinstance(facts, list):
                stored = []
                for fact in facts:
                    if isinstance(fact, str) and len(fact.strip()) > 5:
                        add_memory(fact.strip(), source_session=session_id, mem_type="extracted")
                        stored.append(fact.strip())
                return stored
    except Exception:
        pass
    return []


def inject_memories(user_message: str, history: list[dict]) -> list[dict]:
    """Retrieve relevant memories and inject into the conversation context."""
    memories = search_memories(user_message, n_results=5)
    if not memories:
        return history

    # Filter to reasonably relevant memories (distance < 1.8)
    relevant = [m for m in memories if m.get("distance", 2) < 1.8]
    if not relevant:
        return history

    memory_text = "\n".join(f"- {m['content']}" for m in relevant)
    system_msg = {"role": "system", "content": MEMORY_CONTEXT_TEMPLATE.format(memories=memory_text)}

    # Prepend system message with memories
    if history and history[0]["role"] == "system":
        history[0]["content"] += "\n\n" + system_msg["content"]
    else:
        history = [system_msg] + history

    return history
