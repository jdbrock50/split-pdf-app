import os
import re
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from PyPDF2 import PdfReader, PdfWriter
from .forms import PDFUploadForm
from .models import UploadedPDF
from .utils import extract_total_pages  # ❌ Removed duplicate import of split_pdf

def upload_pdf(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_instance = form.save()
            file_path = pdf_instance.file.path

            total_pages = extract_total_pages(file_path)
            if total_pages:
                split_files = process_pdf_split(file_path)  # ✅ Corrected function call
                return render(request, "splitter/result.html", {"split_files": split_files})
            else:
                return render(request, "splitter/upload.html", {"form": form, "error": "Could not determine total pages."})
    
    else:
        form = PDFUploadForm()

    return render(request, "splitter/upload.html", {"form": form})

def process_pdf_split(file_path):
    """Processes the PDF file and splits it based on section headers."""
    
    reader = PdfReader(file_path)
    section_starts = []

    # Find section start pages based on "Page 1 of X"
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""  
        if re.search(r"Page\s*1\s*of\s*\d+", text, re.IGNORECASE):
            section_starts.append(i)

    section_starts.append(len(reader.pages))  # Add last page index as final boundary

    split_files = []
    for i in range(len(section_starts) - 1):
        start_page = section_starts[i]
        end_page = section_starts[i + 1]
        
        writer = PdfWriter()
        for j in range(start_page, end_page):
            writer.add_page(reader.pages[j])

        output_filename = f"split_section_{i + 1}.pdf"
        output_path = os.path.join(settings.MEDIA_ROOT, "splits", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as output_pdf:
            writer.write(output_pdf)

        split_files.append(f"media/splits/{output_filename}")

    return split_files
