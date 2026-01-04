from __future__ import annotations

import os


def build_llm():
    """
    Construct the chat model.

    Default is OpenAI-compatible via `langchain-openai`.
    """
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
    temperature = float(os.getenv("MODEL_TEMPERATURE", "0"))

    try:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model_name, temperature=temperature)
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Failed to initialize LLM. Ensure `langchain-openai` is installed and "
            "provider credentials (e.g. OPENAI_API_KEY) are set."
        ) from e

