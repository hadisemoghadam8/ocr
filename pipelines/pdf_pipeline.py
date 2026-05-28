
import os
import re
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path

from postprocess.clean_text import clean_ocr_text
from postprocess.rtl import clean_bidi
from postprocess.english_fix import fix_english_ocr
from postprocess.persian_fix import improve_persian_text, fix_safe_ocr_artifacts, advanced_score
from postprocess.normalize_numbers import normalize_numbers
from engines.easyocr_engine import run_easyocr

# Resolve Poppler path relative to the project structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POPPLER_PATH = os.path.join(
    BASE_DIR, "..", "poppler-26.02.0", "Library", "bin"
)


class PDFPipeline:
    """
    PDF processing pipeline using dual OCR engines and adaptive post-processing.
    """

    @staticmethod
    def preprocess_pdf_page(img):
        """
        Apply preprocessing to enhance scanned PDF pages for OCR.
        Steps: upscale, denoise, CLAHE, sharpen, adaptive threshold, and noise removal.
        """
        img_np = np.array(img)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        # Auto upscale based on image width to improve character clarity
        h, w = gray.shape
        scale = 2.2 if w < 1800 else 1.4
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        # Remove high-frequency noise
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # Enhance local contrast for better binarization
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # Mild sharpening to improve edge definition
        blur = cv2.GaussianBlur(gray, (0, 0), 1.2)
        sharp = cv2.addWeighted(gray, 1.6, blur, -0.6, 0)

        # Binarize using adaptive thresholding
        th = cv2.adaptiveThreshold(
            sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 5
        )

        # Remove small noise artifacts
        kernel = np.ones((2, 2), np.uint8)
        th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

        return gray, th

    @staticmethod
    def is_persian_dominant(text: str) -> bool:
        """Check if Persian characters dominate the extracted text."""
        persian = len(re.findall(r'[\u0600-\u06FF]', text))
        english = len(re.findall(r'[A-Za-z]', text))
        return persian > english * 2

    @staticmethod
    def process(file_path):
        """
        Process a PDF file and return extracted text.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            str: Extracted text with page separators.
        """
        # Convert PDF pages to high-DPI images
        images = convert_from_path(file_path, dpi=400, poppler_path=POPPLER_PATH)

        all_text = []
        total_pages = len(images)

        for i, img in enumerate(images):
            print(f"[INFO] Processing PDF page {i + 1}/{total_pages}")

            gray, processed = PDFPipeline.preprocess_pdf_page(img)

            # Rotation is handled upstream. Flipping here would mirror the text.

            # Run Tesseract optimized for structured documents
            tess_text = pytesseract.image_to_string(
                processed, lang="fas+eng",
                config=r'--oem 1 --psm 4 -c preserve_interword_spaces=1'
            )

            # Run EasyOCR for complex layouts or scene text
            easy_text = run_easyocr(gray)
            if easy_text is None or not isinstance(easy_text, str):
                easy_text = ""

            # Clean and score both outputs
            tess_clean = clean_ocr_text(clean_bidi(tess_text))
            easy_clean = clean_ocr_text(clean_bidi(easy_text))

            tess_score = advanced_score(tess_clean)
            easy_score = advanced_score(easy_clean)

            text = easy_clean if easy_score > tess_score else tess_clean
            text = normalize_numbers(text)

            # Apply language-specific post-processing
            if PDFPipeline.is_persian_dominant(text):
                text = improve_persian_text(text)
                text = fix_safe_ocr_artifacts(text)
            else:
                text = fix_english_ocr(text)

            all_text.append(f"\n\n{'='*20} Page {i + 1} {'='*20}\n\n{text}")

        return "\n".join(all_text)