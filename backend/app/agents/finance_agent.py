"""
Finance / FinOps agent: investigates billing anomalies by cross-referencing
invoice line items against cloud usage metrics, then proposes optimizations.
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from app.agents.llm import get_chat_model
from app.agents.state import AgentState
from app.tools.invoice_tool import search_invoices
from app.tools.aws_cost_tool import get_cloud_usage
from app.tools.knowledge_search_tool import search_knowledge_base

FINANCE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a FinOps agent for an enterprise AI platform. When asked "
                   "about cost changes: 1) pull the relevant invoice with search_invoices, "
                   "2) pull cloud usage deltas with get_cloud_usage for the same month, "
                   "3) optionally check search_knowledge_base for the company's cost "
                   "optimization policy, 4) explain the root cause of any anomaly and "
                   "suggest concrete optimizations. Always cite which tool/source informed "
                   "each claim."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)


def finance_node(state: AgentState) -> dict:
    llm = get_chat_model()
    tools = [search_invoices, get_cloud_usage, search_knowledge_base]
    agent = create_tool_calling_agent(llm, tools, FINANCE_PROMPT)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    last_user_msg = state["messages"][-1].content
    result = executor.invoke({"input": last_user_msg, "chat_history": state["messages"][:-1]})

    trace = state.get("trace", [])
    citations = state.get("citations", [])
    for step in result.get("intermediate_steps", []):
        tool_call, tool_output = step[0], step[1]
        trace.append({"agent": "finance", "action": tool_call.tool, "detail": str(tool_call.tool_input)})
        citations.append({"source": tool_call.tool, "snippet": str(tool_output)[:280]})

    from langchain_core.messages import AIMessage
    return {
        "messages": [AIMessage(content=result["output"])],
        "citations": citations,
        "trace": trace,
    }
