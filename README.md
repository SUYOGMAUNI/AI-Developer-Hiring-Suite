# AI Developer Hiring Suite

A full-stack NLP-powered recruitment tool that ranks engineering candidates by semantic fit and delivers AI-powered code reviews — built with Python, Flask, and sentence-transformers.

![Python](https://img.shields.io/badge/Python-3.11-3776ab?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini_API-1.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-22c55e?style=flat-square)

---

## What It Does

| Step | Action |
|------|--------|
| 1 | Paste a **Job Description** |
| 2 | Upload **candidate resumes** (PDF, multiple at once) |
| 3 | Get candidates **ranked by semantic fit** with % scores |
| 4 | See **keyword gap analysis** — what's present vs. missing per candidate |
| 5 | Paste a **code sample** → get a structured AI code review graded A–F |

No keyword-stuffing tricks. Semantic embeddings understand *meaning*, so "ML engineer" and "machine learning developer" score correctly against each other.

---

## Demo

> Upload a JD + resumes → ranked results in seconds

```
Job Description
      │
      ▼
sentence-transformers (all-MiniLM-L6-v2)
      │
      ▼
384-dim embedding  ◄──── also applied to each resume
      │
      ▼
Cosine Similarity Score (0.0 → 1.0)
      │
      ▼
Ranked list + keyword gap + recommendation
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.1 |
| NLP / Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` |
| Similarity | scikit-learn cosine similarity |
| PDF Parsing | PyMuPDF |
| Code Review | Google Gemini 1.5 Flash API |
| Frontend | Jinja2, custom CSS (dark tech-noir) |
| Deployment | Render (Gunicorn) |

---

## Project Structure

```
hiring-suite/
├── app.py                    # Flask routes
├── requirements.txt
├── .env                      # GEMINI_API_KEY (not committed)
├── Procfile                  # Render deployment
│
├── core/
│   ├── resume_parser.py      # PDF → clean text
│   ├── embedder.py           # loads model, computes embeddings
│   ├── scorer.py             # cosine similarity + keyword gap
│   ├── code_reviewer.py      # Gemini API + response parser
│   └── report_builder.py     # assembles final candidate report
│
├── templates/
│   ├── index.html            # upload form
│   ├── results.html          # ranked candidates
│   └── candidate.html        # code review detail
│
├── static/
│   └── style.css
│
└── uploads/                  # temp storage (gitignored)
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/SUYOGMAUNI/ai-developer-hiring-suite
cd ai-developer-hiring-suite
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> `sentence-transformers` will download the `all-MiniLM-L6-v2` model (~80MB) on first run. This only happens once.

### 4. Set up environment variables

Create a `.env` file in the root directory:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com/app/apikey)

### 5. Run the app

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

---

## How Scoring Works

### Resume Ranking

Similarity is computed as cosine distance between the JD embedding and each resume embedding:

```
Final Score = cosine_similarity(embed(JD), embed(resume))
```

Scores range from 0.0 to 1.0 and are converted to percentages.

| Score | Label |
|-------|-------|
| ≥ 75% | Excellent Match |
| ≥ 60% | Good Match |
| ≥ 45% | Moderate Match |
| < 45% | Weak Match |

### Combined Score (with code review)

```
Final = (similarity × 0.6) + (code_grade_score × 0.4)
```

| Final Score | Recommendation |
|-------------|---------------|
| ≥ 72% | Strong Hire |
| ≥ 55% | Consider |
| ≥ 40% | Maybe |
| < 40% | Pass |

### Code Review Grades

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 0.92 | Clean, secure, readable |
| B | 0.75 | Minor style issues only |
| C | 0.55 | Some bugs or security issues |
| D | 0.35 | Multiple bugs, poor structure |
| F | 0.10 | Broken, insecure, unreadable |

---

## Deployment on Render

1. Push your repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `gunicorn app:app`
6. Add environment variable: `GEMINI_API_KEY=your_key`
7. Deploy

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for code reviews |

---

## Requirements

```
flask==3.1.0
python-dotenv==1.0.1
sentence-transformers==3.3.1
PyMuPDF==1.25.3
google-generativeai==0.8.3
numpy==1.26.4
scikit-learn==1.6.1
gunicorn==23.0.0
```

---

## License

MIT License — free to use, modify, and distribute.

---

## Built by

**[Suyog Mauni](https://suyogmauni.com.np/)** — Computer Engineering Student & AI Enthusiast
