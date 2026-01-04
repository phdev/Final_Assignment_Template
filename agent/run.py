from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_core.messages import AIMessage

from agent.graph import build_graph
from observability.bootstrap import get_callbacks, start_task_span


def _normalize_answer(question: str, answer: str) -> str:
    # Minimal normalization: trim and avoid surrounding quotes/markdown noise.
    out = (answer or "").strip()
    if out.startswith("```") and out.endswith("```"):
        out = out.strip("`").strip()
    return out


@lru_cache(maxsize=1)
def _graph():
    return build_graph()


def answer(question: str, *, metadata: dict[str, Any] | None = None, tags: list[str] | None = None) -> str:
    callbacks = get_callbacks()
    run_metadata = metadata or {}
    run_tags = tags or []

    graph = _graph()

    with start_task_span(question=question, metadata=run_metadata):
        result = graph.invoke(
            {"messages": [("user", question)]},
            config={
                "callbacks": callbacks,
                "metadata": run_metadata,
                "tags": run_tags,
            },
        )

    messages = result.get("messages", [])
    last_ai = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)
    text = last_ai.content if last_ai else ""
    return _normalize_answer(question, str(text))

