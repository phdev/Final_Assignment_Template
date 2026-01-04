from __future__ import annotations

import os
from functools import lru_cache


def _has_langfuse_env() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


@lru_cache(maxsize=1)
def get_langfuse_callback():
    """
    Return a Langfuse callback handler if configured, else None.

    This integrates with LangChain/LangGraph via the standard callbacks list.
    """
    if not _has_langfuse_env():
        return None

    try:
        from langfuse.callback import CallbackHandler

        # CallbackHandler reads env vars:
        # LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST (optional)
        return CallbackHandler()
    except Exception:
        return None

