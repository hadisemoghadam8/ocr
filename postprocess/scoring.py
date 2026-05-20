#C:\Users\ASUS\ocr_project\postprocess\scoring.py

import re

def score_ocr_text(text):

    if text is None:
        text = ""

    if not isinstance(text, str):
        text = str(text)

    import re

    persian = len(re.findall(r'[\u0600-\u06FF]', text))
    english = len(re.findall(r'[A-Za-z]', text))

    return persian * 2 + english