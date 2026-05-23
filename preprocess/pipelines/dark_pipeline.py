# C:\Users\ASUS\ocr_project\preprocess\pipelines\dark_pipeline.py

import cv2
import numpy as np


def process_dark_image(image):
    """
    نسخه نهایی و بهینه‌شده برای Dark UI.
    استراتژی: تقویت ساختار حروف (Stroke Enhancement) و حذف نویزهای فشرده‌سازی.
    """

    # ---------------------------------
    # 1. Upscale (بزرگ‌نمایی برای جزئیات)
    # ---------------------------------
    h, w = image.shape[:2]
    if max(h, w) < 1600:
        # INTER_CUBIC بهترین تعادل را برای متن دیجیتال دارد
        image = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # ---------------------------------
    # 2. Grayscale
    # ---------------------------------
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ---------------------------------
    # 3. Gamma Correction (روشن‌سازی هوشمند)
    # ---------------------------------
    # مقدار 0.65 متن‌های خاکستری کمرنگ (مثل @fatemedaniyali) را آشکار می‌کند
    gamma = 0.65
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** (1.0 / invGamma) * 255)
                      for i in np.arange(0, 256)]).astype("uint8")
    gray = cv2.LUT(gray, table)

    # ---------------------------------
    # 4. CLAHE (کنتراست محلی)
    # ---------------------------------
    # clipLimit=2.0 برای جلوگیری از ایجاد هاله دور حروف
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # ---------------------------------
    # 5. Denoise (حذف نویز فشرده‌سازی)
    # ---------------------------------
    # Bilateral Filter نویز را حذف می‌کند اما لبه‌های تیز حروف را نگه می‌دارد
    gray = cv2.bilateralFilter(gray, d=5, sigmaColor=50, sigmaSpace=50)

    # ---------------------------------
    # 6. Sharpening (شارپ کردن برای تمایز حروف)
    # ---------------------------------
    # این مرحله حیاتی است تا 'م' از 'ن' و 'ر' از 'ز' تشخیص داده شود
    kernel_sharpen = np.array([
        [-1, -1, -1],
        [-1,  9, -1],
        [-1, -1, -1]
    ])
    gray = cv2.filter2D(gray, -1, kernel_sharpen)

    # ---------------------------------
    # 7. Morphological Closing (درمان شکستگی حروف)
    # ---------------------------------
    # این خط جادویی است: پیکسل‌های جدا شده درون یک حرف (مثل 'عوا اض') را به هم می‌چسباند
    kernel = np.ones((3,3),np.uint8)
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    # ---------------------------------
    # 8. نرمال‌سازی نهایی کنتراست
    # ---------------------------------
    gray = cv2.convertScaleAbs(gray, alpha=1.1, beta=10)

    # ---------------------------------
    # 9. بازگشت به فرمت رنگی
    # ---------------------------------
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)# C:\Users\ASUS\ocr_project\preprocess\pipelines\dark_pipeline.py

import cv2
import numpy as np


def process_dark_image(image):
    """
    نسخه نهایی و بهینه‌شده برای Dark UI.
    استراتژی: تقویت ساختار حروف (Stroke Enhancement) و حذف نویزهای فشرده‌سازی.
    """

    # ---------------------------------
    # 1. Upscale (بزرگ‌نمایی برای جزئیات)
    # ---------------------------------
    h, w = image.shape[:2]
    if max(h, w) < 1600:
        # INTER_CUBIC بهترین تعادل را برای متن دیجیتال دارد
        image = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # ---------------------------------
    # 2. Grayscale
    # ---------------------------------
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ---------------------------------
    # 3. Gamma Correction (روشن‌سازی هوشمند)
    # ---------------------------------
    # مقدار 0.65 متن‌های خاکستری کمرنگ (مثل @fatemedaniyali) را آشکار می‌کند
    gamma = 0.65
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** (1.0 / invGamma) * 255)
                      for i in np.arange(0, 256)]).astype("uint8")
    gray = cv2.LUT(gray, table)

    # ---------------------------------
    # 4. CLAHE (کنتراست محلی)
    # ---------------------------------
    # clipLimit=2.0 برای جلوگیری از ایجاد هاله دور حروف
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # ---------------------------------
    # 5. Denoise (حذف نویز فشرده‌سازی)
    # ---------------------------------
    # Bilateral Filter نویز را حذف می‌کند اما لبه‌های تیز حروف را نگه می‌دارد
    gray = cv2.bilateralFilter(gray, d=5, sigmaColor=50, sigmaSpace=50)

    # ---------------------------------
    # 6. Sharpening (شارپ کردن برای تمایز حروف)
    # ---------------------------------
    # این مرحله حیاتی است تا 'م' از 'ن' و 'ر' از 'ز' تشخیص داده شود
    kernel_sharpen = np.array([
        [-1, -1, -1],
        [-1,  9, -1],
        [-1, -1, -1]
    ])
    gray = cv2.filter2D(gray, -1, kernel_sharpen)

    # ---------------------------------
    # 7. Morphological Closing (درمان شکستگی حروف)
    # ---------------------------------
    # این خط جادویی است: پیکسل‌های جدا شده درون یک حرف (مثل 'عوا اض') را به هم می‌چسباند
    kernel = np.ones((3,3),np.uint8)
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    # ---------------------------------
    # 8. نرمال‌سازی نهایی کنتراست
    # ---------------------------------
    gray = cv2.convertScaleAbs(gray, alpha=1.1, beta=10)

    # ---------------------------------
    # 9. بازگشت به فرمت رنگی
    # ---------------------------------
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)