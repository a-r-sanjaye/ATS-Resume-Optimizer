# ATS Resume Optimizer

A Flask-based web application that uses Google Gemini AI to analyze resumes against job descriptions, calculate ATS compatibility scores, and generate improved, optimized resumes in PDF format.

## Features
- **AI Analysis**: Uses Google's Gemini models (1.5 Flash/Pro, 2.0 Flash) to critique resumes.
- **ATS Scoring**: calculates a match score (0-100%) based on job description keywords.
- **Resume Improvement**: Generates a completely rewritten, optimized resume.
- **PDF Download**: Download the improved resume as a cleanly formatted PDF.
- **History**: Keeps track of past analyses using a local SQLite database.
- **Visual Gauges**: Visual comparison of Original vs. Improved ATS scores.

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd chatbot_llm
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   Open [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure
- `app.py`: Main Flask application.
- `utils.py`: Logic for AI interaction and PDF generation.
- `templates/`: HTML files for the UI.
- `instance/ats_history.db`: Local database (auto-created).

## Dependencies
- flask
- google-genai
- fpdf2
- pdfplumber
- python-dotenv
- flask-sqlalchemy
