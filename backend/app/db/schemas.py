from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class Citation(BaseModel):
    source: str
    snippet: str
    score: Optional[float] = None


class AgentTraceStep(BaseModel):
    agent: str
    action: str
    detail: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    citations: list[Citation] = []
    agent_trace: list[AgentTraceStep] = []
    created_at: datetime


class DocumentOut(BaseModel):
    id: str
    filename: str
    source_type: str
    status: str
    chunk_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
