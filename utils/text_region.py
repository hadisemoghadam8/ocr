#C:\Users\ASUS\ocr_project\utils\text_region.py

import cv2
import numpy as np


def detect_text_region(image):
    """
    پیدا کردن ناحیه‌ای که احتمالاً متن اصلی داخلش است
    مخصوص عکس‌های واقعی با لیبل سفید/بنر
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # blur سبک
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # threshold روشن
    _, th = cv2.threshold(
        blur,
        180,
        255,
        cv2.THRESH_BINARY
    )

    # morph
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (15, 5)
    )

    morph = cv2.morphologyEx(
        th,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    contours, _ = cv2.findContours(
        morph,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    h, w = image.shape[:2]

    best = None
    best_score = 0

    for cnt in contours:

        x, y, cw, ch = cv2.boundingRect(cnt)

        area = cw * ch

        if area < 5000:
            continue

        ratio = cw / max(ch, 1)

        # لیبل متنی معمولاً کشیده است
        if ratio < 2:
            continue

        # ناحیه پایین تصویر امتیاز بیشتر
        vertical_bonus = y / h

        score = area * 0.7 + vertical_bonus * 10000

        if score > best_score:
            best_score = score
            best = (x, y, cw, ch)

    if best is None:
        return image

    x, y, cw, ch = best

    # padding
    pad = 20

    x1 = max(0, x - pad)
    y1 = max(0, y - pad)

    x2 = min(w, x + cw + pad)
    y2 = min(h, y + ch + pad)

    cropped = image[y1:y2, x1:x2]

    return cropped