#postprocess\clean_text.py
def clean_ocr_text(text: str) -> str:
    lines = text.splitlines()

    cleaned = []

    for line in lines:
        line = line.strip()

        # حذف خالی
        if not line:
            continue

        # حذف خیلی کوتاه
        if len(line) < 3:
            continue

        # حذف خطوط پر از سمبل
        symbols = sum(
            not ch.isalnum() and not ch.isspace()
            for ch in line
        )

        # شمارش انگلیسی
        english_chars = sum(
            ch.isascii() and ch.isalpha()
            for ch in line
        )

        # شمارش فارسی
        persian_chars = sum(
            '\u0600' <= ch <= '\u06FF'
            for ch in line
        )

        # شمارش عدد
        digit_chars = sum(
            ch.isdigit()
            for ch in line
        )

        # تعداد کاراکترهای معتبر
        valid_chars = (
            persian_chars +
            english_chars +
            digit_chars
        )

        # حذف خطوط پر از سمبل
        if symbols / len(line) > 0.35 and persian_chars < 2:
            continue
        # # اگر انگلیسی زیاد و فارسی نداشت → احتمال نویز
        # if english_chars > 3 and persian_chars == 0:
        #     # ولی بعضی UI text ها رو نگه دار
        #     allowed = [
        #         "SUN",
        #         "AM",
        #         "PM",
        #         "Replied"
        #     ]

        #     if not any(word in line for word in allowed):
        #         continue

        # حذف خطوط تکراری عجیب
        if line.lower() in ["ae", "alll", "lll"]:
            continue

        # حذف خطوط بی‌معنی کوتاه
        if valid_chars < 2:
            continue
        
        # حذف خطوط کوتاهِ نویزی
        if len(line) < 3:
            continue

        # حذف نویزهای انتهایی مثل @D &
        if re.fullmatch(r'[@&A-Za-z\s]{1,6}', line):
            continue

        # حذف نویزهای انتهایی داخل خط
        line = re.sub(r'\s+@[\w\s&]+$', '', line)

        # حذف @ و & اضافی آخر خط
        line = re.sub(r'[&@]+$', '', line).strip()

        cleaned.append(line)

    return "\n".join(cleaned)
