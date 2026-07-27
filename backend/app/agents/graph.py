"""
Wires the supervisor + specialist agents into a LangGraph state machine.

Flow:
    START -> supervisor -> (research | finance | END)
    research -> supervisor
    finance -> supervisor
    supervisor -> END  (once it decides enough info has been gathered)

This is the "multi-agent" core of the platform: the supervisor is a router,
and each specialist is an independent tool-calling ReAct agent that can be
extended (e.g. add a "compliance" or "ops" agent) without touching the others.
"""
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.research_agent import research_node
from app.agents.finance_agent import finance_node


def route_from_supervisor(state: AgentState) -> str:
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "FINISH":
        return END
    return next_agent


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("research", research_node)
    graph.add_node("finance", finance_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {"research": "research", "finance": "finance", END: END},
    )
    graph.add_edge("research", "supervisor")
    graph.add_edge("finance", "supervisor")

    return graph.compile()


_compiled_graph = None


def get_agent_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph
