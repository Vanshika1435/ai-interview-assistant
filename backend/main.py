from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routes import auth, interview, feedback, resume
from backend.routes.admin import router as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Interview Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-interview-assistant-wine.vercel.app",
        "https://ai-interview-assistant.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"https://ai-interview-assistant-.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
)

app.include_router(auth.router)
app.include_router(interview.router)
app.include_router(feedback.router)
app.include_router(resume.router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"message": "AI Interview Assistant API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}