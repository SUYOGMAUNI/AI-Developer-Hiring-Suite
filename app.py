import os
import uuid
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.utils import secure_filename
from core.resume_parser import extract_text_from_pdf
from core.scorer import score_candidate
from core.code_reviewer import review_code
from core.report_builder import build_report

app = Flask(__name__)
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
ALLOWED = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    jd_text = request.form.get('jd_text', '').strip()
    if not jd_text:
        return render_template('index.html', error='Please enter a job description.')

    files = request.files.getlist('resumes')
    if not files or all(f.filename == '' for f in files):
        return render_template('index.html', error='Please upload at least one resume.')

    reports = []
    for f in files:
        if f and allowed(f.filename):
            fname = secure_filename(f.filename)
            uid   = str(uuid.uuid4())[:8]
            path  = os.path.join(app.config['UPLOAD_FOLDER'], f'{uid}_{fname}')
            f.save(path)

            resume_text   = extract_text_from_pdf(path)
            resume_score  = score_candidate(jd_text, resume_text)
            candidate_name = fname.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()
            report = build_report(candidate_name, resume_score, None)
            reports.append(report)

            os.remove(path)

    reports.sort(key=lambda r: r['final_score'], reverse=True)
    return render_template('results.html', reports=reports, jd_preview=jd_text[:300])

@app.route('/code-review', methods=['POST'])
def code_review():
    code = request.form.get('code', '').strip()
    name = request.form.get('candidate_name', 'Candidate')
    if not code:
        return {'error': 'No code provided'}, 400
    result = review_code(code)
    return render_template('candidate.html', review=result, name=name)

if __name__ == '__main__':
    app.run(debug=True)