from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models.user import User
from backend.models.session import InterviewSession
from backend.models.message import Message

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_EMAIL = "admin@interview.ai"
ADMIN_PASSWORD = "admin123"


def verify_admin(email: str, password: str):
    if email != ADMIN_EMAIL or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")


@router.post("/login")
def admin_login(payload: dict):
    email = payload.get("email", "")
    password = payload.get("password", "")
    verify_admin(email, password)
    return {"success": True, "message": "Admin authenticated"}


@router.get("/stats")
def get_admin_stats(email: str, password: str, db: Session = Depends(get_db)):
    verify_admin(email, password)

    total_users = db.query(func.count(User.id)).scalar() or 0

    total_sessions = db.query(func.count(InterviewSession.id)).scalar() or 0

    # overall average score
    sessions = db.query(InterviewSession).all()

    overall_avg = 0.0

    if sessions:
        scores = []

        for s in sessions:
            if s.total_questions and s.total_questions > 0:
                avg = s.total_score / s.total_questions
                scores.append(avg)

        if scores:
            overall_avg = round(sum(scores) / len(scores), 2)

    # users list
    users = db.query(User).all()

    user_list = []

    for u in users:

        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == u.id
        ).all()

        avg_score = 0.0

        scores = []

        for s in sessions:
            if s.total_questions and s.total_questions > 0:
                scores.append(s.total_score / s.total_questions)

        if scores:
            avg_score = round(sum(scores) / len(scores), 2)

        user_list.append({
            "id": u.id,
            "name": u.full_name,
            "email": u.email,
            "joined": str(u.created_at)[:10],
            "sessions": len(sessions),
            "avg_score": avg_score
        })

    # recent sessions
    recent_sessions = db.query(InterviewSession)\
        .order_by(InterviewSession.id.desc())\
        .limit(50)\
        .all()

    session_list = []

    for s in recent_sessions:

        user = db.query(User).filter(User.id == s.user_id).first()

        avg_score = 0

        if s.total_questions and s.total_questions > 0:
            avg_score = round(s.total_score / s.total_questions, 2)

        session_list.append({
            "id": s.id,
            "user": user.email if user else "Unknown",
            "type": s.interview_type,
            "topic": s.topic,
            "questions": s.total_questions,
            "score": avg_score,
            "date": str(s.started_at)[:10]
        })

    return {
        "total_users": total_users,
        "total_sessions": total_sessions,
        "avg_score": overall_avg,
        "users": user_list,
        "sessions": session_list
    }