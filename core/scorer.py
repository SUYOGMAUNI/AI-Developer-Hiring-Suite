import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from core.embedder import embed
import re

TECH_KEYWORDS = [
    'python', 'machine learning', 'deep learning', 'flask', 'docker',
    'kubernetes', 'react', 'sql', 'nosql', 'tensorflow', 'pytorch',
    'nlp', 'computer vision', 'api', 'git', 'linux', 'aws', 'gcp',
    'ci/cd', 'microservices', 'rest', 'graphql', 'typescript', 'java',
    'c++', 'rust', 'go', 'agile', 'scrum', 'system design'
]

def similarity_score(jd_text: str, resume_text: str) -> float:
    jd_vec = embed(jd_text).reshape(1, -1)
    res_vec = embed(resume_text).reshape(1, -1)
    score = cosine_similarity(jd_vec, res_vec)[0][0]
    return round(float(score), 4)

def keyword_gap(jd_text: str, resume_text: str) -> dict:
    jd_lower = jd_text.lower()
    res_lower = resume_text.lower()

    jd_keywords  = [k for k in TECH_KEYWORDS if k in jd_lower]
    present      = [k for k in jd_keywords if k in res_lower]
    missing      = [k for k in jd_keywords if k not in res_lower]

    return {
        'required': jd_keywords,
        'present': present,
        'missing': missing,
        'coverage': round(len(present) / len(jd_keywords), 2) if jd_keywords else 1.0
    }

def score_candidate(jd_text: str, resume_text: str) -> dict:
    sim   = similarity_score(jd_text, resume_text)
    gaps  = keyword_gap(jd_text, resume_text)
    label = _label(sim)

    return {
        'similarity': sim,
        'similarity_pct': round(sim * 100, 1),
        'label': label,
        'keyword_gap': gaps
    }

def _label(score: float) -> str:
    if score >= 0.75: return 'Excellent Match'
    if score >= 0.60: return 'Good Match'
    if score >= 0.45: return 'Moderate Match'
    return 'Weak Match'