import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
import re
import os

def extract_total_pages(pdf_path):
    """Extracts total page count from 'Page X of Y' format"""
    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text("text")
        match = re.search(r"Page\s+\d+\s+of\s+(\d+)", text)
        if match:
            return int(match.group(1))
    return None

def split_pdf(pdf_path, total_pages):
    """Splits the PDF into separate files based on detected total pages"""
    if total_pages is None:
        return []

    reader = PdfReader(pdf_path)
    output_files = []
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    for i in range(total_pages):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])

        output_filename = f"media/split/{base_name}_part_{i+1}.pdf"
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)

        with open(output_filename, "wb") as output_pdf:
            writer.write(output_pdf)
        
        output_files.append(output_filename)

    return output_files
