from datetime import datetime

from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Conversation, Message
from app.db.schemas import ChatRequest, ChatResponse, Citation, AgentTraceStep
from app.agents.graph import get_agent_graph

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # Get or create conversation
    if request.conversation_id:
        conversation = db.get(Conversation, request.conversation_id)
    else:
        conversation = Conversation(title=request.message[:60])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Persist the user message
    user_msg = Message(conversation_id=conversation.id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    # Run the multi-agent graph
    graph = get_agent_graph()
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=request.message)],
            "citations": [],
            "trace": [],
            "next_agent": "",
        }
    )

    final_answer = result["messages"][-1].content
    citations = result.get("citations", [])
    trace = result.get("trace", [])

    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=final_answer,
        agent_trace=trace,
        citations=citations,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(
        conversation_id=str(conversation.id),
        message_id=str(assistant_msg.id),
        answer=final_answer,
        citations=[Citation(**c) for c in citations],
        agent_trace=[AgentTraceStep(**t) for t in trace],
        created_at=assistant_msg.created_at or datetime.utcnow(),
    )


@router.get("/{conversation_id}/history")
def get_history(conversation_id: str, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "citations": m.citations,
            "agent_trace": m.agent_trace,
            "created_at": m.created_at,
        }
        for m in messages
    ]
