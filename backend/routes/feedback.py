from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.services.auth_service import get_current_user
from backend.models.session import InterviewSession
from backend.models.message import Message

router = APIRouter(prefix="/feedback", tags=["Feedback"])


def get_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Token missing")
    return authorization.split(" ")[1]


@router.get("/{session_id}")
def get_feedback(session_id: int, db: Session = Depends(get_db), token: str = Depends(get_token)):
    user = get_current_user(token, db)

    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user.id
    ).first()

    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.id.asc()).all()

    return {
        "session_id": session.id,
        "interview_type": session.interview_type,
        "topic": session.topic,
        "total_score": round(session.total_score, 2),
        "total_questions": session.total_questions,
        "started_at": session.started_at,
        "ended_at": session.ended_at,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "score": m.score,
                "feedback": m.feedback
            }
            for m in messages
        ]
    }