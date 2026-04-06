import streamlit as st
import re
from utils.parser import extract_text
from model.similarity import get_match_details
from model.skills import extract_skills

# Page config
st.set_page_config(
    page_title="Resume Screening AI",
    page_icon="📄",
    layout="wide"
)

# Load skills
with open("data/skills.txt") as f:
    skills_list = sorted({s.strip().lower() for s in f.readlines() if s.strip()})

# Custom CSS
st.markdown("""
<style>
.main-title {
    font-size: 49px;
    font-weight: 701;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 30px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.score-box {
    padding: 20px;
    border-radius: 15px;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    margin-bottom: 15px;
    border-left: 4px solid #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}
.stTextArea, .stFileUploader {
    border-radius: 10px !important;
}
h2 {
    color: #e0e0e0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-weight: 600;
}
h3 {
    color: #f0f0f0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-title">📄 Resume Screening AI</p>', unsafe_allow_html=True)
st.write("### Analyze resumes against job descriptions")

# Job Description
job_desc = st.text_area(
    "📝 Enter Job Description",
    height=150,
    placeholder="Paste the job description here..."
)

job_desc_clean = re.sub(r'[^a-z0-9\s]', ' ', job_desc.lower())

# File Upload
resume_files = st.file_uploader(
    "📂 Upload Resume(s)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if resume_files and job_desc_clean:
    results = []

    for file in resume_files:
        text = extract_text(file)

        if not text.strip():
            st.warning(f"⚠ Could not read {file.name}")
            continue

        match_details = get_match_details(text, job_desc_clean, skills_list)
        score = match_details["score"]
        skills = extract_skills(text, skills_list)


        missing_skills = match_details["missing_skills"]
        required_skills = match_details["job_skills"]
        matched_required_skills = match_details["matched_skills"]

        results.append((file.name, score, skills, missing_skills, required_skills, matched_required_skills))

    results = sorted(results, key=lambda x: x[1], reverse=True)

    st.write("## 🏆 Candidate Ranking")

    for name, score, skills, missing_skills, required_skills, matched_required_skills in results:
        with st.container():
            st.markdown("---")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"### 📄 {name}")

                st.progress(min(int(score), 100))
                st.write(f"### 🎯 Match Score: {score}%")

                if required_skills:
                    st.info(
                        f"📌 Required Skills: {', '.join(required_skills)}\n\n"
                        f"✅ Matched Required Skills: {', '.join(matched_required_skills) if matched_required_skills else 'None'}"
                    )

                st.success(f"✅ Skills Found: {', '.join(skills) if skills else 'None'}")

                if missing_skills:
                    st.error(f"❌ Missing Skills: {', '.join(missing_skills)}")
                else:
                    st.info("🎉 No missing skills")

            with col2:
                if score >= 70:
                    st.metric("Status", "Excellent 🔥")
                elif score >= 40:
                    st.metric("Status", "Good 👍")
                else:
                    st.metric("Status", "Needs Improvement ⚠")