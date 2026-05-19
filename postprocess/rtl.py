#C:\Users\ASUS\ocr_project\postprocess\rtl.py
# اصلاح نمایش RTL فقط برای خطوط فارسی
def rtl_display_line(line: str) -> str:

    # حذف فاصله قبل از علائم
    line = re.sub(
    r'[ \t]+([،,.:;!?؟؛])',
    r'\1',
    line
)

    # حذف فاصله بعد از #
    line = re.sub(r'#\s+', '#', line)

    # شمارش فارسی و انگلیسی
    persian_chars = len(
        re.findall(r'[\u0600-\u06FF]', line)
    )

    english_chars = len(
        re.findall(r'[A-Za-z]', line)
    )

    # فقط اگر فارسی غالب بود RTL شود
    if (
    persian_chars >= 5 and
    persian_chars > english_chars * 3
):
        line = '\u202B' + line + '\u202C'

    return line

# اصلاح ساده‌ی فاصله‌ی علائم
def fix_bidi_punctuation(text: str) -> str:
    # فاصله قبل از علائم را حذف می‌کنیم
    text = re.sub(r'\s+([،,.:;!?؟؛])', r'\1', text)

    # فاصله بعد از # را حذف می‌کنیم
    text = re.sub(r'#\s+', '#', text)

    return text



def clean_bidi(text: str) -> str:
    return re.sub(
        r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]',
        '',
        text
    )
