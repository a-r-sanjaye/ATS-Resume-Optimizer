from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from io import BytesIO
from werkzeug.utils import secure_filename
from utils import extract_text_from_pdf, analyze_resume, generate_pdf
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ats_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_filename = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    analysis_json = db.Column(db.Text, nullable=False) # Storing JSON as string
    file_data = db.Column(db.LargeBinary) # Store PDF binary data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Ensure upload directory exists - REMOVED for DB storage
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume' not in request.files:
            return redirect(request.url)
        
        file = request.files['resume']
        job_desc = request.form.get('job_desc')
        
        if file.filename == '':
            return redirect(request.url)
            
        if file and job_desc:
            filename = secure_filename(file.filename)
            
            # Read file into memory
            file_bytes = file.read()
            
            # Process content from memory
            try:
                # Create a stream for pdfplumber
                file_stream = BytesIO(file_bytes)
                resume_text = extract_text_from_pdf(file_stream)
                
                analysis_result = analyze_resume(resume_text, job_desc)
                
                # Save to Database with file data
                new_analysis = Analysis(
                    resume_filename=filename,
                    job_description=job_desc,
                    analysis_json=json.dumps(analysis_result),
                    file_data=file_bytes
                )
                db.session.add(new_analysis)
                db.session.commit()
                
                return render_template('result.html', 
                                       score=analysis_result.get('score', 0),
                                       improved_score=analysis_result.get('improved_score', 'N/A'),
                                       keywords=analysis_result.get('keywords', []),
                                       improved_resume=analysis_result.get('improved_resume', ''),
                                       ats_report=analysis_result.get('ats_report', ''),
                                       analysis_id=new_analysis.id)
            except Exception as e:
                return f"An error occurred: {e}"
                
    return render_template('index.html')

@app.route('/history')
def history():
    analyses = Analysis.query.order_by(Analysis.created_at.desc()).all()
    return render_template('history.html', analyses=analyses)

@app.route('/history/<int:id>')
def view_history(id):
    analysis = Analysis.query.get_or_404(id)
    analysis_result = json.loads(analysis.analysis_json)
    return render_template('result.html', 
                           score=analysis_result.get('score', 0),
                           improved_score=analysis_result.get('improved_score', 'N/A'),
                           keywords=analysis_result.get('keywords', []),
                           improved_resume=analysis_result.get('improved_resume', ''),
                           ats_report=analysis_result.get('ats_report', ''),
                           analysis_id=analysis.id,
                           timestamp=analysis.created_at)

@app.route('/download/<int:id>')
def download_resume(id):
    analysis = Analysis.query.get_or_404(id)
    if not analysis.file_data:
        return "File not found", 404
        
    return send_file(
        BytesIO(analysis.file_data),
        download_name=analysis.resume_filename,
        as_attachment=True
    )

@app.route('/download_improved/<int:id>')
def download_improved_resume(id):
    analysis = Analysis.query.get_or_404(id)
    analysis_result = json.loads(analysis.analysis_json)
    improved_content = analysis_result.get('improved_resume', 'No improvement data available.')
    
    file_stream = generate_pdf(improved_content)
    
    return send_file(
        file_stream,
        mimetype='application/pdf',
        download_name=f"Improved_{analysis.resume_filename}.pdf",
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)
