# C:\Users\ASUS\ocr_project\postprocess\scoring.py

import re


def score_ocr_text(text):

    if text is None:
        return -999

    if not isinstance(text, str):
        text = str(text)

    persian_chars = len(
        re.findall(r'[\u0600-\u06FF]', text)
    )

    english_chars = len(
        re.findall(r'[A-Za-z]', text)
    )

    digits = len(
        re.findall(r'\d', text)
    )

    garbage = len(
        re.findall(r'[@#$%^&*_=+<>\\/|~`]', text)
    )

    weird_patterns = len(
        re.findall(r'(lll|III|@@@|###)', text)
    )

    words = len(text.split())

    score = (
        persian_chars * 4 +
        english_chars * 2 +
        digits -
        garbage * 8 +
        words * 1.5
    )

    # garbage شدید
    if garbage > persian_chars * 0.3:
        score -= 120

    # الگوهای خراب OCR
    if weird_patterns > 2:
        score -= 100

    return score