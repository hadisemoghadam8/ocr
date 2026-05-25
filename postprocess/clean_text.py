# postprocess/clean_text.py
import re


def clean_ocr_text(text: str) -> str:
    """
    تمیزکاری عمومی خروجی OCR:
    - حذف خطوط خالی و نویزی
    - حذف سمبل‌های اضافی و کاراکترهای نامعتبر
    - حفظ خطوط معتبر فارسی/انگلیسی/عددی
    """
    
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()

        # ✅ حذف خطوط کاملاً خالی
        if not line:
            continue

        # 🔢 شمارش انواع کاراکترها در خط
        symbols = sum(
            not ch.isalnum() and not ch.isspace()
            for ch in line
        )
        english_chars = sum(
            ch.isascii() and ch.isalpha()
            for ch in line
        )
        persian_chars = sum(
            '\u0600' <= ch <= '\u06FF'
            for ch in line
        )
        digit_chars = sum(
            ch.isdigit()
            for ch in line
        )

        # تعداد کاراکترهای معتبر (فارسی + انگلیسی + عدد)
        valid_chars = persian_chars + english_chars + digit_chars

        # 🗑 حذف خطوط پر از سمبل (مگر اینکه فارسی غالب باشد)
        if len(line) > 0 and symbols / len(line) > 0.35 and persian_chars < 2:
            continue

        # 🗑 حذف خطوط تکراری/بی‌معنی کوتاه که OCR گاهی تولید می‌کند
        if line.lower() in ["ae", "alll", "lll"]:
            continue

        if line.strip() in ["ممت", "مشا"]:
            continue

        # 🗑 حذف خطوط خیلی کوتاه یا کم‌محتوا
        if valid_chars < 2:
            continue
        if len(line) < 3:
            continue

        # 🧹 حذف نویزهای انتهایی مثل @D & یا رشته‌های مشابه
        line = re.sub(r'\s+@[\w\s&]+$', '', line)
        line = re.sub(r'[&@]+$', '', line).strip()

        # ✅ افزودن خط تمیزشده به خروجی
        cleaned.append(line)

    return "\n".join(cleaned)