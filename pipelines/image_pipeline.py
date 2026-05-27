import os
import re
import cv2
from preprocess.analyzer import ImageAnalyzer
from preprocess.router import PipelineRouter
from postprocess.normalize_numbers import normalize_numbers
from engines.manager import OCRManager
from utils.rotation import detect_best_rotation
from postprocess.clean_text import clean_ocr_text
from postprocess.persian_fix import improve_persian_text, fix_safe_ocr_artifacts
from postprocess.english_fix import fix_english_ocr

from postprocess.rtl import clean_bidi, fix_bidi_punctuation
from utils.text_region import detect_text_region

class ImagePipeline:

    @staticmethod
    def _is_text_bad(text: str) -> bool:
        ratio = ImagePipeline._bad_text_ratio(text)
        print(f"[DEBUG] bad ratio={ratio:.2f}")
        return ratio > 0.35
    


    @staticmethod
    def _postprocess_text(text: str) -> str:

    # ✅ لاگ دیباگ: نمایش خروجی خام قبل از هر اصلاحی
        if '_' in text or 'د،' in text:
            print(f"[DEBUG] RAW OCR TEXT: {repr(text)}")

        text = clean_ocr_text(text)
        text = improve_persian_text(text)
        text = normalize_numbers(text)
        text = fix_english_ocr(text)
        text = clean_bidi(text)
        text = fix_bidi_punctuation(text)
        
        # ✅ اعمال جهت‌دهی هوشمند RTL برای خطوط فارسی
        from postprocess.rtl import smart_direction_fix
        lines = text.split('\n')
        text = '\n'.join(smart_direction_fix(line) for line in lines)
        
        return text.strip()

    
    @staticmethod
    def _bad_text_ratio(text: str) -> float:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return 1.0

        bad_lines = 0
        for line in lines:
            english_chars = sum(ch.isascii() and ch.isalpha() for ch in line)
            persian_chars = sum('\u0600' <= ch <= '\u06FF' for ch in line)
            symbols = sum(not ch.isalnum() and not ch.isspace() for ch in line)
            garbage = len(re.findall(r'[@#$%^&*_=+<>\\/|~`]', line))

            if len(line) < 3:
                bad_lines += 1
                continue
            if (symbols / max(len(line), 1) > 0.35 and persian_chars < 2):
                bad_lines += 1
                continue
            if garbage > 4:
                bad_lines += 1
                continue
            if (persian_chars < 2 and english_chars >= 6):
                bad_lines += 1

        return bad_lines / max(len(lines), 1)

    @staticmethod
    def process(image_path: str) -> str:
        os.makedirs("output", exist_ok=True)
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not load image")
        print("[INFO] Image loaded")

        rotation_result = detect_best_rotation(image)
        image = rotation_result["image"]
        print(f"[INFO] Rotation corrected: {rotation_result['angle']}°")

        image_info = ImageAnalyzer.analyze(image)
        print("[INFO] Router analysis:")
        print(image_info)

        route_result = PipelineRouter.route(image, image_info)
        processed_image = route_result["image"]

        scene_text = route_result.get("scene_text", False)
        screenshot_mode = route_result.get("screenshot", False)
        dark_mode = route_result.get("dark_mode", False)

        if processed_image is None:
            processed_image = image

        cv2.imwrite("output/debug_preprocess.jpg", processed_image)
        print("[INFO] Preprocessing completed")

        if (not screenshot_mode and not scene_text and not dark_mode):
            processed_image = detect_text_region(processed_image)

        if dark_mode:
            print("[INFO] Dark mode multi-pass OCR")
            text_1 = OCRManager.run_best_engine(processed_image)
            text_2 = OCRManager.run_best_engine(image)

            if ImagePipeline._is_text_bad(text_1) and not ImagePipeline._is_text_bad(text_2):
                raw_text = text_2
            elif ImagePipeline._is_text_bad(text_2) and not ImagePipeline._is_text_bad(text_1):
                raw_text = text_1
            else:
                ratio_1 = ImagePipeline._bad_text_ratio(text_1)
                ratio_2 = ImagePipeline._bad_text_ratio(text_2)
                raw_text = text_1 if ratio_1 <= ratio_2 else text_2
        else:
            raw_text = OCRManager.run_best_engine(
                processed_image,
                scene_text=scene_text,
                screenshot_mode=screenshot_mode
            )

        if (not scene_text and not screenshot_mode and ImagePipeline._is_text_bad(raw_text)):
            print("[WARNING] Preprocessed OCR bad -> trying raw rotated image")
            raw_text_2 = OCRManager.run_best_engine(image, lang=['en', 'fa'], paragraph=False)
            if not ImagePipeline._is_text_bad(raw_text_2):
                raw_text = raw_text_2
                print("[INFO] Raw image OCR selected")

        text = ImagePipeline._postprocess_text(raw_text)
        
        if dark_mode or screenshot_mode:
            text = fix_safe_ocr_artifacts(text)

        print("[INFO] Postprocess completed")
        return text