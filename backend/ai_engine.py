import requests
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama runs locally on this URL — no API key needed
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME  = "llama3"


# ── STARTUP CHECK ─────────────────────────────────────────────────────

def load_model():
    """
    Called on server startup.
    Checks that Ollama is running and the model is available.
    """
    logger.info("Checking Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m["name"] for m in response.json().get("models", [])]
            logger.info(f"Ollama running. Available models: {models}")
            if not any(MODEL_NAME in m for m in models):
                logger.warning(
                    f"Model '{MODEL_NAME}' not found! "
                    f"Run: ollama pull {MODEL_NAME}"
                )
            else:
                logger.info(f"Model '{MODEL_NAME}' ready!")
        else:
            raise ConnectionError("Ollama returned unexpected status")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama.\n"
            "Make sure Ollama is installed and running.\n"
            "Download from: https://ollama.com\n"
            "Then run: ollama pull mistral"
        )


# ── CORE CALL ─────────────────────────────────────────────────────────

def call_ollama(prompt: str, max_tokens: int = 500) -> str:
    """
    Sends a prompt to the local Ollama server and returns the response.

    HOW IT WORKS:
    Ollama runs a tiny HTTP server on your machine (port 11434).
    We POST a JSON request with the prompt, it streams back the response.
    """
    payload = {
        "model":  MODEL_NAME,
        "prompt": prompt,
        "stream": False,          # get full response at once (simpler)
        "options": {
            "num_predict": max_tokens,   # max output tokens
            "temperature": 0.7,          # 0=robotic, 1=creative, 0.7=balanced
            "top_p": 0.9,
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["response"].strip()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Ollama is not running. Start it from your system tray or run 'ollama serve'.")
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama timed out. The model may be loading — try again in a moment.")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {str(e)}")


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

    raw = call_ollama(prompt, max_tokens=400)
    questions = parse_questions(raw, num_questions)
    logger.info(f"Generated {len(questions)} questions")
    return questions


def parse_questions(raw_text: str, num_questions: int) -> list[str]:
    questions = []
    for line in raw_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        # Remove numbering like "1." "2)" "Q1:" etc
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

    raw = call_ollama(prompt, max_tokens=700)
    logger.info(f"Raw evaluation received ({len(raw)} chars)")
    return parse_evaluation(raw, answer)


def parse_evaluation(raw: str, original_answer: str) -> dict:
    """
    Parses the structured response from Ollama into a clean dictionary.
    Each section is extracted using regex pattern matching.
    """

    def extract(label: str) -> str:
        # Match "LABEL: content" up to the next label or end of string
        pattern = rf"{label}:\s*(.+?)(?=\n[A-Z_]{{3,}}:|$)"
        match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    grammar      = extract("GRAMMAR")         or "The answer demonstrates basic communication skills. Consider using more professional vocabulary."
    clarity      = extract("CLARITY")         or "The answer partially addresses the question. A clearer structure would help."
    technical    = extract("TECHNICAL")        or "The technical content needs more depth and specificity for this role."
    improvements = extract("IMPROVEMENTS")    or "Add specific examples. Quantify your achievements. Use the STAR method."
    improved     = extract("IMPROVED_ANSWER") or original_answer

    # Extract the score number
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
    """Simple rule-based score used when the model output can't be parsed."""
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