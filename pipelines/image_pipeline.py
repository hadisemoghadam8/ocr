# C:\Users\ASUS\ocr_project\pipelines\image_pipeline.py

import os
import re
import cv2

from preprocess.analyzer import ImageAnalyzer
from preprocess.router import PipelineRouter

from engines.manager import OCRManager
from utils.rotation import detect_best_rotation
from postprocess.clean_text import clean_ocr_text
from postprocess.persian_fix import improve_persian_text
from postprocess.english_fix import fix_english_ocr
from postprocess.rtl import (
    clean_bidi,
    fix_bidi_punctuation,
    smart_direction_fix
)


class ImagePipeline:

    @staticmethod
    def _is_text_bad(text: str) -> bool:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return True

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

            valid_chars = english_chars + persian_chars + sum(
                ch.isdigit() for ch in line
            )

            garbage = len(
                re.findall(r'[@#$%^&*_=+<>\\/|~`]', line)
            )

            if len(line) < 3:
                bad_lines += 1
                continue

            if symbols / max(len(line), 1) > 0.35 and persian_chars < 2:
                bad_lines += 1
                continue

            if persian_chars < 2 and english_chars >= 3:
                bad_lines += 1
                continue

            if garbage > 4:
                bad_lines += 1
                continue

            if valid_chars < 2:
                bad_lines += 1
                continue

        ratio = bad_lines / max(len(lines), 1)

        print(
            f"[DEBUG] bad_lines={bad_lines} "
            f"total={len(lines)} "
            f"ratio={ratio:.2f}"
        )

        return ratio > 0.35

    @staticmethod
    def _postprocess_text(text: str) -> str:
        text = clean_ocr_text(text)
        text = improve_persian_text(text)
        text = fix_english_ocr(text)
        text = clean_bidi(text)
        text = fix_bidi_punctuation(text)

        lines = []
        for line in text.splitlines():
            lines.append(smart_direction_fix(line))

        return "\n".join(lines)

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
        processed_image = PipelineRouter.route(
            image,
            image_info
        )

        if processed_image is None:
            processed_image = image

        cv2.imwrite(
            "output/debug_preprocess.jpg",
            processed_image
        )
        print("[INFO] Preprocessing completed")


        # ---------------------------------
        # OCR روی preprocess
        # ---------------------------------
        raw_text = OCRManager.run_best_engine(
            processed_image
        )

        # ---------------------------------
        # اگر متن خراب بود
        # OCR مستقیم روی تصویر خامِ rotate شده
        # ---------------------------------
        if ImagePipeline._is_text_bad(raw_text):

            print(
                "[WARNING] Preprocessed OCR bad -> "
                "trying raw rotated image"
            )

            raw_text_2 = OCRManager.run_best_engine(
                image
            )

            if not ImagePipeline._is_text_bad(raw_text_2):

                raw_text = raw_text_2

                print(
                    "[INFO] Raw image OCR selected"
                )
            
        # ---------------------------------
        # Legacy-safe fallback:
        # اگر خروجی بد بود، یک بار روی تصویر چرخیده‌ی خام هم امتحان کن
        # ---------------------------------
        if ImagePipeline._is_text_bad(raw_text):
            print(
                "[WARNING] OCR quality poor -> "
                "retrying on rotated original image"
            )

            fallback_text = OCRManager.run_best_engine(image)

            if not ImagePipeline._is_text_bad(fallback_text):
                raw_text = fallback_text
                print("[INFO] Fallback OCR improved result")

        # ---------------------------------
        # Postprocess
        # ---------------------------------
        text = ImagePipeline._postprocess_text(raw_text)

        print("[INFO] Postprocess completed")

        return text
