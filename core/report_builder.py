def build_report(name: str, resume_score: dict, code_review: dict | None) -> dict:
    resume_weight = 0.6
    code_weight   = 0.4

    if code_review and 'grade_score' in code_review:
        final = (resume_score['similarity'] * resume_weight) + \
                (code_review['grade_score'] * code_weight)
    else:
        final = resume_score['similarity']

    return {
        'name': name,
        'resume_score': resume_score,
        'code_review': code_review,
        'final_score': round(final, 4),
        'final_pct': round(final * 100, 1),
        'recommendation': _recommend(final)
    }

def _recommend(score: float) -> str:
    if score >= 0.72: return 'Strong Hire'
    if score >= 0.55: return 'Consider'
    if score >= 0.40: return 'Maybe'
    return 'Pass'