"""
Research agent: answers questions by searching the internal knowledge base
(RAG over ingested PDFs/Confluence/Notion/email) and citing its sources.
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from app.agents.llm import get_chat_model
from app.agents.state import AgentState
from app.tools.knowledge_search_tool import search_knowledge_base

RESEARCH_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a research agent for an enterprise knowledge platform. "
                   "Use the search_knowledge_base tool to find relevant company "
                   "documents before answering. Always cite the source of any claim."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)


def research_node(state: AgentState) -> dict:
    llm = get_chat_model()
    tools = [search_knowledge_base]
    agent = create_tool_calling_agent(llm, tools, RESEARCH_PROMPT)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    last_user_msg = state["messages"][-1].content
    result = executor.invoke({"input": last_user_msg, "chat_history": state["messages"][:-1]})

    citations = state.get("citations", [])
    for step in result.get("intermediate_steps", []):
        tool_output = step[1]
        if isinstance(tool_output, str) and "source:" in tool_output:
            for block in tool_output.split("---"):
                if "source:" in block:
                    citations.append({"source": block.split("source:")[1].split(",")[0].strip(), "snippet": block.strip()[:280]})

    trace = state.get("trace", []) + [
        {"agent": "research", "action": "search_knowledge_base", "detail": last_user_msg}
    ]

    from langchain_core.messages import AIMessage
    return {
        "messages": [AIMessage(content=result["output"])],
        "citations": citations,
        "trace": trace,
    }
