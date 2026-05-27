from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routes import auth, interview, feedback, resume
from backend.routes.admin import router as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Interview Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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