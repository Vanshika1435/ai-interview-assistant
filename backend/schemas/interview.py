from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class StartSessionRequest(BaseModel):
    interview_type: str
    topic: Optional[str] = None
    resume_skills: Optional[List[str]] = []
    resume_level: Optional[str] = None          # ← was missing


class MessageRequest(BaseModel):
    session_id: int
    user_answer: str


class MessageResponse(BaseModel):
    role: str
    content: str
    score: Optional[float] = None
    feedback: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    interview_type: str
    topic: Optional[str]
    total_score: float
    total_questions: int
    started_at: datetime

    class Config:
        from_attributes = True


class SessionDetailResponse(BaseModel):
    session: SessionResponse
    messages: List[MessageResponse]