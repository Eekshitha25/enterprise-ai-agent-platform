"""
Supervisor node: a routing LLM call that reads the conversation and decides
which specialist agent should handle the next step, or whether to finish.
"""
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.state import AgentState
from app.agents.llm import get_chat_model

SUPERVISOR_PROMPT = """You are the routing supervisor for an enterprise AI agent \
platform. Given the conversation so far, decide which specialist should act next:

- "research": for questions that require searching internal company documents,
  policies, wikis, or general knowledge-base lookups.
- "finance": for questions about billing, AWS costs, invoices, spend anomalies,
  or cloud usage.
- "FINISH": once enough information has been gathered to give the user a
  complete, well-cited answer.

Respond with exactly one word: research, finance, or FINISH."""

ROUTES = {"research", "finance", "finish"}


def supervisor_node(state: AgentState) -> dict:
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [SystemMessage(content=SUPERVISOR_PROMPT), *state["messages"]]
    )
    chain = prompt | llm | StrOutputParser()
    decision = chain.invoke({}).strip().lower()

    route = decision if decision in ROUTES else "finish"
    trace_entry = {"agent": "supervisor", "action": "route", "detail": route}

    return {
        "next_agent": "FINISH" if route == "finish" else route,
        "trace": state.get("trace", []) + [trace_entry],
    }
