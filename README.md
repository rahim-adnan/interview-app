# 🎯 AI Interview Coach

A fully local, completely free AI-powered interview practice web application.
Practice job interviews, get detailed feedback, and improve your answers —
no API keys, no subscriptions, no internet required after setup.

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
- **100% local** — your answers never leave your machine
- **No API key** — powered by Ollama + Llama3, completely free forever

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Python-based web UI |
| Backend | FastAPI | REST API server |
| AI Model | Llama3 via Ollama | Local language model |
| Validation | Pydantic | Request/response schemas |
| HTTP | requests | Frontend ↔ Backend calls |

---

## 📁 Project Structure

```
interview-app/
├── backend/
│   ├── main.py          # FastAPI server — 2 API endpoints
│   ├── ai_engine.py     # Ollama integration + prompt engineering
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
- ~6GB free disk space (for Llama3 model)
- 8GB RAM recommended

---

### Step 1 — Clone or download the project
```bash
git clone https://github.com/yourname/interview-app.git
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

### Step 3 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Install Ollama
1. Go to **https://ollama.com**
2. Download and install for your OS
3. Ollama will run silently in the background after install

### Step 5 — Download Llama3 model
```bash
ollama pull llama3
```
> ⏳ This downloads ~4.7GB once. Never again after this.

### Step 6 — Start the backend (Terminal 1)
```bash
cd backend
python main.py
```
Wait for:
```
Model 'llama3' ready!
Server ready!
```
> API docs available at: http://localhost:8000/docs

### Step 7 — Start the frontend (Terminal 2)
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

## ⚡ Performance Notes

| Model | Speed (CPU) | Quality |
|---|---|---|
| phi3 | ~20–40 sec | Good |
| mistral | ~40–60 sec | Great |
| **llama3** | **~60–120 sec** | **Great** |

> Responses take 60–120 seconds on CPU — this is normal.
> A machine with a GPU (NVIDIA) will be 10–20x faster.
> To use a different model: change `MODEL_NAME` in `backend/ai_engine.py`
> and run `ollama pull <modelname>`.

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---|---|
| `Backend offline` in UI | Run `python main.py` in the backend folder |
| `Model 'llama3' not found` | Run `ollama pull llama3` |
| `Cannot connect to Ollama` | Open Ollama from Start Menu or run `ollama serve` |
| Spinner never finishes | Wait up to 2 minutes — normal on CPU |
| `ModuleNotFoundError` | Activate venv and run `pip install -r requirements.txt` |
| Port 8000 already in use | Change port in `main.py` to 8001 |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |

---

## 🔮 Future Improvements

- [ ] GPU support for faster inference
- [ ] More job roles (expand from 15 to 50+)
- [ ] Difficulty levels (Junior / Mid / Senior)
- [ ] Interview timer to simulate real pressure
- [ ] PDF export of session feedback
- [ ] Persistent history across sessions (database)
- [ ] Speech-to-text answer input
- [ ] Multi-language support

---

## 👤 Author

Built with Python, FastAPI, Streamlit, and Ollama.
100% free and open source.

---

## 📄 License

MIT License — free to use, modify, and distribute.
