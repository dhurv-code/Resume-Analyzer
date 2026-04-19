from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

skills_db = [
    "python", "java", "c++", "react", "fastapi",
    "sql", "mongodb", "machine learning",
    "git", "html", "css", "javascript",
    "tensorflow", "pytorch", "nodejs"
]

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.lower()

def detect_skills(text):
    found = []
    for skill in skills_db:
        if skill in text:
            found.append(skill)
    return found

@app.get("/")
def home():
    return {"message": "Resume Analyzer API Running"}

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_text = extract_text_from_pdf(resume)
    jd_text = job_description.lower()


    docs = [resume_text, jd_text]
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(docs)

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    match_score = round(similarity * 100, 2)


    resume_skills = detect_skills(resume_text)
    jd_skills = detect_skills(jd_text)

    matched = [s for s in jd_skills if s in resume_skills]
    missing = [s for s in jd_skills if s not in resume_skills]


    ats_score = min(100, 40 + len(matched) * 15)

    suggestions = []

    if missing:
        suggestions.append("Add missing skills in projects or experience.")

    if "linkedin" not in resume_text:
        suggestions.append("Add LinkedIn profile.")

    if "github" not in resume_text:
        suggestions.append("Add GitHub profile.")

    if len(resume_text) < 300:
        suggestions.append("Resume content looks short. Add more achievements.")

    return {
        "match_score": match_score,
        "ats_score": ats_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions,
        "resume_text": resume_text[:1000]
    }