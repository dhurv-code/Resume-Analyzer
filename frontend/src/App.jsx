import { useState } from "react";
import axios from "axios";

export default function App(){
  const [file, setFile] = useState(null);
  const [jobDesc, setJobDesc] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");


  const analyzeResume= async()=>{
    if(!file||!jobDesc.trim()){
      setError("Please upload a resume and enter job description.")
      return;
    }

    setError("");
    setLoading(true);
    setResult(null);

    const formData=new FormData();
    formData.append("resume",file);
    formData.append("job_description",jobDesc);

    try{
      const res=await axios.post(
        "https://resume-analyzer-yjdf.onrender.com/analyze",
        formData
      );
      setResult(res.data);
    }catch(err){
      console.log(err);
      setError("Backend connection failed.")
    }
    finally{
      setLoading(false);
    }
  };

   return (
    <div className="min-h-screen bg-slate-950 text-white px-6 py-10">
      <div className="max-w-5xl mx-auto">

        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold mb-3">
            AI Resume Analyzer
          </h1>
          <p className="text-slate-400 text-lg">
            Match your resume with any job description instantly
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">

          <div className="bg-slate-900 rounded-2xl p-6 shadow-xl">
            <h2 className="text-2xl font-semibold mb-4">
              Upload Resume
            </h2>

            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full p-3 bg-slate-800 rounded-xl"
            />

            {file && (
              <p className="mt-3 text-green-400 text-sm">
                {file.name}
              </p>
            )}
          </div>

          <div className="bg-slate-900 rounded-2xl p-6 shadow-xl">
            <h2 className="text-2xl font-semibold mb-4">
              Job Description
            </h2>

            <textarea
              rows="8"
              value={jobDesc}
              onChange={(e) => setJobDesc(e.target.value)}
              placeholder="Paste job description here..."
              className="w-full p-4 bg-slate-800 rounded-xl outline-none"
            />
          </div>
        </div>

        <div className="text-center mt-8">
          <button
            onClick={analyzeResume}
            className="px-8 py-4 rounded-2xl bg-blue-600 hover:bg-blue-500 transition text-lg font-semibold"
          >
            {loading ? "Analyzing..." : "Analyze Resume"}
          </button>
        </div>

        {error && (
          <p className="text-red-400 text-center mt-5">{error}</p>
        )}

        {result && (
  <div className="mt-10 bg-slate-900 rounded-2xl p-8 shadow-xl space-y-6">

    <h2 className="text-3xl font-bold">Analysis Result</h2>

    <div>
      <p className="text-slate-400">Match Score</p>
      <p className="text-green-400 text-3xl font-bold">
        {result.match_score}%
      </p>
    </div>

    <div>
      <p className="text-slate-400">ATS Score</p>
      <p className="text-blue-400 text-3xl font-bold">
        {result.ats_score}/100
      </p>
    </div>

    <div>
      <p className="text-slate-400 mb-2">Matched Skills</p>
      <div className="flex flex-wrap gap-2">
        {result.matched_skills.map((skill, i) => (
          <span key={i} className="bg-green-600 px-3 py-1 rounded-full text-sm">
            {skill}
          </span>
        ))}
      </div>
    </div>

    <div>
      <p className="text-slate-400 mb-2">Missing Skills</p>
      <div className="flex flex-wrap gap-2">
        {result.missing_skills.map((skill, i) => (
          <span key={i} className="bg-red-600 px-3 py-1 rounded-full text-sm">
            {skill}
          </span>
        ))}
      </div>
    </div>

    <div>
      <p className="text-slate-400 mb-2">Suggestions</p>
      <ul className="list-disc ml-6 text-slate-300">
        {result.suggestions.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>

  </div>
        )}

      </div>
    </div>
  );
  
}