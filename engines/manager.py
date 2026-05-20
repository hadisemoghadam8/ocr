# C:\Users\ASUS\ocr_project\engines\manager.py

from engines.tesseract_engine import run_tesseract
from engines.easyocr_engine import run_easyocr
from postprocess.scoring import score_ocr_text


class OCRManager:

    @staticmethod
    def normalize_ocr_output(text):

        if text is None:
            return ""

        if isinstance(text, str):
            return text

        if isinstance(text, list):

            if len(text) == 0:
                return ""

            # EasyOCR output: [(text, conf), ...]
            if isinstance(text[0], tuple):
                return " ".join(
                    [item[1] for item in text if isinstance(item, tuple) and len(item) > 1]
                )

            return " ".join(map(str, text))

        return str(text)

    @staticmethod
    def run_best_engine(image):

        # -----------------------------
        # Tesseract
        # -----------------------------
        tess_text = OCRManager.normalize_ocr_output(
            run_tesseract(image)
        )

        # -----------------------------
        # EasyOCR
        # -----------------------------
        easy_text = OCRManager.normalize_ocr_output(
            run_easyocr(image)
        )

        # -----------------------------
        # Score outputs
        # -----------------------------
        tess_score = score_ocr_text(tess_text)
        easy_score = score_ocr_text(easy_text)

        print(f"[INFO] Tesseract score: {tess_score}")
        print(f"[INFO] EasyOCR score: {easy_score}")

        # -----------------------------
        # Select best result
        # -----------------------------
        if easy_score > tess_score:
            print("[INFO] EasyOCR selected")
            return easy_text

        print("[INFO] Tesseract selected")
        return tess_text