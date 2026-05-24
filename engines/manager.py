# C:\Users\ASUS\ocr_project\engines\manager.py

from engines.tesseract_engine import run_tesseract
from engines.easyocr_engine import run_easyocr
from postprocess.scoring import score_ocr_text


class OCRManager:
    @staticmethod
    def normalize_ocr_output(text):

        if text is None:
            return ""

        # already string
        if isinstance(text, str):
            return text

        # EasyOCR list output
        if isinstance(text, list):

            cleaned = []

            for item in text:

                if not item:
                    continue

                if isinstance(item, str):
                    cleaned.append(item.strip())

                elif isinstance(item, tuple):

                    # detail=1 mode
                    if len(item) >= 2:
                        cleaned.append(str(item[1]).strip())

            return "\n".join(cleaned)

        return str(text)
    
    @staticmethod
    def run_best_engine(
        image,
        scene_text=False,
        screenshot_mode=False
    ):

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



        # ---------------------------------
        # Screenshot -> EasyOCR forced
        # ---------------------------------
        if screenshot_mode:
            print("[INFO] Screenshot mode -> EasyOCR forced")
            return OCRManager.normalize_ocr_output(
                run_easyocr(image, paragraph=True)
            )
        

        # ---------------------------------
        # Scene text همیشه EasyOCR
        # ---------------------------------

        # engines/manager.py
        if scene_text:
            print("[INFO] Scene text → EasyOCR forced")
            return OCRManager.normalize_ocr_output(
                run_easyocr(image, paragraph=True)  # ✅ برگشت به True برای مرتب‌سازی خطوط
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