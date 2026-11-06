# AI Interview Assistant

An AI-powered interview preparation platform designed to simulate HR and technical interviews, evaluate candidate responses, and provide actionable feedback. The application combines a web-based interface with an AI-powered backend to create an interactive interview practice experience.

## Overview

AI Interview Assistant helps candidates prepare for interviews through structured interview sessions, AI-generated questions, answer evaluation, and performance tracking.

Users can practice behavioral and technical interviews, submit answers through text or voice, analyze their resumes, and review feedback to identify areas for improvement.

## Features

- **HR and Technical Interview Modes:** Practice behavioral interviews and topic-specific technical interviews.
- **AI-Powered Question Generation:** Generate interview questions based on the selected interview type, technical topic, and extracted resume skills.
- **Answer Evaluation:** Receive AI-generated scores on a scale of 1–10, feedback, and relevant follow-up questions.
- **Voice-Based Responses:** Record spoken answers and convert audio into text using speech recognition.
- **Resume Analysis:** Upload a PDF resume to extract skills, identify experience level, and receive suggested interview topics and improvement areas.
- **Coding Practice:** Generate coding problems and receive AI-assisted evaluation of submitted solutions, including complexity and improvement suggestions.
- **Performance Dashboard:** View interview statistics and performance information.
- **Interview History:** Review previous interview sessions and their results.
- **User Authentication:** Registration and login functionality using JWT-based authentication.
- **Admin Interface:** Dedicated administrative interface.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| AI Integration | Groq API |
| AI Model | OpenAI GPT-OSS 120B (through Groq) |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT, Python-JOSE, bcrypt |
| Speech Recognition | faster-whisper |
| Resume Processing | PyPDF2 |
| API Communication | HTTPX |
| Deployment | Vercel, Render |

## System Architecture

The application follows a client-server architecture with a separate frontend and backend.

```text
                 User
                  |
                  v
          Frontend Application
          HTML / CSS / JavaScript
                  |
                  v
             FastAPI Backend
                  |
       +----------+-----------+
       |          |           |
       v          v           v
 Authentication  Interview   Resume
    Routes        Routes     Routes
       |          |           |
       +----------+-----------+
                  |
                  v
             Service Layer
       +----------+-----------+
       |          |           |
       v          v           v
    AI Service  Speech     Database
       |        Service    (PostgreSQL)
       |
       v
    Groq API
       |
       v
 AI-Generated Questions,
 Evaluation and Feedback
```

## Interview Workflow

1. The user registers or logs into the application.
2. The user selects an interview type, such as HR or Technical.
3. For technical interviews, a relevant topic can be selected.
4. The backend generates an interview question using the Groq API.
5. The user submits an answer through text or voice input.
6. For voice responses, the audio is transcribed into text using faster-whisper.
7. The answer is sent to the AI evaluation service.
8. The system generates a score, feedback, and a follow-up question.
9. Interview information and performance data are stored for tracking and review.

## Resume Analysis Workflow

1. The user uploads a PDF resume.
2. PyPDF2 extracts the text from the document.
3. The extracted information is passed to the AI service.
4. The AI analyzes skills, experience level, suggested interview topics, strengths, and improvement areas.
5. The results help personalize the interview preparation process.

## Project Structure

```text
ai-interview-assistant/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   └── services/
│       ├── ai_service.py
│       ├── auth_service.py
│       ├── speech_service.py
│       └── interview_service.py
│
├── frontend/
│   ├── index.html
│   ├── landing.html
│   ├── dashboard.html
│   ├── interview.html
│   ├── coding.html
│   ├── admin.html
│   ├── css/
│   └── js/
│
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

## Local Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Groq API key
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Vanshika1435/ai-interview-assistant.git
cd ai-interview-assistant
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/interview_db

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

GROQ_API_KEY=your_groq_api_key
```

Replace the placeholder values with your own configuration. Never commit API keys or credentials to GitHub.

### 5. Create the PostgreSQL database

Create a database named `interview_db` or update `DATABASE_URL` to match your database configuration.

### 6. Start the backend

```bash
uvicorn backend.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Run the frontend

Open the frontend entry page using a local development server, such as VS Code Live Server.

Ensure the frontend API configuration points to your running backend.

## Deployment

| Component | Platform |
|---|---|
| Frontend | Vercel |
| Backend | Render |
| AI Inference | Groq API |
| Database | PostgreSQL |

**Live Application:** https://ai-interview-assistant-wine.vercel.app/

**Backend API:** https://ai-interview-assistant-backend-jy4u.onrender.com

**API Documentation:** https://ai-interview-assistant-backend-jy4u.onrender.com/docs

The deployed backend exposes its FastAPI documentation. Full application functionality depends on valid database connectivity and the required deployment environment variables.

## Key Learning Outcomes

- Building REST APIs using FastAPI.
- Integrating external LLM APIs into an application.
- Designing a structured interview workflow.
- Working with PostgreSQL and SQLAlchemy.
- Implementing JWT-based authentication.
- Processing voice input using speech recognition.
- Extracting and analyzing resume information.
- Connecting and deploying separate frontend and backend services.

## Future Improvements

- More detailed interview performance analytics.
- Expanded coding evaluation and test-case support.
- More personalized interview recommendations.
- Enhanced speech interaction and feedback.

---

**Author:** Vanshika Sharma

**Repository:** https://github.com/Vanshika1435/ai-interview-assistant
