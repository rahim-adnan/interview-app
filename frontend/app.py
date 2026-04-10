import streamlit as st
import requests
import json
from config import (
    QUESTIONS_ENDPOINT, EVALUATE_ENDPOINT, HEALTH_ENDPOINT,
    JOB_ROLES, REQUEST_TIMEOUT, SCORE_COLORS
)


# ── PAGE CONFIG ───────────────────────────────────────────────────────
# Must be the FIRST Streamlit call in the file

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ── CUSTOM CSS ────────────────────────────────────────────────────────
# Streamlit lets us inject CSS to customize the look

st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f8f9fa; }

    /* Feedback card styling */
    .feedback-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #4A90D9;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .feedback-card h4 {
        color: #2c3e50;
        margin-bottom: 8px;
        font-size: 15px;
        font-weight: 600;
    }
    .feedback-card p {
        color: #444;
        font-size: 14px;
        line-height: 1.6;
        margin: 0;
    }

    /* Score badge */
    .score-badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        font-size: 22px;
        font-weight: bold;
        margin: 10px 0;
    }
    .score-high   { background: #d4edda; color: #155724; }
    .score-medium { background: #fff3cd; color: #856404; }
    .score-low    { background: #f8d7da; color: #721c24; }

    /* Question card */
    .question-card {
        background: #eef4ff;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 8px 0;
        border-left: 4px solid #4A90D9;
        font-size: 15px;
        color: #1a1a2e;
    }

    /* Improved answer box */
    .improved-answer {
        background: #f0fff4;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #28a745;
        font-size: 14px;
        color: #1a3a1a;
        line-height: 1.7;
    }

    /* Header styling */
    .app-header {
        text-align: center;
        padding: 20px 0 10px;
    }

    /* Status dot */
    .status-online  { color: #28a745; font-weight: 600; }
    .status-offline { color: #dc3545; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE INIT ────────────────────────────────────────────────
# session_state persists data between Streamlit reruns.
# We initialize keys here so they always exist before we use them.

if "questions" not in st.session_state:
    st.session_state.questions = []         # list of question strings

if "selected_role" not in st.session_state:
    st.session_state.selected_role = ""

if "feedback_history" not in st.session_state:
    st.session_state.feedback_history = []  # list of feedback dicts

if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0


# ── HELPER FUNCTIONS ──────────────────────────────────────────────────

def check_backend_health() -> bool:
    """Checks if the FastAPI backend is running."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        return response.status_code == 200
    except:
        return False


def fetch_questions(role: str, num_questions: int) -> list:
    """Calls /generate-questions and returns a list of question strings."""
    payload = {"role": role, "num_questions": num_questions}
    response = requests.post(QUESTIONS_ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()["questions"]


def fetch_evaluation(question: str, answer: str, role: str) -> dict:
    """Calls /evaluate-answer and returns the feedback dictionary."""
    payload = {"question": question, "answer": answer, "role": role}
    response = requests.post(EVALUATE_ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_score_style(score: int) -> tuple:
    """Returns (css_class, emoji) based on score."""
    if score >= 8:
        return "score-high", "🟢"
    elif score >= 5:
        return "score-medium", "🟡"
    else:
        return "score-low", "🔴"


def render_feedback_card(icon: str, title: str, content: str, border_color: str = "#4A90D9"):
    """Renders a single styled feedback card."""
    st.markdown(f"""
    <div class="feedback-card" style="border-left-color: {border_color};">
        <h4>{icon} {title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)


# ── HEADER ────────────────────────────────────────────────────────────

st.markdown("""
<div class="app-header">
    <h1>🎯 AI Interview Coach</h1>
    <p style="color: #666; font-size: 16px;">
        Practice job interviews and get instant AI-powered feedback on your answers
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()


# ── BACKEND STATUS ────────────────────────────────────────────────────
# Show a live indicator so the user knows if the backend is running

col_status, col_spacer = st.columns([1, 3])
with col_status:
    backend_ok = check_backend_health()
    if backend_ok:
        st.markdown('<p class="status-online">● Backend connected</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-offline">● Backend offline — run: cd backend && python main.py</p>', unsafe_allow_html=True)


# ── SECTION 1: ROLE SELECTION ─────────────────────────────────────────

st.markdown("### 👤 Step 1 — Choose your job role")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    selected_role = st.selectbox(
        "Select a job role to practice:",
        options=JOB_ROLES,
        index=0,
        label_visibility="collapsed"
    )

with col2:
    num_questions = st.selectbox(
        "Number of questions:",
        options=[3, 4, 5],
        index=1
    )

with col3:
    generate_btn = st.button(
        "🎲 Generate Questions",
        type="primary",
        use_container_width=True,
        disabled=not backend_ok
    )


# ── GENERATE QUESTIONS LOGIC ──────────────────────────────────────────

if generate_btn:
    with st.spinner(f"Generating {num_questions} interview questions for {selected_role}..."):
        try:
            questions = fetch_questions(selected_role, num_questions)
            # Save to session state so they persist across reruns
            st.session_state.questions = questions
            st.session_state.selected_role = selected_role
            st.session_state.feedback_history = []       # reset feedback
            st.session_state.current_question_idx = 0    # start from Q1
            st.success(f"✅ Generated {len(questions)} questions for **{selected_role}**!")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot reach the backend. Make sure it's running on port 8000.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# ── SECTION 2: QUESTIONS + ANSWERS ───────────────────────────────────

if st.session_state.questions:
    st.divider()
    st.markdown(f"### 📋 Step 2 — Answer the questions  ·  Role: **{st.session_state.selected_role}**")

    # Show all questions with a small card for each
    for i, question in enumerate(st.session_state.questions):
        st.markdown(f"""
        <div class="question-card">
            <strong>Q{i+1}.</strong> {question}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Let user pick which question to answer
    st.markdown("#### ✍️ Select a question and write your answer")

    q_options = [f"Q{i+1}: {q[:60]}..." for i, q in enumerate(st.session_state.questions)]
    selected_q_idx = st.selectbox(
        "Choose question to answer:",
        range(len(q_options)),
        format_func=lambda i: q_options[i]
    )

    selected_question = st.session_state.questions[selected_q_idx]

    # Show the selected question clearly
    st.info(f"**Question:** {selected_question}")

    # Text area for user's answer
    user_answer = st.text_area(
        "Your answer:",
        placeholder="Type your answer here... Be detailed and use specific examples.",
        height=150,
        key=f"answer_{selected_q_idx}"  # unique key per question
    )

    # Word count display (helpful for users)
    if user_answer:
        word_count = len(user_answer.split())
        color = "#28a745" if word_count >= 50 else "#ffc107" if word_count >= 20 else "#dc3545"
        st.markdown(f'<p style="color:{color}; font-size:13px;">📝 Word count: {word_count} (aim for 50+ words)</p>',
                    unsafe_allow_html=True)

    # Submit button
    evaluate_btn = st.button(
        "🤖 Get AI Feedback",
        type="primary",
        disabled=not user_answer or len(user_answer.strip()) < 5
    )


    # ── EVALUATE ANSWER LOGIC ─────────────────────────────────────────

    if evaluate_btn and user_answer:
        with st.spinner("🧠 AI is analyzing your answer... (may take 30–60 seconds)"):
            try:
                feedback = fetch_evaluation(
                    question=selected_question,
                    answer=user_answer,
                    role=st.session_state.selected_role
                )

                # Save to history so user can review all past answers
                history_entry = {
                    "question": selected_question,
                    "answer": user_answer,
                    "feedback": feedback
                }
                # Update or append
                found = False
                for entry in st.session_state.feedback_history:
                    if entry["question"] == selected_question:
                        entry.update(history_entry)
                        found = True
                        break
                if not found:
                    st.session_state.feedback_history.append(history_entry)

                # ── DISPLAY FEEDBACK ──────────────────────────────────
                st.divider()
                st.markdown("### 📊 AI Feedback")

                # Score at the top (prominent)
                score = feedback["score"]
                score_class, score_emoji = get_score_style(score)
                st.markdown(f"""
                <div style="text-align:center; margin: 10px 0 20px;">
                    <div class="score-badge {score_class}">
                        {score_emoji} Score: {score} / 10
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Feedback cards in 2 columns
                col_a, col_b = st.columns(2)

                with col_a:
                    render_feedback_card(
                        "📝", "Grammar & Language",
                        feedback["grammar"],
                        border_color="#6c757d"
                    )
                    render_feedback_card(
                        "🎯", "Clarity & Structure",
                        feedback["clarity"],
                        border_color="#17a2b8"
                    )

                with col_b:
                    render_feedback_card(
                        "⚙️", "Technical Accuracy",
                        feedback["technical_accuracy"],
                        border_color="#fd7e14"
                    )
                    render_feedback_card(
                        "💡", "Suggestions for Improvement",
                        feedback["improvements"],
                        border_color="#6f42c1"
                    )

                # Improved answer — full width below
                st.markdown("#### ✨ Improved Sample Answer")
                st.markdown(f"""
                <div class="improved-answer">
                    {feedback["improved_answer"]}
                </div>
                """, unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot reach the backend.")
            except Exception as e:
                st.error(f"❌ Evaluation failed: {str(e)}")


# ── SECTION 3: SESSION HISTORY ────────────────────────────────────────
# Shows all questions answered in this session

if st.session_state.feedback_history:
    st.divider()
    st.markdown("### 📚 Session History")
    st.caption(f"You've answered {len(st.session_state.feedback_history)} question(s) this session.")

    for i, entry in enumerate(st.session_state.feedback_history):
        score = entry["feedback"]["score"]
        score_class, score_emoji = get_score_style(score)

        with st.expander(f"Q{i+1}: {entry['question'][:70]}...  {score_emoji} {score}/10"):
            st.markdown(f"**Your answer:** {entry['answer']}")
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Grammar:** {entry['feedback']['grammar']}")
                st.markdown(f"**Clarity:** {entry['feedback']['clarity']}")
            with col2:
                st.markdown(f"**Technical:** {entry['feedback']['technical_accuracy']}")
                st.markdown(f"**Improvements:** {entry['feedback']['improvements']}")
            st.markdown(f"**✨ Better answer:** {entry['feedback']['improved_answer']}")

    # Summary stats
    st.divider()
    scores = [e["feedback"]["score"] for e in st.session_state.feedback_history]
    avg_score = sum(scores) / len(scores)

    col1, col2, col3 = st.columns(3)
    col1.metric("Questions Answered", len(scores))
    col2.metric("Average Score", f"{avg_score:.1f} / 10")
    col3.metric("Best Score", f"{max(scores)} / 10")

    if st.button("🗑️ Clear Session & Start Over"):
        st.session_state.questions = []
        st.session_state.feedback_history = []
        st.session_state.selected_role = ""
        st.rerun()


# ── FOOTER ────────────────────────────────────────────────────────────

st.divider()
st.markdown("""
<div style="text-align:center; color:#999; font-size:13px; padding: 10px 0;">
    AI Interview Coach · Powered by HuggingFace flan-t5-large · Runs 100% locally
</div>
""", unsafe_allow_html=True)
