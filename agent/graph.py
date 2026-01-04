from __future__ import annotations

from langchain_core.messages import SystemMessage

from agent.llm import build_llm
from agent.prompts import SYSTEM_PROMPT
from agent.tools import calculator, now_utc


def build_graph():
    """
    Returns a LangGraph runnable.

    We use the prebuilt ReAct-style agent for reliability and tool calling.
    """
    from langgraph.prebuilt import create_react_agent

    llm = build_llm()
    tools = [calculator, now_utc]
    system = SystemMessage(content=SYSTEM_PROMPT)

    return create_react_agent(model=llm, tools=tools, prompt=system)

