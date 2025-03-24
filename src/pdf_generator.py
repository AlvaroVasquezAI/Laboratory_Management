# pdf_generator.py
from fpdf import FPDF
import json

class PracticeReportGenerator:
    def __init__(self):
        self.pdf = FPDF()

    def generate_practice_pdf(self, practice_data, output_file):
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)
        
        # Add header
        self.pdf.cell(200, 10, txt=practice_data["title"], ln=1, align='C')
        self.pdf.cell(200, 10, txt=f"Subject: {practice_data['subject']}", ln=1, align='L')
        
        # Add content
        self.pdf.multi_cell(0, 10, txt=f"Objective:\n{practice_data['objective']}")
        self.pdf.multi_cell(0, 10, txt=f"Introduction:\n{practice_data['introduction']}")
        
        self.pdf.output(output_file)