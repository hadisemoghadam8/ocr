import re


def normalize_numbers(text: str) -> str:
    """
    Convert Arabic and English digits to Persian numerals.
    Skips conversion for short texts or English-dominant content.
    """
    if not text or not isinstance(text, str):
        return ""

    # Skip normalization for short strings (e.g., "4K", "2h") or English-heavy text
    if len(text.strip()) < 15:
        return text

    persian = len(re.findall(r'[\u0600-\u06FF]', text))
    english = len(re.findall(r'[A-Za-z]', text))

    if english > persian:
        return text

    # Translation tables for digit conversion
    arabic_to_persian = str.maketrans("٠١٢٣٤٥٦٧٨٩", "۰۱۲۳۴۵۶۷۸۹")
    english_to_persian = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

    text = text.translate(arabic_to_persian)
    text = text.translate(english_to_persian)

    return text