import os
import re
import logging
import requests

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── CONFIGURATION ─────────────────────────────────────────────────────

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME   = "llama3-8b-8192"   # Free Llama3 on Groq — fast & free


def get_api_key() -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        raise RuntimeError(
            "GROQ_API_KEY environment variable not set.\n"
            "Get a free key at: https://console.groq.com\n"
            "Then set it: export GROQ_API_KEY=your_key_here"
        )
    return key


# ── STARTUP CHECK ─────────────────────────────────────────────────────

def load_model():
    """
    Called on server startup.
    Checks that the Groq API key is set and valid.
    """
    logger.info("Checking Groq API connection...")
    try:
        key = get_api_key()
        # lightweight test call
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if response.status_code == 200:
            logger.info(f"Groq connected. Model '{MODEL_NAME}' ready!")
        else:
            raise RuntimeError(f"Groq API error: {response.status_code} — {response.text}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot reach Groq API. Check your internet connection.")


# ── CORE CALL ─────────────────────────────────────────────────────────

def call_groq(prompt: str, max_tokens: int = 500) -> str:
    """
    Sends a prompt to the Groq cloud API and returns the response.
    Uses the OpenAI-compatible chat completions endpoint.
    """
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":       MODEL_NAME,
        "messages":    [{"role": "user", "content": prompt}],
        "max_tokens":  max_tokens,
        "temperature": 0.7,
        "top_p":       0.9,
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot reach Groq API. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise RuntimeError("Groq API timed out. Please try again.")
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            raise RuntimeError("Invalid GROQ_API_KEY. Get a free key at https://console.groq.com")
        raise RuntimeError(f"Groq API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")


# ── QUESTION GENERATION ───────────────────────────────────────────────

def generate_questions(role: str, num_questions: int = 4) -> list[str]:
    logger.info(f"Generating {num_questions} questions for: {role}")

    prompt = f"""You are an experienced HR interviewer. Generate exactly {num_questions} realistic interview questions for a {role} position.

Rules:
- Mix technical and behavioral questions
- Make them specific to the {role} role
- Number each question
- Output ONLY the questions, no explanations or extra text

Example format:
1. How do you handle tight deadlines?
2. Explain the difference between X and Y.

Now generate {num_questions} questions for a {role}:"""

    raw = call_groq(prompt, max_tokens=400)
    questions = parse_questions(raw, num_questions)
    logger.info(f"Generated {len(questions)} questions")
    return questions


def parse_questions(raw_text: str, num_questions: int) -> list[str]:
    questions = []
    for line in raw_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        cleaned = re.sub(r'^[\d]+[.):\-]\s*', '', line).strip()
        cleaned = re.sub(r'^[Qq][\d]+[.):\-]\s*', '', cleaned).strip()
        if len(cleaned) > 15:
            questions.append(cleaned)
    if len(questions) < 2:
        questions = get_fallback_questions(num_questions)
    return questions[:num_questions]


def get_fallback_questions(num_questions: int) -> list[str]:
    fallbacks = [
        "Tell me about yourself and your professional background.",
        "What is your greatest technical strength and how have you applied it?",
        "Describe a challenging project you worked on and how you overcame obstacles.",
        "Where do you see yourself in 5 years?",
        "Why are you interested in this role?",
        "How do you handle tight deadlines and competing priorities?",
        "Describe a time you had a conflict with a teammate and how you resolved it.",
        "What motivates you professionally?",
    ]
    return fallbacks[:num_questions]


# ── ANSWER EVALUATION ─────────────────────────────────────────────────

def evaluate_answer(question: str, answer: str, role: str) -> dict:
    logger.info(f"Evaluating answer for role: {role}")

    prompt = f"""You are an expert interview coach. A candidate is interviewing for a {role} position.

Question asked: {question}

Candidate's answer: {answer}

Evaluate the answer and respond in EXACTLY this format. Do not add anything before or after.

GRAMMAR: Write 2 sentences evaluating the grammar, vocabulary, and language professionalism.

CLARITY: Write 2 sentences evaluating how clear, structured, and direct the answer is.

TECHNICAL: Write 2 sentences evaluating the technical accuracy and depth for a {role} role.

IMPROVEMENTS: Write 2-3 specific actionable suggestions to improve this answer.

IMPROVED_ANSWER: Rewrite the answer professionally in 3-5 sentences using the STAR method (Situation, Task, Action, Result) where applicable.

SCORE: Write only a single number from 1 to 10."""

    raw = call_groq(prompt, max_tokens=700)
    logger.info(f"Raw evaluation received ({len(raw)} chars)")
    return parse_evaluation(raw, answer)


def parse_evaluation(raw: str, original_answer: str) -> dict:
    def extract(label: str) -> str:
        pattern = rf"{label}:\s*(.+?)(?=\n[A-Z_]{{3,}}:|$)"
        match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    grammar      = extract("GRAMMAR")         or "The answer demonstrates basic communication skills. Consider using more professional vocabulary."
    clarity      = extract("CLARITY")         or "The answer partially addresses the question. A clearer structure would help."
    technical    = extract("TECHNICAL")       or "The technical content needs more depth and specificity for this role."
    improvements = extract("IMPROVEMENTS")    or "Add specific examples. Quantify your achievements. Use the STAR method."
    improved     = extract("IMPROVED_ANSWER") or original_answer

    score_raw   = extract("SCORE")
    score_match = re.search(r'\b([1-9]|10)\b', score_raw)
    score       = int(score_match.group(1)) if score_match else calculate_fallback_score(original_answer)

    return {
        "grammar":            grammar,
        "clarity":            clarity,
        "technical_accuracy": technical,
        "improvements":       improvements,
        "improved_answer":    improved,
        "score":              score,
    }


def calculate_fallback_score(answer: str) -> int:
    score = 5
    words = len(answer.split())
    if words < 10:    score -= 3
    elif words < 25:  score -= 1
    elif words >= 60: score += 2
    elif words >= 40: score += 1
    keywords = ["example", "achieved", "result", "because", "project",
                "team", "improved", "led", "built", "designed", "implemented"]
    score += min(sum(1 for w in keywords if w in answer.lower()), 2)
    return max(1, min(10, score))