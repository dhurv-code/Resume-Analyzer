from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Later restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expanded Multi-Domain Skills Database
skills_db = [

    # Technical Skills
    "python", "java", "c++", "javascript", "typescript",
    "react", "node.js", "express.js", "fastapi", "django",
    "html", "css", "tailwind", "bootstrap",
    "sql", "mysql", "postgresql", "mongodb",
    "tensorflow", "pytorch", "machine learning",
    "deep learning", "nlp", "pandas", "numpy",
    "scikit-learn", "aws", "azure", "docker",
    "kubernetes", "git", "github", "linux", "postman",

    # Management Skills
    "project management", "team management",
    "stakeholder management", "operations management",
    "strategic planning", "business development",
    "leadership", "decision making", "problem solving",

    # Communication / Soft Skills
    "communication", "verbal communication",
    "written communication", "presentation skills",
    "negotiation", "public speaking", "collaboration",
    "teamwork", "interpersonal skills",
    "time management", "adaptability",
    "critical thinking",

    # Product Management Skills
    "product management", "roadmap planning",
    "market research", "user research",
    "agile", "scrum", "jira", "kanban",
    "product strategy", "go-to-market",
    "requirements gathering", "wireframing",
    "a/b testing",

    # HR Skills
    "recruitment", "talent acquisition",
    "employee engagement", "performance management",
    "payroll", "onboarding", "hr operations",
    "training and development", "conflict resolution",
    "employee relations",

    # Sales / Marketing Skills
    "sales", "lead generation", "crm",
    "customer relationship management",
    "digital marketing", "seo", "sem",
    "branding", "content marketing",
    "email marketing", "social media marketing",

    # Finance / Analytics
    "excel", "financial analysis",
    "budgeting", "forecasting",
    "accounting", "data analysis",
    "power bi", "tableau",

    # Customer Support
    "customer service", "client handling",
    "issue resolution", "technical support",
    "call handling"
]


@app.get("/")
def home():
    return {"message": "Resume Analyzer API Running"}


# Extract text from uploaded PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.lower()


# Better skill detection using word boundaries
def detect_skills(text):
    found = []

    for skill in skills_db:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text):
            found.append(skill)

    return found


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_text = extract_text_from_pdf(resume)
    jd_text = job_description.lower()

    # TF-IDF Similarity
    docs = [resume_text, jd_text]
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(docs)

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    match_score = round(similarity * 100, 2)

    # Skill Matching
    resume_skills = detect_skills(resume_text)
    jd_skills = detect_skills(jd_text)

    matched = [skill for skill in jd_skills if skill in resume_skills]
    missing = [skill for skill in jd_skills if skill not in resume_skills]

    # ATS Readiness Score
    ats_score = min(100, 40 + len(matched) * 10)

    # Suggestions
    suggestions = []

    if missing:
        suggestions.append("Add missing relevant skills to improve alignment.")

    if "linkedin" not in resume_text:
        suggestions.append("Add LinkedIn profile.")

    if "github" not in resume_text:
        suggestions.append("Add GitHub profile.")

    if len(resume_text) < 300:
        suggestions.append("Resume seems short. Add more measurable achievements.")

    return {
        "match_score": match_score,
        "ats_score": ats_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions,
        "resume_text": resume_text[:1000]
    }