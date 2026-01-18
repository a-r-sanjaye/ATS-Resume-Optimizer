from utils import generate_pdf
import os

try:
    print("Testing PDF Generation...")
    content = {
        "Professional Summary": "Experienced software engineer...",
        "Experience": ["Developer at Company A", "Intern at Company B"]
    }
    pdf_bytes_io = generate_pdf(content)
    
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes_io.getvalue())
        
    print("PDF generated successfully: test_output.pdf")
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"General Error: {e}")
