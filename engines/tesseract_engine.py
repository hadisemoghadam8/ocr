#C:\Users\ASUS\ocr_project\engines\tesseract_engine.py
import pytesseract

def run_tesseract(img, psm=6):
    """
    Run Tesseract OCR on an image.

    Parameters:
        img: numpy array image
        psm: Page Segmentation Mode (default=6)

    Returns:
        Extracted text (string)
    """

    config = f"--oem 3 --psm {psm}"

    text = pytesseract.image_to_string(
        img,
        lang="fas+eng",
        config=config
    )

    return text
