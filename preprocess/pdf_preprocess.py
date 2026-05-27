#C:\Users\ASUS\ocr_project\preprocess\pdf_preprocess.py
import os
import re
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path

from pipelines.pdf_pipeline import preprocess_pdf_page
from postprocess.persian_fix import advanced_score, improve_persian_text, fix_english_ocr

# Resolve Poppler path relative to project structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POPPLER_PATH = os.path.join(BASE_DIR, "poppler-26.02.0", "Library", "bin")


def is_persian_line(text: str) -> bool:
    """Check if a line contains more Persian than English characters."""
    persian_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    english_chars = len(re.findall(r'[A-Za-z]', text))
    return persian_chars > english_chars


def process_pdf(
    file_path,
    clean_ocr_text,
    clean_bidi,
    score_text,
    run_easyocr,
    normalize_numbers
):
    """
    Process a PDF file using dependency-injected OCR and post-processing functions.
    
    This functional approach allows flexible testing and alternative pipeline usage.
    """
    # Convert PDF pages to high-DPI images for better OCR accuracy
    images = convert_from_path(file_path, dpi=400, poppler_path=POPPLER_PATH)

    all_text = []
    total_pages = len(images)

    for i, img in enumerate(images):
        print(f"[INFO] Processing PDF page {i + 1}/{total_pages}")

        # Apply preprocessing to enhance text clarity
        gray, processed = preprocess_pdf_page(img)

        # Run Tesseract optimized for structured document layouts
        tess_text = pytesseract.image_to_string(
            processed,
            lang="fas+eng",
            config=r'--oem 1 --psm 4 -c preserve_interword_spaces=1'
        )

        # Run EasyOCR for complex or scene-like text regions
        easy_text = run_easyocr(img)

        # Clean and normalize both outputs
        tess_clean = clean_ocr_text(clean_bidi(tess_text))
        easy_clean = clean_ocr_text(clean_bidi(easy_text))

        # Select the engine with the higher quality score
        tess_score = advanced_score(tess_clean)
        easy_score = advanced_score(easy_clean)

        text = easy_clean if easy_score > tess_score else tess_clean
        text = normalize_numbers(text)

        # Apply language-specific post-processing
        persian_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        english_chars = len(re.findall(r'[A-Za-z]', text))

        if english_chars > persian_chars:
            text = fix_english_ocr(text)
        else:
            text = improve_persian_text(text)

        # Append page separator for readable multi-page output
        all_text.append(f"\n\n--- Page {i + 1} ---\n\n{text}\n")

    return "\n".join(all_text)