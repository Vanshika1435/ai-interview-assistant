from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interview_type = Column(String(50), nullable=False)  # HR or Technical
    topic = Column(String(100), nullable=True)           # Python, DSA etc
    total_score = Column(Float, default=0.0)
    total_questions = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")