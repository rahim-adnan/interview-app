from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from models import (
    QuestionRequest, QuestionResponse,
    EvaluateRequest, FeedbackResponse,
    ErrorResponse
)
from ai_engine import load_model, generate_questions, evaluate_answer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── STARTUP / SHUTDOWN ────────────────────────────────────────────────
# This runs ONCE when the server starts.
# We load the AI model here so it's ready before any requests come in.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: load the model before accepting requests
    logger.info("Server starting — loading AI model...")
    load_model()
    logger.info("Server ready!")
    yield
    # SHUTDOWN: nothing to clean up for our model
    logger.info("Server shutting down.")


# ── APP SETUP ─────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Interview Practice API",
    description="Generate interview questions and get AI feedback on your answers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS = Cross-Origin Resource Sharing
# This allows our Streamlit frontend (running on port 8501)
# to talk to our FastAPI backend (running on port 8000).
# Without this, the browser blocks the connection.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # in production, replace * with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── HEALTH CHECK ──────────────────────────────────────────────────────
# A simple endpoint to confirm the server is alive.
# Try it: http://localhost:8000/health

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Interview API is running"}


# ── ENDPOINT 1: GENERATE QUESTIONS ───────────────────────────────────
# The frontend sends: { "role": "Software Engineer", "num_questions": 4 }
# We return:          { "role": "...", "questions": ["Q1", "Q2", ...] }

@app.post("/generate-questions", response_model=QuestionResponse)
async def get_questions(request: QuestionRequest):
    """
    Generate interview questions for a given job role.

    - Validates input automatically via Pydantic (QuestionRequest)
    - Calls ai_engine to generate questions
    - Returns structured JSON response
    """
    # Validate role isn't empty
    if not request.role.strip():
        raise HTTPException(status_code=400, detail="Role cannot be empty")

    # Clamp num_questions between 2 and 6
    num_q = max(2, min(6, request.num_questions))

    try:
        logger.info(f"Generating {num_q} questions for: {request.role}")
        questions = generate_questions(request.role, num_q)

        return QuestionResponse(
            role=request.role,
            questions=questions,
            success=True
        )

    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate questions: {str(e)}"
        )


# ── ENDPOINT 2: EVALUATE ANSWER ───────────────────────────────────────
# The frontend sends: { "question": "...", "answer": "...", "role": "..." }
# We return:          { "grammar": "...", "clarity": "...", "score": 7, ... }

@app.post("/evaluate-answer", response_model=FeedbackResponse)
async def get_evaluation(request: EvaluateRequest):
    """
    Evaluate a user's interview answer and return structured feedback.

    - Takes the question, the user's answer, and the job role
    - Returns feedback on grammar, clarity, technical accuracy,
      suggestions for improvement, a rewritten answer, and a score
    """
    # Validate inputs
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    if not request.answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty")
    if len(request.answer.strip()) < 5:
        raise HTTPException(status_code=400, detail="Answer is too short to evaluate")

    try:
        logger.info(f"Evaluating answer for: {request.role}")
        feedback = evaluate_answer(request.question, request.answer, request.role)

        return FeedbackResponse(
            question=request.question,
            grammar=feedback["grammar"],
            clarity=feedback["clarity"],
            technical_accuracy=feedback["technical_accuracy"],
            improvements=feedback["improvements"],
            improved_answer=feedback["improved_answer"],
            score=feedback["score"],
            success=True
        )

    except Exception as e:
        logger.error(f"Error evaluating answer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate answer: {str(e)}"
        )


# ── RUN THE SERVER ────────────────────────────────────────────────────
# This block only runs if you execute: python main.py
# If using uvicorn directly (recommended), this block is ignored.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
