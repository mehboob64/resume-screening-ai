import streamlit as st
import re
from utils.parser import extract_text
from model.similarity import get_similarity
from model.skills import extract_skills

# Page config
st.set_page_config(
    page_title="Resume Screening AI",
    page_icon="📄",
    layout="wide"
)

# Load skills
with open("data/skills.txt") as f:
    skills_list = [s.strip().lower() for s in f.readlines()]

# Custom CSS
st.markdown("""
<style>
.main-title {
    font-size: 40px;
    font-weight: bold;
    text-align: center;
}
.score-box {
    padding: 15px;
    border-radius: 12px;
    background-color: #1e1e1e;
    margin-bottom: 10px;
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

        score = get_similarity(text, job_desc_clean)
        skills = extract_skills(text, skills_list)

        missing_skills = [
            s for s in skills_list if s in job_desc_clean and s not in skills
        ]

        results.append((file.name, score, skills, missing_skills))

    results = sorted(results, key=lambda x: x[1], reverse=True)

    st.write("## 🏆 Candidate Ranking")

    for name, score, skills, missing_skills in results:
        with st.container():
            st.markdown("---")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"### 📄 {name}")

                st.progress(min(int(score), 100))
                st.write(f"### 🎯 Match Score: {score}%")

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