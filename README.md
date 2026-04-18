# 🎯 AI Interview Coach

A free, AI-powered interview practice web application.
Practice job interviews, get detailed feedback, and improve your answers —
powered by Groq + Llama3, no local setup required.

---

## 🖥️ Screenshots

```
┌─────────────────────────────────────────────────────┐
│  🎯 AI Interview Coach                              │
│  Practice job interviews and get instant feedback   │
│  ● Backend connected                                │
│                                                     │
│  👤 Step 1 — Choose your job role                  │
│  [ Software Engineer        ▾ ]  [ 4 ▾ ]  [🎲 Go] │
│                                                     │
│  📋 Step 2 — Answer the questions                  │
│  Q1. Explain how you handle system design at scale  │
│  Q2. Describe a time you debugged a hard problem    │
│                                                     │
│  ✍️  Your answer: [________________________]       │
│  📝 Word count: 72                                  │
│                          [ 🤖 Get AI Feedback ]     │
│                                                     │
│  📊 AI Feedback          🟢 Score: 8 / 10          │
│  ┌──────────────┐  ┌──────────────────────────┐    │
│  │ 📝 Grammar   │  │ ⚙️ Technical Accuracy     │    │
│  │ Great use of │  │ Solid understanding of... │    │
│  │ vocabulary.. │  │                          │    │
│  └──────────────┘  └──────────────────────────┘    │
│  ✨ Improved Sample Answer                          │
│  In my previous role at...                          │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Features

- **Role-specific questions** — 15 job roles, mix of technical + behavioral questions
- **5-dimension feedback** — grammar, clarity, technical accuracy, improvements, rewritten answer
- **Score 1–10** — color-coded rating (🟢 great / 🟡 average / 🔴 needs work)
- **Improved sample answer** — AI rewrites your answer using the STAR method
- **Session history** — review all your answers and scores in one session
- **Summary stats** — average score, best score, questions answered
- **Fast responses** — powered by Groq cloud (~1–2 seconds per request)

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Python-based web UI |
| Backend | FastAPI | REST API server |
| AI Model | Llama3 via Groq API | Cloud language model |
| Validation | Pydantic | Request/response schemas |
| HTTP | requests | Frontend ↔ Backend calls |

---

## 📁 Project Structure

```
interview-app/
├── backend/
│   ├── main.py          # FastAPI server — 2 API endpoints
│   ├── ai_engine.py     # Groq API integration + prompt engineering
│   └── models.py        # Pydantic request/response schemas
├── frontend/
│   ├── app.py           # Full Streamlit UI
│   └── config.py        # API URLs, job roles, settings
├── requirements.txt     # Python dependencies
└── README.md
```

---

## 🚀 Setup & Installation

### Requirements
- Python 3.9+
- Windows / Mac / Linux
- A free Groq API key — get one at [console.groq.com](https://console.groq.com)

---

### Step 1 — Clone the project
```bash
git clone https://github.com/rahim-adnan/interview-app.git
cd interview-app
```

### Step 2 — Create and activate virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set your Groq API key
Create a `.env` file inside the `backend/` folder:
```
GROQ_API_KEY=your_key_here
```
> Get a free key at: https://console.groq.com

### Step 5 — Start the backend (Terminal 1)
```bash
cd backend
python main.py
```
Wait for:
```
Groq connected. Model 'llama3-8b-8192' ready!
Server ready!
```
> API docs available at: http://localhost:8000/docs

### Step 6 — Start the frontend (Terminal 2)
```bash
cd frontend
streamlit run app.py
```
> Opens automatically at: http://localhost:8501

---

## 🔌 API Reference

### `GET /health`
Check if the server is running.
```json
{ "status": "healthy", "message": "AI Interview API is running" }
```

### `POST /generate-questions`
Generate interview questions for a role.
```json
Request:  { "role": "Software Engineer", "num_questions": 4 }
Response: { "role": "Software Engineer", "questions": ["Q1...", "Q2..."] }
```

### `POST /evaluate-answer`
Evaluate a candidate's interview answer.
```json
Request: {
  "question": "Tell me about yourself.",
  "answer": "I am a software engineer with 3 years of experience...",
  "role": "Software Engineer"
}
Response: {
  "grammar": "The answer uses clear and professional language...",
  "clarity": "The response is well structured and direct...",
  "technical_accuracy": "Good demonstration of relevant experience...",
  "improvements": "1. Add specific project examples. 2. Quantify achievements.",
  "improved_answer": "With 3 years of experience building scalable APIs...",
  "score": 7
}
```

---

## ⚡ Performance

Responses typically arrive in **1–2 seconds** thanks to Groq's fast inference cloud.

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---|---|
| `Backend offline` in UI | Run `python main.py` in the backend folder |
| `GROQ_API_KEY not set` | Make sure `.env` file exists in the `backend/` folder |
| `Invalid GROQ_API_KEY` | Double-check the key copied from console.groq.com |
| `ModuleNotFoundError` | Activate venv and run `pip install -r requirements.txt` |
| Port 8000 already in use | Change port in `main.py` to 8001 |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |

---

## 🔮 Future Improvements

- [ ] More job roles (expand from 15 to 50+)
- [ ] Difficulty levels (Junior / Mid / Senior)
- [ ] Interview timer to simulate real pressure
- [ ] PDF export of session feedback
- [ ] Persistent history across sessions (database)
- [ ] Speech-to-text answer input
- [ ] Multi-language support

---

## 👤 Author

Built with Python, FastAPI, Streamlit, and Groq.
100% free and open source.

---

## 📄 License

MIT License — free to use, modify, and distribute.
