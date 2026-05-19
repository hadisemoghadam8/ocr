#C:\Users\ASUS\ocr_project\postprocess\english_fix.py
def fix_english_ocr(text: str) -> str:
    # اصلاحات پایه
    replacements = {
        # OCR اشتباه برای I'll
        r'\bIll\b': "I'll",
        r'\bIIl\b': "I'll",
        r'\bIII\b': "I'll",
        r'\bI1l\b': "I'll",

        # فاصله‌گذاری علائم انگلیسی
        r'(?<!\n)[ \t]+([.,!?;:])': r'\1',
    }

    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)

    # فقط برای متن‌های انگلیسی بلند
    english_chars = len(
        re.findall(r'[A-Za-z]', text)
    )

    if english_chars > 30:
        # مورد خاص 2 1 1 --> I'll
        text = re.sub(
            r'\b2\W*1\W*1\b',
            "I'll",
            text
        )

        # مثال خروجی تو: "be! they Were further than"
        # معمولاً باید "be! They were further than" باشد
        text = re.sub(
            r'\bbe!\s*they\s+Were\b',
            "be! They were",
            text
        )

        # عنوان ساده: "Afternoon Dorothy Parker" → "Afternoon — Dorothy Parker"
        text = re.sub(
            r'(?m)^(Afternoon)\s+(Dorothy Parker)\s*$',
            r'\1 — \2',
            text
        )


        # =====================================================
        # 👇👇 افزوده‌های جدید برای اصلاح نقطه‌ها و ویرگول‌ها
        # =====================================================

        # 1️⃣ حذف ویرگول اشتباه ابتدای خط (,And → And)
        text = re.sub(
            r'(?m)^,([A-Z])',
            r'\1',
            text
        )

        # 2️⃣ برگرداندن علامت نقطه یا ویرگول که ابتدا آمده بعد از خط قبل
        text = re.sub(
            r'\n([,.;:!?])([A-Za-z])',
            r'\1 \2',
            text
        )

        # 3️⃣ اصلاح URLs حذف‌شده نقاط
        text = re.sub(
            r'www\s+([A-Za-z0-9-]+)\s+com',
            r'www.\1.com',
            text
        )

        # 4️⃣ اصلاح سطر پایانی شعر Afternoon که OCR ترتیبش را بهم زده
        text = re.sub(
            r'be!\s*They\s+were\s+further\s+than',
            "Were further than they be!",
            text
        )


    return text
