import httpx
from backend.config import settings

OLLAMA_OPTIONS = {
    "num_predict": 250,
    "temperature": 0.7,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
}


def ask_ollama(prompt: str) -> str:
    try:
        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": OLLAMA_OPTIONS,
            },
            timeout=60.0,
        )
        data = response.json()
        return data.get("response", "").strip()
    except httpx.TimeoutException:
        return "AI_TIMEOUT"
    except Exception as e:
        return f"AI Error: {str(e)}"


def generate_first_question(
    interview_type: str,
    topic: str = None,
    resume_skills: list = None,
    resume_level: str = None
) -> str:
    # Resume-based interview takes highest priority
    if resume_skills and len(resume_skills) > 0:
        top_skills = ", ".join(resume_skills[:3])
        level = resume_level or "Mid"
        prompt = (
            f"You are an expert technical interviewer. "
            f"The candidate is a {level}-level developer with top skills: {top_skills}. "
            f"Ask ONE targeted technical interview question specifically testing their strongest skill ({resume_skills[0]}). "
            f"The question should match their {level} experience level. "
            "Output ONLY the question. No intro, no explanation, no extra text."
        )
    elif interview_type == "HR":
        prompt = (
            "You are a professional HR interviewer conducting a behavioral interview. "
            "Ask ONE concise HR/behavioral interview question about work experience, "
            "teamwork, conflict resolution, or career goals. "
            "Output ONLY the question. No intro, no explanation."
        )
    else:
        # Technical interview — topic-specific
        t = topic if topic else "general programming"
        topic_prompts = {
            "Python": "Python programming — focus on OOP, decorators, generators, async/await, or data structures",
            "JavaScript": "JavaScript — focus on closures, event loop, promises, ES6+, or DOM manipulation",
            "DSA": "Data Structures & Algorithms — focus on arrays, trees, graphs, sorting, or dynamic programming",
            "SQL": "SQL and databases — focus on JOINs, indexes, transactions, normalization, or query optimization",
            "Machine Learning": "Machine Learning — focus on model training, overfitting, evaluation metrics, or algorithms",
            "System Design": "System Design — focus on scalability, load balancing, databases, caching, or microservices",
        }
        focus = topic_prompts.get(t, f"{t} programming concepts")
        prompt = (
            f"You are an expert technical interviewer. Topic: {focus}. "
            f"Ask ONE specific, challenging technical question about {t}. "
            "The question should test deep understanding, not just definitions. "
            "Output ONLY the question. No intro, no explanation, no extra text."
        )
    return ask_ollama(prompt)


def evaluate_answer(
    question: str,
    answer: str,
    interview_type: str,
    topic: str = None,
    resume_skills: list = None
) -> dict:
    context = ""
    if resume_skills:
        context = f"The candidate listed these skills on their resume: {', '.join(resume_skills[:3])}. "
    elif topic:
        context = f"This is a {topic} technical interview question. "
    elif interview_type == "HR":
        context = "This is an HR behavioral interview question. "

    prompt = (
        f"{context}"
        f"Evaluate this interview answer.\n"
        f"Q: {question}\n"
        f"A: {answer}\n\n"
        "Reply in EXACTLY this format (3 lines only):\n"
        "SCORE: <number 1-10>\n"
        "FEEDBACK: <one specific sentence about what was good or missing>\n"
        f"NEXT_QUESTION: <one follow-up question on the same topic ({topic or interview_type})>"
    )

    raw = ask_ollama(prompt)
    result = {
        "score": 5.0,
        "feedback": "Could not evaluate.",
        "next_question": _default_next_question(interview_type, topic, resume_skills)
    }

    if raw == "AI_TIMEOUT":
        result["feedback"] = "Response timed out. Please try again."
        return result

    try:
        for line in raw.split("\n"):
            line = line.strip()
            if line.startswith("SCORE:"):
                val = line.replace("SCORE:", "").strip().split()[0]
                result["score"] = max(1.0, min(10.0, float(val)))
            elif line.startswith("FEEDBACK:"):
                result["feedback"] = line.replace("FEEDBACK:", "").strip()
            elif line.startswith("NEXT_QUESTION:"):
                result["next_question"] = line.replace("NEXT_QUESTION:", "").strip()
    except Exception:
        result["feedback"] = raw[:300]

    return result


def _default_next_question(interview_type: str, topic: str = None, resume_skills: list = None) -> str:
    if resume_skills:
        return f"Can you describe a project where you used {resume_skills[0]}?"
    if interview_type == "HR":
        return "Tell me about a time you handled a conflict at work."
    topic_defaults = {
        "Python": "Explain the difference between a list and a tuple in Python.",
        "JavaScript": "How does the JavaScript event loop work?",
        "DSA": "Explain the time complexity of binary search.",
        "SQL": "What is the difference between INNER JOIN and LEFT JOIN?",
        "Machine Learning": "What is overfitting and how do you prevent it?",
        "System Design": "How would you design a URL shortener?",
    }
    return topic_defaults.get(topic, "Describe a challenging technical problem you solved.")


def analyze_resume(text: str) -> dict:
    prompt = (
        "Analyze this resume and reply in EXACTLY this format (no extra text):\n"
        "SKILLS: <comma-separated top 6 technical skills>\n"
        "EXPERIENCE_LEVEL: <Fresher/Junior/Mid/Senior>\n"
        "SUGGESTED_TOPICS: <comma-separated best interview topics>\n"
        "STRENGTHS: <one sentence about key strengths>\n"
        "IMPROVEMENT_AREAS: <one sentence about gaps>\n"
        "ROADMAP: <3 specific learning steps separated by | character>\n\n"
        f"Resume:\n{text[:2000]}"
    )
    raw = ask_ollama(prompt)

    sections = {
        "skills": [],
        "experience_level": "Unknown",
        "suggested_topics": [],
        "strengths": "",
        "improvement_areas": "",
        "roadmap": [],
        "raw": raw,
    }

    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("SKILLS:"):
            sections["skills"] = [s.strip() for s in line.replace("SKILLS:", "").split(",") if s.strip()]
        elif line.startswith("EXPERIENCE_LEVEL:"):
            sections["experience_level"] = line.replace("EXPERIENCE_LEVEL:", "").strip()
        elif line.startswith("SUGGESTED_TOPICS:"):
            sections["suggested_topics"] = [s.strip() for s in line.replace("SUGGESTED_TOPICS:", "").split(",") if s.strip()]
        elif line.startswith("STRENGTHS:"):
            sections["strengths"] = line.replace("STRENGTHS:", "").strip()
        elif line.startswith("IMPROVEMENT_AREAS:"):
            sections["improvement_areas"] = line.replace("IMPROVEMENT_AREAS:", "").strip()
        elif line.startswith("ROADMAP:"):
            raw_roadmap = line.replace("ROADMAP:", "").strip()
            sections["roadmap"] = [s.strip() for s in raw_roadmap.split("|") if s.strip()]

    return sections