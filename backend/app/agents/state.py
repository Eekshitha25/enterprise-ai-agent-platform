"""
Shared state object passed between nodes in the LangGraph agent graph.
"""
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # Full chat history using LangGraph's built-in message reducer
    messages: Annotated[list, add_messages]
    # Which specialist agent the supervisor routed to ("research" | "finance" | "END")
    next_agent: str
    # Accumulated citations across all tool calls in this turn
    citations: list[dict]
    # Ordered trace of which agent/tool ran and what it did, for UI display
    trace: list[dict]
