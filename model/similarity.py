from functools import lru_cache

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


@lru_cache(maxsize=1)
def _load_embedding_model():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def _get_embedding_similarity(resume, job_desc):
    model = _load_embedding_model()

    if model is None:
        return None

    embeddings = model.encode([resume, job_desc], normalize_embeddings=True)
    score = float(np.dot(embeddings[0], embeddings[1])) * 100
    return max(10.0, round(score, 2))


def _get_tfidf_similarity(resume, job_desc):
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([resume, job_desc])
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100

    if score == 0:
        return 10.0

    return round(score, 2)


def _normalize_skill(skill):
    return re.sub(r"\s+", " ", skill.strip().lower())


def _extract_skill_matches(text, skills_list):
    text = text.lower()
    normalized_skills = [_normalize_skill(skill) for skill in skills_list if skill.strip()]
    required_skills = sorted({skill for skill in normalized_skills if skill in text})
    return required_skills


def get_similarity(resume, job_desc, skills_list=None):
    if not resume.strip() or not job_desc.strip():
        return 10.0

    embedding_score = _get_embedding_similarity(resume, job_desc)

    if embedding_score is not None:
        semantic_score = embedding_score
    else:
        semantic_score = _get_tfidf_similarity(resume, job_desc)

    if not skills_list:
        return semantic_score

    resume_skills = _extract_skill_matches(resume, skills_list)
    job_skills = _extract_skill_matches(job_desc, skills_list)

    if not job_skills:
        return semantic_score

    matched_skills = [skill for skill in job_skills if skill in resume_skills]
    skill_coverage = (len(matched_skills) / len(job_skills)) * 100

    score = (skill_coverage * 0.7) + (semantic_score * 0.3)

    if matched_skills and len(matched_skills) == len(job_skills):
        score = max(score, 95.0)
    elif matched_skills:
        score += min(10.0, len(matched_skills) * 2.0)

    return round(min(score, 100.0), 2)


def get_match_details(resume, job_desc, skills_list=None):
    resume = resume or ""
    job_desc = job_desc or ""

    score = get_similarity(resume, job_desc, skills_list)

    if not skills_list:
        return {
            "score": score,
            "matched_skills": [],
            "job_skills": [],
            "missing_skills": [],
        }

    resume_skills = _extract_skill_matches(resume, skills_list)
    job_skills = _extract_skill_matches(job_desc, skills_list)
    matched_skills = [skill for skill in job_skills if skill in resume_skills]
    missing_skills = [skill for skill in job_skills if skill not in resume_skills]

    return {
        "score": score,
        "matched_skills": matched_skills,
        "job_skills": job_skills,
        "missing_skills": missing_skills,
    }