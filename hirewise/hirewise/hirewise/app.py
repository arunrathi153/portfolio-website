import os
import uuid
import tempfile
from flask import Flask, request, render_template, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from resume_reader import extract_text
from resume_parser import extract_resume_details
from job_matcher import rank_candidates

# PDF generation
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
UPLOAD_FOLDER = tempfile.gettempdir()

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-secure-random-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_presets():
    return {
        'Data Scientist (example)': 'python, machine learning, deep learning, sql, pandas',
        'Backend (example)': 'python, django, flask, sql, aws',
        'Frontend (example)': 'javascript, react, html, css'
    }
@app.route('/')
def landing():
    return render_template('landing.html')
@app.route('/match', methods=['GET', 'POST'])
def index():
    # Pre-filled values (used if form reloads after validation error)
    form_data = {
        'job_skills': '',
        'experience': '',
        'education': ''
    }

    if request.method == 'POST':
        # Get job requirement fields (preserve them)
        form_data['job_skills'] = request.form.get('job_skills', '').strip()
        form_data['experience'] = request.form.get('experience', '').strip()
        form_data['education'] = request.form.get('education', '').strip()

        # Parse experience safely as float (allow decimals like 0.5)
        try:
            req_experience = float(form_data['experience']) if form_data['experience'] != '' else 0.0
            if req_experience < 0:
                raise ValueError("negative")
        except Exception:
            flash("⚠ Invalid value for required experience. Please enter a number (e.g. 2 or 1.5).")
            return render_template('index.html', presets=get_presets(), form_data=form_data)

        # Uploaded resumes
        uploaded = request.files.getlist('resumes') or []
        # Some browsers may produce a single empty FileStorage; treat empty names as no files
        if not uploaded or all((not f) or (not getattr(f, "filename", "")) for f in uploaded):
            flash("⚠ Please upload at least one resume file.")
            return render_template('index.html', presets=get_presets(), form_data=form_data)

        saved_files = []
        resumes_parsed = []

        # Save files with unique names (keep original name for display)
        for f in uploaded:
            if not f:
                continue
            fname = getattr(f, "filename", "")
            if fname and allowed_file(fname):
                filename = secure_filename(fname)
                unique_name = f"{uuid.uuid4().hex}_{filename}"
                path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                try:
                    f.save(path)
                    saved_files.append((filename, path))
                except Exception as e:
                    flash(f"Failed to save uploaded file {filename}: {e}")
            else:
                if fname:
                    flash(f"Skipping unsupported file type: {fname}")

        if not saved_files:
            flash("⚠ No valid resume files were uploaded (supported: .pdf, .txt, .docx).")
            return render_template('index.html', presets=get_presets(), form_data=form_data)

        # Parse resumes
        for original_name, path in saved_files:
            text = extract_text(path)
            if not text:
                resumes_parsed.append({
                    'file_name': original_name,
                    'skills': [],
                    'experience': 0.0,
                    'education': [],
                    'raw_text': ''
                })
            else:
                parsed = extract_resume_details(text)
                parsed['file_name'] = original_name
                # simple heuristic for name
                first_lines = [l.strip() for l in text.splitlines() if l.strip()]
                if first_lines:
                    parsed['name'] = first_lines[0][:80]
                resumes_parsed.append(parsed)

        job_req = {
            'skills': form_data['job_skills'],
            'experience': req_experience,
            'education': form_data['education']
        }

        ranked = rank_candidates(resumes_parsed, job_req)

        # PDF report path
        pdf_filename = f"ranked_results_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

        # Generate PDF in landscape
        try:
            doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter))
            elements = []

            styles = getSampleStyleSheet()
            styleN = styles['Normal']
            styleN.wordWrap = 'CJK'  # Enable text wrapping

            elements.append(Paragraph("Ranked Candidates Report", styles['Title']))
            elements.append(Spacer(1, 12))

            # Table header (matches HTML)
            data = [[
                "Rank", "Name", "File", "Total Score", "Matched Skills",
                "Skills %", "Experience", "Education", "Years Exp"
            ]]

            # Table rows
            for idx, r in enumerate(ranked, start=1):
                years_value = r['details'].get('experience', 0)
                # format years nicely (int if whole, else one decimal)
                if isinstance(years_value, (int, float)):
                    years_str = str(int(years_value)) if float(years_value).is_integer() else f"{round(years_value, 1)}"
                else:
                    years_str = str(years_value)
                data.append([
                    Paragraph(str(idx), styleN),
                    Paragraph(r.get('name', ''), styleN),
                    Paragraph(r.get('file_name', ''), styleN),
                    Paragraph(str(r['score']['total_score']), styleN),
                    Paragraph(", ".join(r['score']['matched_skills']), styleN),
                    Paragraph(str(r['score']['skills_score']), styleN),
                    Paragraph("Matched" if r['score'].get('experience_match') else "Not Matched", styleN),
                    Paragraph("Matched" if r['score'].get('education_match') else "Not Matched", styleN),
                    Paragraph(years_str, styleN)
                ])

            # Column widths for better fit
            col_widths = [40, 100, 140, 60, 170, 60, 70, 70, 60]

            table = Table(data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ]))
            elements.append(table)

            doc.build(elements)
        except Exception as e:
            flash(f"Failed to generate PDF report: {e}")
            return render_template('index.html', presets=get_presets(), form_data=form_data)

        # Render results page with PDF link
        return render_template(
            'results.html',
            ranked=ranked,
            csv_download=True,
            csv_name=os.path.basename(pdf_path)
        )

    # GET request: show blank form (or with presets)
    return render_template('index.html',  form_data=form_data)

@app.route('/download/<csv_name>')
def download_csv(csv_name):
    path = os.path.join(app.config['UPLOAD_FOLDER'], csv_name)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        flash("PDF not found.")
        return redirect(url_for('index'))

@app.route('/health')
def health():
    return "OK", 200
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=False, port=5000)
