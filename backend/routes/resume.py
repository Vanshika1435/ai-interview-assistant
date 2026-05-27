from fastapi import APIRouter, Depends, Header, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
import PyPDF2
import io

from backend.database import get_db
from backend.services.auth_service import get_current_user
from backend.services.ai_service import analyze_resume   # ← use the structured parser

router = APIRouter(prefix="/resume", tags=["Resume"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token missing")
    return authorization.split(" ")[1]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception:
        return ""


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    user = get_current_user(token, db)

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    contents = await file.read()

    # Save file
    file_path = f"{UPLOAD_DIR}/resume_{user.id}.pdf"
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text
    resume_text = extract_text_from_pdf(contents)

    if not resume_text:
        return {"message": "Resume uploaded but could not extract text", "analysis": None}

    # Use the structured analyzer — returns dict with skills, experience_level, etc.
    analysis = analyze_resume(resume_text)

    return {
        "message": "Resume uploaded and analyzed successfully!",
        "filename": file.filename,
        "analysis": analysis        # ← now a proper dict, not a raw string
    }