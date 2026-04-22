API_BASE_URL = "https://interview-app-6i3h.onrender.com"
# Endpoints
QUESTIONS_ENDPOINT = f"{API_BASE_URL}/generate-questions"
EVALUATE_ENDPOINT  = f"{API_BASE_URL}/evaluate-answer"
HEALTH_ENDPOINT    = f"{API_BASE_URL}/health"

# Timeout in seconds for API calls
REQUEST_TIMEOUT = 120

# Available job roles in the dropdown
JOB_ROLES = [
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Product Manager",
    "UI/UX Designer",
    "Cybersecurity Analyst",
    "Cloud Engineer",
    "QA Engineer",
    "Mobile Developer",
    "Business Analyst",
]

# Score color thresholds (used for the score badge color)
SCORE_COLORS = {
    "high":   (8, 10, "🟢"),   # score 8-10
    "medium": (5, 7,  "🟡"),   # score 5-7
    "low":    (1, 4,  "🔴"),   # score 1-4
}