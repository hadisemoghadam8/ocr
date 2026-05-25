# C:\Users\ASUS\ocr_project\engines\tesseract_engine.py
import pytesseract

def run_tesseract(img, psm=6):
    """
    اجرای Tesseract OCR با تنظیمات بهینه برای اسناد فارسی اسکن‌شده.
    
    Parameters:
        img: numpy array image (ترجیحاً باینری شده/سیاه و سفید)
        psm: Page Segmentation Mode (6 برای بلوک یکنواخت متن مناسب است)

    Returns:
        Extracted text (string)
    """
    # ✅ استفاده از LSTM خالص (OEM 1) + فقط زبان فارسی
    # حذف 'eng' برای جلوگیری از تولید نویزهای لاتین مثل SLL, LS, CI
    config = f"--oem 1 --psm {psm}"

    text = pytesseract.image_to_string(
        img,
        lang="fas",  # فقط فارسی
        config=config
    )

    return text