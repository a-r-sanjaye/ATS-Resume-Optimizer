from fpdf import FPDF
from io import BytesIO
import os
import pdfplumber
import json
from dotenv import load_dotenv
from google import genai
import textwrap

# Explicitly define path to .env file to avoid CWD ambiguity
env_path = os.path.join(os.path.dirname(__file__), '.env')
# Force override ensures we read the file even if a stale env var exists
loaded = load_dotenv(env_path, override=True) 

class ResumePDF(FPDF):
    def header(self):
        # Optional: Add a top border or logo if needed
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf(improved_content):
    pdf = ResumePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Try to use Arial if available for better Unicode support, else fallback to Helvetica
    font_path = "C:/Windows/Fonts/arial.ttf"
    if os.path.exists(font_path):
        try:
            pdf.add_font("Arial", "", font_path, uni=True)
            pdf.add_font("Arial", "B", "C:/Windows/Fonts/arialbd.ttf", uni=True)
            main_font = "Arial"
        except Exception:
             main_font = "Helvetica"
    else:
        main_font = "Helvetica"

    pdf.set_font(main_font, "B", 16)
    pdf.cell(0, 10, "Improved Resume", ln=True, align="C")
    pdf.ln(5)

    if isinstance(improved_content, dict):
        for section, content in improved_content.items():
            # Section Header
            pdf.set_font(main_font, "B", 12)
            pdf.set_text_color(30, 144, 255) # DodgerBlue
            pdf.cell(0, 10, section.upper(), ln=True)
            
            # Content
            pdf.set_font(main_font, "", 10)
            pdf.set_text_color(0, 0, 0)
            
            # Helper to handle content types
            if isinstance(content, list):
                content_str = "\n".join([f"• {item}" for item in content])
            else:
                content_str = str(content)
            
            # Handle encoding for core fonts if not using Unicode font
            if main_font == "Helvetica":
                content_str = content_str.encode('latin-1', 'replace').decode('latin-1')

            pdf.multi_cell(0, 6, content_str)
            pdf.ln(3)
    else:
        # Fallback for simple string
        pdf.set_font(main_font, "", 10)
        content_str = str(improved_content)
        if main_font == "Helvetica":
             content_str = content_str.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, content_str)

    # Save to memory
    f = BytesIO()
    pdf.output(f)
    f.seek(0)
    return f

def extract_text_from_pdf(pdf_source):
    text = ""
    # pdfplumber.open() accepts path or file-like object
    with pdfplumber.open(pdf_source) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def get_api_key():
    # Try getting from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Fallback: Read manually if load_dotenv failed silently
    if not api_key:
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_API_KEY='):
                        api_key = line.strip().split('=', 1)[1]
                        break
        except Exception:
            pass
            
    return api_key.strip() if api_key else None

def analyze_resume(resume_text, job_description):
    api_key = get_api_key()
    
    if not api_key:
         return {
            "score": 0,
            "keywords": [],
            "improved_resume": {"Error": "API Key missing."},
            "ats_report": "System could not load Google API Key."
        }
         
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Act as an expert ATS (Applicant Tracking System) Resume Optimizer.
    Analyze the following resume against the provided job description.
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Provide a response in valid JSON format with the following keys:
    - "score": A numeric score from 0-100 representing the ORIGINAL match score.
    - "improved_score": A numeric score from 0-100 representing the Estimated Score AFTER applying the improvements.
    - "keywords": A list of missing keywords.
    - "improved_resume": A COMPLETE, READY-TO-USE RESUME content in dictionary format (sections as keys).
      The content MUST be tailored to match the JD and justify the 'improved_score'.
    - "ats_report": A detailed analysis.

    Ensure the response is purely JSON.
    """
    
    models_to_try = [
        'gemini-2.5-flash',
        'gemini-2.0-flash-exp',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro-latest',
        'gemini-2.0-flash',
        'gemini-1.5-flash'
    ]
    
    last_exception = None
    import re
    
    for model_name in models_to_try:
        try:
            print(f"DEBUG: Trying model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            
            # Robust JSON extraction
            text_response = response.text
            # Try to find JSON block between ```json and ``` or just { ... }
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Fallback: try to find the first '{' and last '}'
                json_match = re.search(r'(\{.*\})', text_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = text_response # Hope for the best

            # clean up any trailing commas or simple issues if possible (basic)
            return json.loads(json_str)
        except Exception as e:
            print(f"WARNING: Model {model_name} failed: {e}")
            last_exception = e
            continue
            
    return {
        "score": 0,
        "keywords": [],
        "improved_resume": {"Error": "Failed to generate resume."},
        "ats_report": f"All models failed. Last error: {str(last_exception)}"
    }
