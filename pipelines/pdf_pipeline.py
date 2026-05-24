# pipelines/pdf_pipeline.py
"""
PDF Pipeline for OCR Project
----------------------------
پردازش PDF با پیش‌پردازش قوی + دو موتور OCR + پست‌پروسس هوشمند
سازگار با ساختار کلاسیک پروژه و main.py
"""

import os
import re
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path

# ✅ ایمپورت تمام توابع کمکی (خودکفا - بدون نیاز به پاس دادن پارامتر)
from postprocess.clean_text import clean_ocr_text
from postprocess.rtl import clean_bidi
from postprocess.english_fix import fix_english_ocr
from postprocess.persian_fix import improve_persian_text, fix_safe_ocr_artifacts, advanced_score
from postprocess.normalize_numbers import normalize_numbers
from engines.easyocr_engine import run_easyocr


# مسیر Poppler (نسبی و قابل حمل)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POPPLER_PATH = os.path.join(
    BASE_DIR,
    "..",
    "poppler-26.02.0",
    "Library",
    "bin"
)


class PDFPipeline:
    """
    پایپ‌لاین پردازش PDF با معماری کلاسیک و سازگار با main.py
    
    Usage:
        result = PDFPipeline.process("samples/afternoon.pdf")
    """

    @staticmethod
    def preprocess_pdf_page(img):
        """
        پیش‌پردازش قوی برای صفحات اسکن‌شده
        شامل: upscale هوشمند، denoise، CLAHE، sharpen، adaptive threshold
        """
        
        img_np = np.array(img)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        # -----------------------------
        # ۱. Auto Upscale هوشمند
        # -----------------------------
        h, w = gray.shape
        scale = 2.2 if w < 1800 else 1.4
        gray = cv2.resize(
            gray, None,
            fx=scale, fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

        # -----------------------------
        # ۲. Denoise پیشرفته
        # -----------------------------
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # -----------------------------
        # ۳. Local Contrast (CLAHE)
        # -----------------------------
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # -----------------------------
        # ۴. Sharpen ملایم
        # -----------------------------
        blur = cv2.GaussianBlur(gray, (0, 0), 1.2)
        sharp = cv2.addWeighted(gray, 1.6, blur, -0.6, 0)

        # -----------------------------
        # ۵. Adaptive Threshold
        # -----------------------------
        th = cv2.adaptiveThreshold(
            sharp, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 5
        )

        # -----------------------------
        # ۶. Morphology Cleanup (حذف نویز ریز)
        # -----------------------------
        kernel = np.ones((2, 2), np.uint8)
        th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

        return gray, th

    @staticmethod
    def is_persian_dominant(text: str) -> bool:
        """
        تشخیص زبان غالب متن برای انتخاب پست‌پروسس مناسب
        """
        persian = len(re.findall(r'[\u0600-\u06FF]', text))
        english = len(re.findall(r'[A-Za-z]', text))
        return persian > english * 2

    @staticmethod
    def process(file_path):
        """
        تابع اصلی پردازش PDF - سازگار با فراخوانی از main.py
        
        Args:
            file_path (str): مسیر فایل PDF
            
        Returns:
            str: متن استخراج‌شده با فرمت‌بندی صفحات
        """
        
        # تبدیل PDF به لیست تصاویر با DPI بالا
        images = convert_from_path(
            file_path,
            dpi=400,
            poppler_path=POPPLER_PATH
        )

        all_text = []
        total_pages = len(images)

        for i, img in enumerate(images):
            print(f"[INFO] Processing PDF page {i + 1}/{total_pages}")

            # 🔄 پیش‌پردازش قوی تصویر
            gray, processed = PDFPipeline.preprocess_pdf_page(img)

            # ⚠️ نکته حیاتی: هیچ فلیپ اجباری اینجا نیست!
            # چرخش ۱۸۰ درجه قبلاً در مرحله router/preprocess انجام شده.
            # افزودن cv2.flip در اینجا باعث آینه‌ای شدن متن و خروجی garbled می‌شود.

            # 📸 ذخیره دیباگ (اختیاری - برای عیب‌یابی)
            # cv2.imwrite(f"output/debug_page_{i}_preprocessed.jpg", processed)

            # -----------------------------------------
            # موتور ۱: Tesseract (برای متون ساختاریافته)
            # -----------------------------------------
            tess_text = pytesseract.image_to_string(
                processed,
                lang="fas+eng",
                config=r'--oem 1 --psm 4 -c preserve_interword_spaces=1'
            )

            # -----------------------------------------
            # موتور ۲: EasyOCR (برای متون پیچیده/اسکرین‌شات)
            # -----------------------------------------
            easy_text = run_easyocr(gray)


            # ✅ اگر EasyOCR هیچ چیزی برنگرداند، رشته خالی در نظر بگیر
            if easy_text is None or not isinstance(easy_text, str):
                easy_text = ""


            # 🧹 تمیزکاری اولیه هر دو خروجی
            tess_clean = clean_ocr_text(clean_bidi(tess_text))
            easy_clean = clean_ocr_text(clean_bidi(easy_text))

            # 📊 امتیازدهی هوشمند و انتخاب بهترین
            tess_score = advanced_score(tess_clean)
            easy_score = advanced_score(easy_clean)
            
            text = easy_clean if easy_score > tess_score else tess_clean

            # 🔢 نرمال‌سازی اعداد (فارسی/انگلیسی)
            text = normalize_numbers(text)

            # 🌐 تشخیص زبان و اعمال پست‌پروسس تخصصی
            if PDFPipeline.is_persian_dominant(text):
                # ✅ متن فارسی: اصلاح حروف، نیم‌فاصله، علائم، RTL
                text = improve_persian_text(text)
                text = fix_safe_ocr_artifacts(text)  # اصلاحات ایمن اضافی
            else:
                # ✅ متن انگلیسی: اصلاح I'll، علائم، الگوهای خاص
                text = fix_english_ocr(text)

            # 📄 افزودن جداکننده صفحه به خروجی نهایی
            all_text.append(f"\n\n{'='*20} Page {i + 1} {'='*20}\n\n{text}")

        return "\n".join(all_text)