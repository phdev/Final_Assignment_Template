from __future__ import annotations

import os


def langsmith_metadata() -> dict[str, str]:
    """
    Provide helpful metadata keys commonly used for LangSmith filtering.

    LangSmith tracing itself is enabled via env:
    - LANGCHAIN_TRACING_V2=true
    - LANGCHAIN_API_KEY=...
    - LANGCHAIN_PROJECT=...
    """
    md: dict[str, str] = {}
    project = os.getenv("LANGCHAIN_PROJECT")
    if project:
        md["langsmith_project"] = project
    return md

