from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Sequence

from observability.langfuse import get_langfuse_callback
from observability.langsmith import langsmith_metadata
from observability.otel import get_tracer, span_attributes_from


def get_callbacks() -> Sequence[Any]:
    """
    A single place to assemble callbacks for LangChain/LangGraph runs.

    - LangSmith uses env-based tracing; no callback required.
    - Langfuse is attached as a callback handler when configured.
    """
    callbacks: list[Any] = []
    lf = get_langfuse_callback()
    if lf is not None:
        callbacks.append(lf)
    return callbacks


@contextmanager
def start_task_span(*, question: str, metadata: dict[str, Any] | None = None) -> Iterator[None]:
    md = metadata or {}
    md.update(langsmith_metadata())

    tracer = get_tracer()
    attrs = span_attributes_from(md)
    attrs["app.question_length"] = len(question or "")

    with tracer.start_as_current_span("agent.task", attributes=attrs):
        yield

