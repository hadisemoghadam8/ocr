# C:\Users\ASUS\ocr_project\pipelines\image_pipeline.py

import os
import re
import cv2
# from utils.text_region import detect_text_region
from preprocess.analyzer import ImageAnalyzer
from preprocess.router import PipelineRouter
from postprocess.normalize_numbers import normalize_numbers
from engines.manager import OCRManager
from utils.rotation import detect_best_rotation
from postprocess.clean_text import clean_ocr_text
from postprocess.persian_fix import improve_persian_text, fix_safe_ocr_artifacts
from postprocess.english_fix import fix_english_ocr


from postprocess.rtl import (
    clean_bidi,
    fix_bidi_punctuation,
    smart_direction_fix
)
from utils.text_region import detect_text_region

class ImagePipeline:

    @staticmethod
    def _is_text_bad(text: str) -> bool:

        ratio = ImagePipeline._bad_text_ratio(text)

        print(f"[DEBUG] bad ratio={ratio:.2f}")

        return ratio > 0.35

    @staticmethod
    def _postprocess_text(text: str) -> str:

        text = clean_ocr_text(text)

        text = improve_persian_text(text)

        # normalize digits
        text = normalize_numbers(text)

        text = fix_english_ocr(text)

        text = clean_bidi(text)

        text = fix_bidi_punctuation(text)

        lines = []

        for line in text.splitlines():

            lines.append(
                smart_direction_fix(line)
            )

        return "\n".join(lines)
    
    @staticmethod
    def _bad_text_ratio(text: str) -> float:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return 1.0

        bad_lines = 0

        for line in lines:

            english_chars = sum(
                ch.isascii() and ch.isalpha()
                for ch in line
            )

            persian_chars = sum(
                '\u0600' <= ch <= '\u06FF'
                for ch in line
            )

            symbols = sum(
                not ch.isalnum() and not ch.isspace()
                for ch in line
            )

            garbage = len(
                re.findall(
                    r'[@#$%^&*_=+<>\\/|~`]',
                    line
                )
            )

            if len(line) < 3:
                bad_lines += 1
                continue

            if (
                symbols / max(len(line), 1) > 0.35
                and persian_chars < 2
            ):
                bad_lines += 1
                continue

            if garbage > 4:
                bad_lines += 1
                continue

            if (
                persian_chars < 2 and
                english_chars >= 6
            ):
                bad_lines += 1

        return bad_lines / max(len(lines), 1)


    @staticmethod
    def process(image_path: str) -> str:
        os.makedirs("output", exist_ok=True)

        # ---------------------------------
        # Load image
        # ---------------------------------
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("Could not load image")

        print("[INFO] Image loaded")

        # ---------------------------------
        # Rotation correction
        # ---------------------------------
        
        rotation_result = detect_best_rotation(image)
        image = rotation_result["image"]

        print(
            f"[INFO] Rotation corrected: "
            f"{rotation_result['angle']}°"
        )

        # ---------------------------------
        # Analyze image
        # ---------------------------------
        image_info = ImageAnalyzer.analyze(image)

        print("[INFO] Router analysis:")
        print(image_info)

        # ---------------------------------
        # Select preprocess pipeline
        # ---------------------------------
        route_result = PipelineRouter.route(
            image,
            image_info
        )

        processed_image = route_result["image"]

        scene_text = route_result.get(
            "scene_text",
            False
        )
        screenshot_mode = route_result.get(
            "screenshot",
            False
        )
        dark_mode = route_result.get(
            "dark_mode",
            False
        )



        if processed_image is None:
            processed_image = image

        cv2.imwrite(
            "output/debug_preprocess.jpg",
            processed_image
        )

        print("[INFO] Preprocessing completed")



        # ---------------------------------
        # Detect important text region
        # ---------------------------------

        if (
            not screenshot_mode
            and not scene_text
            and not dark_mode
        ):

            processed_image = detect_text_region(
                processed_image
            )


        # ---------------------------------
        # OCR
        # ---------------------------------

        if dark_mode:

            print("[INFO] Dark mode multi-pass OCR")

            # pass 1: روی تصویر پردازش‌شده
            text_1 = OCRManager.run_best_engine(processed_image)

            # pass 2: روی تصویر خامِ چرخش‌یافته (برای مقایسه)
            text_2 = OCRManager.run_best_engine(image)

            score_1 = len(text_1)
            score_2 = len(text_2)

            bad_1 = ImagePipeline._is_text_bad(text_1)
            bad_2 = ImagePipeline._is_text_bad(text_2)

            if bad_1 and not bad_2:
                raw_text = text_2

            elif bad_2 and not bad_1:
                raw_text = text_1

            else:
                ratio_1 = ImagePipeline._bad_text_ratio(text_1)
                ratio_2 = ImagePipeline._bad_text_ratio(text_2)

                # انتخاب بهترین بر اساس نسبت کیفیت
                raw_text = text_1 if ratio_1 <= ratio_2 else text_2

        else:
            # حالت عادی: فراخوانی استاندارد
            raw_text = OCRManager.run_best_engine(
                processed_image,
                scene_text=scene_text,
                screenshot_mode=screenshot_mode
            )

        # اگر متن خراب بود
        # OCR مستقیم روی تصویر خامِ rotate شده
        # ---------------------------------
        if (
            not scene_text and
            not screenshot_mode and
            ImagePipeline._is_text_bad(raw_text)
        ):

            print(
                "[WARNING] Preprocessed OCR bad -> "
                "trying raw rotated image"
            )

            raw_text_2 = OCRManager.run_best_engine(
                image,
                lang=['en', 'fa'],      # اضافه شد
                paragraph=False         # اضافه شد
            )

            if not ImagePipeline._is_text_bad(raw_text_2):

                raw_text = raw_text_2

                print(
                    "[INFO] Raw image OCR selected"
                )

        # ---------------------------------
        # Postprocess
        # ---------------------------------
        text = ImagePipeline._postprocess_text(raw_text)
        
        # ✅ اعمال اصلاحات ایمن فقط برای حالت‌های مبتنی بر اسکرین‌شات/UI
        # (شامل dark_mode و screenshot_mode)
        if dark_mode or screenshot_mode:
            text = fix_safe_ocr_artifacts(text)

        print("[INFO] Postprocess completed")
        return text