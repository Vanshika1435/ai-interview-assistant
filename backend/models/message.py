from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)    # 'ai' or 'user'
    content = Column(Text, nullable=False)
    score = Column(Float, nullable=True)         # score for user answers
    feedback = Column(Text, nullable=True)       # ai feedback on answer
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="messages")