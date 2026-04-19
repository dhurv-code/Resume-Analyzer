# from fastapi import FastAPI, UploadFile,  File , Form
# from fastapi.middleware.cors import CORSMiddleware
# import pdfplumber
# from sentence_transformers import SentenceTransformer, util
# app=FastAPI()

# # using middleware here

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://127.0.0.1:5173"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# model=SentenceTransformer('all-MiniLM-L6-v2')
# @app.get("/")
# def home():
#     return{"message":"Resume analyzer api running"}
# def extract_text_from_pdf(file):
#     text=""
#     with pdfplumber.open(file.file)as pdf:
#         for page in pdf.pages:
#             text+=page.extract_text()+" "
#     return text


# @app.post("/analyze")
# async def analyze_resume(
#     resume:UploadFile=File(...),
#     job_description:str=Form(...)
# ):
#     resume_text=extract_text_from_pdf(resume)
#     embedding1= model.encode(resume_text, convert_to_tensor=True)
#     embedding2=model.encode(job_description, convert_to_tensor=True)
    
#     score=util.pytorch_cos_sim(embedding1, embedding2).item()
    
#     return{
#         "match_score":round(score*100,2),
#         "resume_text":resume_text[:500]
#     }


from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import re
from sentence_transformers import SentenceTransformer, util

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer("all-MiniLM-L6-v2")

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
            t = page.extract_text()
            if t:
                text += t + " "
    return text.lower()

def detect_skills(text):
    found = []
    for skill in skills_db:
        if skill in text:
            found.append(skill)
    return found

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_text = extract_text_from_pdf(resume)
    jd_text = job_description.lower()

    embedding1 = model.encode(resume_text, convert_to_tensor=True)
    embedding2 = model.encode(jd_text, convert_to_tensor=True)

    score = util.pytorch_cos_sim(embedding1, embedding2).item()
    match_score = round(score * 100, 2)

    resume_skills = detect_skills(resume_text)
    jd_skills = detect_skills(jd_text)

    matched = [s for s in jd_skills if s in resume_skills]
    missing = [s for s in jd_skills if s not in resume_skills]

    ats_score = min(100, len(matched) * 15 + 40)

    suggestions = []
    if missing:
        suggestions.append("Add missing skills in projects or experience.")
    if "linkedin" not in resume_text:
        suggestions.append("Add LinkedIn profile.")
    if "github" not in resume_text:
        suggestions.append("Add GitHub profile.")

    return {
        "match_score": match_score,
        "ats_score": ats_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions,
        "resume_text": resume_text[:1000]
    }








