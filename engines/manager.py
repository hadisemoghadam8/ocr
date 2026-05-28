
from engines.tesseract_engine import run_tesseract
from engines.easyocr_engine import run_easyocr
from postprocess.scoring import score_ocr_text


class OCRManager:
    @staticmethod
    def normalize_ocr_output(text):
        """Convert various OCR output formats into a single string."""
        if text is None:
            return ""

        if isinstance(text, str):
            return text

        # Handle list outputs (EasyOCR returns list of tuples/strings)
        if isinstance(text, list):
            cleaned = []
            for item in text:
                if not item:
                    continue
                if isinstance(item, str):
                    cleaned.append(item.strip())
                elif isinstance(item, tuple):
                    # Extract text from detail=1 output format
                    if len(item) >= 2:
                        cleaned.append(str(item[1]).strip())
            return "\n".join(cleaned)

        return str(text)
    
    @staticmethod
    def run_best_engine(image, scene_text=False, screenshot_mode=False):
        # Get normalized outputs from both engines
        tess_text = OCRManager.normalize_ocr_output(run_tesseract(image))
        easy_text = OCRManager.normalize_ocr_output(run_easyocr(image))

        # Force EasyOCR for screenshots (better at detecting UI/text overlays)
        if screenshot_mode:
            print("[INFO] Screenshot mode -> EasyOCR forced")
            return OCRManager.normalize_ocr_output(run_easyocr(image, paragraph=True))
        
        # Force EasyOCR for natural scene text
        if scene_text:
            print("[INFO] Scene text -> EasyOCR forced")
            return OCRManager.normalize_ocr_output(run_easyocr(image, paragraph=True))

        # Score and compare outputs
        tess_score = score_ocr_text(tess_text)
        easy_score = score_ocr_text(easy_text)

        print(f"[INFO] Tesseract score: {tess_score}")
        print(f"[INFO] EasyOCR score: {easy_score}")

        # Return the engine with the higher confidence score
        if easy_score > tess_score:
            print("[INFO] EasyOCR selected")
            return easy_text

        print("[INFO] Tesseract selected")
        return tess_text