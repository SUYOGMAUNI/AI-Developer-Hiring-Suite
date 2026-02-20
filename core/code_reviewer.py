import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

PROMPT_TEMPLATE = """
You are a senior software engineer doing a strict code review.
Analyze the code below and respond ONLY with a valid JSON object.
No markdown fences, no explanation, no text outside the JSON.

Code to review:
---
{code}
---

Respond with exactly this JSON structure (all fields required):
{{
  "language": "detected programming language",
  "grade": "A or B or C or D or F",
  "grade_score": <float 0.0 to 1.0 matching grade: A=0.9, B=0.75, C=0.55, D=0.35, F=0.1>,
  "summary": "2-3 sentence overall honest assessment of code quality",
  "bugs": [
    "describe each bug clearly, e.g. 'Line 12: division by zero if denominator is 0'"
  ],
  "security_issues": [
    "describe each security issue, e.g. 'SQL query is not parameterized — SQL injection risk'"
  ],
  "style_issues": [
    "describe each style/readability issue, e.g. 'Variable name x is not descriptive'"
  ],
  "strengths": [
    "what the code does well, e.g. 'Good use of early returns reduces nesting'"
  ],
  "complexity": "Low / Medium / High",
  "maintainability": "Low / Medium / High",
  "refactored_snippet": "paste an improved version of the worst section only, or empty string if code is already clean"
}}

Grading rubric:
A = clean, secure, readable, no issues
B = minor style issues, no bugs
C = some bugs or security issues, mostly readable
D = multiple bugs, poor structure
F = broken, insecure, unreadable
"""

GRADE_SCORES = {
    'A': 0.92,
    'B': 0.75,
    'C': 0.55,
    'D': 0.35,
    'F': 0.10
}

MAX_CODE_LENGTH = 8000
MAX_RETRIES = 3
RETRY_DELAY = 2


def review_code(code: str) -> dict:
    if not code or not code.strip():
        return _error_response('No code was provided.')

    code = code[:MAX_CODE_LENGTH]

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = PROMPT_TEMPLATE.format(code=code)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=1500,
                )
            )

            text = response.text.strip()
            text = _strip_markdown(text)
            result = json.loads(text)
            result = _normalize(result)
            return result

        except json.JSONDecodeError:
            if attempt == MAX_RETRIES:
                return _error_response(
                    'AI returned an unparseable response after 3 attempts.',
                    raw=text if 'text' in dir() else ''
                )
            time.sleep(RETRY_DELAY)

        except Exception as e:
            err_str = str(e)

            if '429' in err_str or 'quota' in err_str.lower():
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt * 2)
                    continue
                return _error_response('Gemini API rate limit hit. Please wait a moment and try again.')

            if 'api_key' in err_str.lower() or 'API_KEY' in err_str:
                return _error_response('Invalid or missing GEMINI_API_KEY in your .env file.')

            if attempt == MAX_RETRIES:
                return _error_response(f'Gemini API error: {err_str}')

            time.sleep(RETRY_DELAY)

    return _error_response('All retry attempts failed.')


def _strip_markdown(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped in ('```json', '```', '~~~'):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned).strip()


def _normalize(result: dict) -> dict:
    grade = result.get('grade', 'C').upper()
    if grade not in GRADE_SCORES:
        grade = 'C'

    result['grade'] = grade
    result['grade_score'] = GRADE_SCORES[grade]

    list_fields = ['bugs', 'security_issues', 'style_issues', 'strengths']
    for field in list_fields:
        if field not in result or not isinstance(result[field], list):
            result[field] = []

    str_fields = ['language', 'summary', 'complexity', 'maintainability', 'refactored_snippet']
    for field in str_fields:
        if field not in result or not isinstance(result[field], str):
            result[field] = ''

    if not result.get('language'):
        result['language'] = 'Unknown'

    result['total_issues'] = (
        len(result['bugs']) +
        len(result['security_issues']) +
        len(result['style_issues'])
    )

    result['has_critical'] = len(result['bugs']) > 0 or len(result['security_issues']) > 0

    return result


def _error_response(message: str, raw: str = '') -> dict:
    return {
        'error': message,
        'raw': raw,
        'grade': 'N/A',
        'grade_score': 0.0,
        'language': 'Unknown',
        'summary': '',
        'bugs': [],
        'security_issues': [],
        'style_issues': [],
        'strengths': [],
        'complexity': 'Unknown',
        'maintainability': 'Unknown',
        'refactored_snippet': '',
        'total_issues': 0,
        'has_critical': False
    }