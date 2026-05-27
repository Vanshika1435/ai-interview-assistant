from fastapi import APIRouter, Depends, Header, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.models.session import InterviewSession
from backend.models.message import Message
from backend.models.user import User
from backend.database import get_db
from backend.schemas.interview import StartSessionRequest, MessageRequest
from backend.services.interview_service import start_interview, send_answer, end_interview, get_user_sessions
from backend.services.auth_service import get_current_user, decode_access_token
from backend.services.speech_service import transcribe_audio
from pydantic import BaseModel

router = APIRouter(prefix="/interview", tags=["Interview"])


def get_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Token missing")
    return authorization.split(" ")[1]


@router.post("/start")
def start(data: StartSessionRequest, db: Session = Depends(get_db), token: str = Depends(get_token)):
    user = get_current_user(token, db)
    return start_interview(data, user, db)


@router.post("/answer")
def answer(data: MessageRequest, db: Session = Depends(get_db), token: str = Depends(get_token)):
    user = get_current_user(token, db)
    return send_answer(data, user, db)


@router.post("/end/{session_id}")
def end(session_id: int, db: Session = Depends(get_db), token: str = Depends(get_token)):
    user = get_current_user(token, db)
    return end_interview(session_id, user, db)


@router.get("/history")
def history(db: Session = Depends(get_db), token: str = Depends(get_token)):
    user = get_current_user(token, db)
    return get_user_sessions(user, db)


@router.post("/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...),
    token: str = Depends(get_token)
):
    audio_bytes = await audio.read()
    transcribed_text = transcribe_audio(audio_bytes)
    if transcribed_text.startswith("Transcription error"):
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=transcribed_text)
    return {"transcribed_text": transcribed_text}


@router.post("/voice-answer")
async def voice_answer(
    session_id: int,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    user = get_current_user(token, db)
    audio_bytes = await audio.read()
    transcribed_text = transcribe_audio(audio_bytes)
    if transcribed_text.startswith("Transcription error"):
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=transcribed_text)
    data = MessageRequest(session_id=session_id, user_answer=transcribed_text)
    result = send_answer(data, user, db)
    result["transcribed_text"] = transcribed_text
    return result


@router.get("/stats")
def get_stats(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    try:
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()

        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == user.id
        ).all()

        total_interviews = len(sessions)
        avg_score = 0.0

        if sessions:
            scores = [s.total_score for s in sessions if s.total_score and s.total_questions and s.total_questions > 0]
            if scores:
                avg_score = sum(scores) / len(scores)

        # Count only user messages (actual answers)
        session_ids = [s.id for s in sessions]
        questions_answered = 0
        if session_ids:
            questions_answered = db.query(Message).filter(
                Message.session_id.in_(session_ids),
                Message.role == "user"
            ).count()

        # Best score
        best_score = 0.0
        if sessions:
            best = max(
                (s.total_score for s in sessions if s.total_score and s.total_questions and s.total_questions > 0),
                default=0.0
            )
            best_score = round(best, 1)

        # Per-topic breakdown
        topic_stats = {}
        for s in sessions:
            key = s.topic if s.topic else s.interview_type
            if key not in topic_stats:
                topic_stats[key] = {"count": 0, "total": 0.0}
            topic_stats[key]["count"] += 1
            if s.total_score:
                topic_stats[key]["total"] += s.total_score

        topic_breakdown = [
            {
                "topic": k,
                "sessions": v["count"],
                "avg_score": round(v["total"] / v["count"], 1) if v["count"] > 0 else 0
            }
            for k, v in topic_stats.items()
        ]

        # Recent 5 session scores for chart
        recent_scores = []
        for s in sorted(sessions, key=lambda x: x.id)[-8:]:
            if s.total_score is not None and s.total_questions and s.total_questions > 0:
                recent_scores.append({
                    "label": f"{s.interview_type[:2]}-{s.id}",
                    "score": round(s.total_score, 1),
                    "type": s.interview_type,
                    "topic": s.topic or s.interview_type
                })

        return {
            "total_interviews": total_interviews,
            "average_score": round(avg_score, 1),
            "questions_answered": questions_answered,
            "best_score": best_score,
            "topic_breakdown": topic_breakdown,
            "recent_scores": recent_scores
        }

    except Exception as e:
        return {
            "total_interviews": 0,
            "average_score": 0,
            "questions_answered": 0,
            "best_score": 0,
            "topic_breakdown": [],
            "recent_scores": []
        }


@router.get("/sessions")
def get_sessions(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    try:
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()

        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == user.id
        ).order_by(InterviewSession.id.desc()).all()

        result = []
        for s in sessions:
            avg_score = 0.0
            if s.total_score and s.total_questions and s.total_questions > 0:
                avg_score = round(s.total_score, 2)

            result.append({
                "id": s.id,
                "interview_type": s.interview_type,
                "topic": s.topic,
                "average_score": avg_score,          # fixed key name
                "questions_count": s.total_questions or 0,  # fixed key name
                "created_at": str(s.started_at)       # use started_at
            })

        return result

    except Exception as e:
        return []