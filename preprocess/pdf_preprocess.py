#C:\Users\ASUS\ocr_project\preprocess\pdf_preprocess.py
import os
import re
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path

from pipelines.pdf_pipeline import preprocess_pdf_page
from postprocess.persian_fix import advanced_score, improve_persian_text, fix_english_ocr


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POPPLER_PATH = os.path.join(
    BASE_DIR,
    "poppler-26.02.0",
    "Library",
    "bin"
)


def is_persian_line(text: str) -> bool:

    persian_chars = len(
        re.findall(r'[\u0600-\u06FF]', text)
    )

    english_chars = len(
        re.findall(r'[A-Za-z]', text)
    )

    return persian_chars > english_chars




def process_pdf(
    file_path,
    clean_ocr_text,
    clean_bidi,
    score_text,
    run_easyocr,
    normalize_numbers
):

    images = convert_from_path(
        file_path,
        dpi=400,
        poppler_path=POPPLER_PATH
    )

    all_text = []

    total_pages = len(images)

    for i, img in enumerate(images):

        print(
            f"[INFO] Processing PDF page "
            f"{i + 1}/{total_pages}"
        )

        gray, processed = preprocess_pdf_page(img)

        tess_text = pytesseract.image_to_string(
            processed,
            lang="fas+eng",
            config=r'--oem 1 --psm 4 -c preserve_interword_spaces=1'
        )

        easy_text = run_easyocr(img)

        tess_clean = clean_ocr_text(
            clean_bidi(tess_text)
        )

        easy_clean = clean_ocr_text(
            clean_bidi(easy_text)
        )

        tess_score = advanced_score(tess_clean)
        easy_score = advanced_score(easy_clean)

        text = (
            easy_clean
            if easy_score > tess_score
            else tess_clean
        )

        text = normalize_numbers(text)

        persian_chars = len(
            re.findall(r'[\u0600-\u06FF]', text)
        )

        english_chars = len(
            re.findall(r'[A-Za-z]', text)
        )

        # متن انگلیسی
        if english_chars > persian_chars:

            text = fix_english_ocr(text)

        # متن فارسی
        else:

            text = improve_persian_text(text)

        all_text.append(
            f"\n\n--- Page {i + 1} ---\n\n{text}\n"
        )

    final_text = "\n".join(all_text)

    return final_text