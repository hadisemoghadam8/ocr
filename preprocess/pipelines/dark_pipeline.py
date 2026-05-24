# C:\Users\ASUS\ocr_project\preprocess\pipelines\dark_pipeline.py
import cv2
import numpy as np

def process_dark_image(image):
    """
    نسخه نهایی Dark UI Pipeline (استاندارد OCR)
    استراتژی: ایزوله‌سازی محتوا -> باینری‌سازی Otsu -> مورفولوژی ایمن برای انگلیسی
    """

    # # ---------------------------------
    # # 1. Smart Crop (حذف لوگوی X، حاشیه‌ها و x.com)
    # # ---------------------------------
    # h, w = image.shape[:2]
    # # برش دقیق ناحیه توییت (بر اساس ساختار استاندارد اسکرین‌شات X)
    # y1, y2 = int(h * 0.14), int(h * 0.84)
    # x1, x2 = int(w * 0.09), int(w * 0.91)
    # image = image[y1:y2, x1:x2]

    # ---------------------------------
    # 2. Upscale (بزرگ‌نمایی استاندارد OCR)
    # ---------------------------------
    h, w = image.shape[:2]
    if max(h, w) < 1400:
        image = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # ---------------------------------
    # 3. Grayscale
    # ---------------------------------
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ---------------------------------
    # 4. Mild Denoise (حذف آرتیفکت‌های JPEG بدون تار کردن)
    # ---------------------------------
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # ---------------------------------
    # 5. Binarization (تبدیل به سیاه‌وسفید خالص - کلید حل مشکل انگلیسی)
    # ---------------------------------
    # THRESH_BINARY_INV چون پس‌زمینه تیره و متن روشن است
    # Otsu به‌طور خودکار بهترین آستانه را برای ترکیب فارسی/انگلیسی پیدا می‌کند
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # ---------------------------------
    # 6. Morphology (اصلاح نهایی برای حفظ انگلیسی)
    # ---------------------------------
    # حذف MORPH_CLOSE که حروف نازک انگلیسی را حذف می‌کند
    # فقط MORPH_OPEN برای حذف نویز، با کرنل بسیار کوچک
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_clean, iterations=1)
    
    # ---------------------------------
    # 7. Return (فرمت رنگی برای سازگاری با EasyOCR)
    # ---------------------------------
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)