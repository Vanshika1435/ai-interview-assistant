from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from backend.models.session import InterviewSession
from backend.models.message import Message
from backend.models.user import User
from backend.schemas.interview import StartSessionRequest, MessageRequest
from backend.services.ai_service import generate_first_question, evaluate_answer
import json


def start_interview(data: StartSessionRequest, current_user: User, db: Session) -> dict:
    session = InterviewSession(
        user_id=current_user.id,
        interview_type=data.interview_type,
        topic=data.topic
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Parse resume_skills if passed
    resume_skills = data.resume_skills or []
    resume_level = data.resume_level or None

    first_question = generate_first_question(
        data.interview_type,
        data.topic,
        resume_skills=resume_skills,
        resume_level=resume_level
    )

    ai_message = Message(
        session_id=session.id,
        role="ai",
        content=first_question
    )
    db.add(ai_message)
    db.commit()

    return {
        "session_id": session.id,
        "interview_type": session.interview_type,
        "topic": session.topic,
        "first_question": first_question
    }


def send_answer(data: MessageRequest, current_user: User, db: Session) -> dict:
    session = db.query(InterviewSession).filter(
        InterviewSession.id == data.session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    last_ai_message = db.query(Message).filter(
        Message.session_id == session.id,
        Message.role == "ai"
    ).order_by(Message.id.desc()).first()

    last_question = last_ai_message.content if last_ai_message else "General question"

    user_message = Message(
        session_id=session.id,
        role="user",
        content=data.user_answer
    )
    db.add(user_message)

    # Pass resume_skills and topic for context-aware evaluation
    resume_skills = getattr(data, "resume_skills", [])
    evaluation = evaluate_answer(
        last_question,
        data.user_answer,
        session.interview_type,
        topic=session.topic,
        resume_skills=resume_skills
    )

    user_message.score = evaluation["score"]
    user_message.feedback = evaluation["feedback"]

    session.total_questions += 1
    session.total_score = (
        (session.total_score * (session.total_questions - 1) + evaluation["score"])
        / session.total_questions
    )

    next_question = evaluation["next_question"]
    ai_message = Message(
        session_id=session.id,
        role="ai",
        content=next_question
    )
    db.add(ai_message)
    db.commit()

    return {
        "score": evaluation["score"],
        "feedback": evaluation["feedback"],
        "next_question": next_question,
        "total_score": round(session.total_score, 2)
    }


def end_interview(session_id: int, current_user: User, db: Session) -> dict:
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.ended_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Interview completed!",
        "total_questions": session.total_questions,
        "final_score": round(session.total_score, 2)
    }


def get_user_sessions(current_user: User, db: Session) -> list:
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.started_at.desc()).all()
    return sessions