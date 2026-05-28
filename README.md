# 🤖 AI Interview Assistant (A.I.I.A)

An intelligent interview preparation platform that simulates real HR and Technical interviews using AI. Built as an internship project.

---

## ✨ Features

- 🎯 **HR & Technical Interview Modes** — Behavioral questions + topic-specific technical rounds
- 🧠 **AI-Powered Evaluation** — Real-time scoring (1–10) and feedback on every answer
- 📄 **Resume Analysis** — Upload your PDF resume; AI extracts skills, experience level, and suggests interview topics
- 🎤 **Voice Input** — Record your answer, get it transcribed, edit if needed, then send
- 📊 **Performance Dashboard** — Track total interviews, average score, questions answered
- 🕓 **Interview History** — Review all past sessions with scores
- 🌓 **Dark / Light Theme** — Toggle anytime
- 🔐 **JWT Authentication** — Secure register/login flow

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + SQLAlchemy |
| AI Model | Ollama + Llama 3 (local) |
| Speech-to-Text | faster-whisper |
| Auth | JWT (python-jose) |

---

## 📁 Folder Structure

```
ai-interview-assistant/
├── backend/
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Environment settings
│   ├── database.py           # DB engine & session
│   ├── models/
│   │   ├── user.py
│   │   ├── session.py
│   │   └── message.py
│   ├── schemas/
│   │   ├── user.py
│   │   └── interview.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── interview.py
│   │   ├── feedback.py
│   │   ├── resume.py
│   │   └── admin.py
│   └── services/
│       ├── ai_service.py
│       ├── auth_service.py
│       ├── speech_service.py
│       └── interview_service.py
├── frontend/
│   ├── index.html            # Login / Register
│   ├── dashboard.html        # Main dashboard
│   ├── interview.html        # Chat interface
│   ├── landing.html          # Landing page
│   ├── admin.html            # Admin panel
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── auth.js
│       ├── dashboard.js
│       ├── interview.js
│       └── admin.js
├── uploads/                  # Resume PDFs stored here
├── .env                      # Environment variables (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- [Ollama](https://ollama.ai) installed and running
- Llama 3 model pulled

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-interview-assistant.git
cd ai-interview-assistant
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/interview_db
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
OLLAMA_BASE_URL=http://localhost:11434
```

### 5. Set up PostgreSQL database

```sql
CREATE DATABASE interview_db;
```

### 6. Pull the AI model

```bash
ollama pull llama3
```

### 7. Run the backend

```bash
uvicorn backend.main:app --reload
```

API will be live at: `https://ai-interview-assistant-backend-v5hv.onrender.com`  
Swagger docs at: `https://ai-interview-assistant-backend-v5hv.onrender.com`

### 8. Open the frontend

Just open `frontend/index.html` in your browser, or use Live Server in VS Code.

---

## 🔑 Admin Panel

Access at `frontend/admin.html`

Default credentials:
```
Email:    admin@interview.ai
Password: admin123
```

---

## 📦 Requirements

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]==4.0.1
python-multipart
pydantic
pydantic-settings
python-dotenv
httpx
pydantic[email]
faster-whisper
PyPDF2
```

---

## 🚀 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user info |
| POST | `/interview/start` | Start a new interview session |
| POST | `/interview/answer` | Submit an answer |
| POST | `/interview/end/{id}` | End interview session |
| GET | `/interview/sessions` | Get all sessions |
| GET | `/interview/stats` | Get performance stats |
| POST | `/resume/upload` | Upload and analyze resume PDF |
| GET | `/feedback/{session_id}` | Get detailed session feedback |

---

## 👨‍💻 Author

Built with ❤️ as an internship project.

---

## 📄 License

MIT License