
from pydantic import BaseModel



from typing import List, Optional


# ── REQUEST MODELS (data coming IN to the API) ────────────────────────

class QuestionRequest(BaseModel):
    """Sent by the frontend to /generate-questions"""
    role: str                          # e.g. "Software Engineer"
    num_questions: int = 4             # how many questions to generate (default: 4)


class EvaluateRequest(BaseModel):
    """Sent by the frontend to /evaluate-answer"""
    question: str                      # the interview question
    answer: str                        # the user's typed answer
    role: str                          # role context helps the AI judge technical accuracy


# ── RESPONSE MODELS (data going OUT of the API) ───────────────────────

class QuestionResponse(BaseModel):
    """Returned by /generate-questions"""
    role: str
    questions: List[str]               # list of question strings
    success: bool = True


class FeedbackResponse(BaseModel):
    """Returned by /evaluate-answer — structured feedback card"""
    question: str
    grammar: str                       # grammar and language quality
    clarity: str                       # how clear and structured the answer is
    technical_accuracy: str            # correctness of technical content
    improvements: str                  # specific suggestions
    improved_answer: str               # a rewritten better version
    score: int                         # 1–10 rating
    success: bool = True


class ErrorResponse(BaseModel):
    """Returned when something goes wrong"""
    success: bool = False
    message: str
