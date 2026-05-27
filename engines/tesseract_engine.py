# C:\Users\ASUS\ocr_project\engines\tesseract_engine.py

import pytesseract

def run_tesseract(img, psm=6):
    """
    Run Tesseract OCR optimized for scanned Persian documents.
    """
    # LSTM mode with custom page segmentation
    config = f"--oem 1 --psm {psm}"

    # Use Persian only to prevent Latin character artifacts
    text = pytesseract.image_to_string(
        img,
        lang="fas",
        config=config
    )

    return text