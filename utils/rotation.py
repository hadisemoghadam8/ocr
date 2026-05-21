# C:\Users\ASUS\ocr_project\utils\rotation.py

import re
import cv2
import numpy as np
import pytesseract

from PIL import Image

from utils.ocr_utils import detect_psm


ROTATIONS = [0, 90, 180, 270]


# =====================================================
# Text scoring helpers
# =====================================================

def _count_persian(text: str) -> int:
    return len(re.findall(r'[\u0600-\u06FF]', text))


def _count_english(text: str) -> int:
    return len(re.findall(r'[A-Za-z]', text))


def _count_digits(text: str) -> int:
    return len(re.findall(r'\d', text))


def _count_garbage(text: str) -> int:
    return len(
        re.findall(
            r'[@#$%^&*_=+<>\\/|~`]',
            text
        )
    )


def _count_valid_words(text: str) -> int:
    return len(
        re.findall(
            r'[\u0600-\u06FFA-Za-z]{2,}',
            text
        )
    )


# =====================================================
# OCR quality analysis
# =====================================================

def _count_bad_lines(text: str) -> int:

    bad = 0

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        fa = _count_persian(line)

        en = _count_english(line)

        garbage = _count_garbage(line)

        # خیلی کوتاه
        if len(line) < 3:
            bad += 1
            continue

        # سمبل زیاد
        if garbage > 4:
            bad += 1
            continue

        # انگلیسی نویزی
        if fa < 2 and en > 5:
            bad += 1
            continue

        # فقط انگلیسی
        if re.fullmatch(r'[A-Za-z\s]{3,}', line):
            bad += 1
            continue

    return bad





def _layout_bonus(
    image: Image.Image,
    angle: int,
    text: str
) -> float:

    w, h = image.size

    ratio = w / max(h, 1)

    persian = _count_persian(text)

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    line_count = len(lines)

    bonus = 0.0

    # ---------------------------------
    # portrait image
    # ---------------------------------

    if ratio < 0.9:

        # اگر متن فارسی زیاد داریم
        # معمولاً متن خوابیده است
        if persian > 20:

            if angle in (90, 270):
                bonus += 45

            else:
                bonus -= 20

    # ---------------------------------
    # landscape image
    # ---------------------------------

    elif ratio > 1.1:

        if angle in (0, 180):
            bonus += 20

    # ---------------------------------
    # line structure
    # ---------------------------------

    if line_count <= 2:
        bonus -= 10

    return bonus

# =====================================================
# OCR score
# =====================================================

def score_ocr_text(
    text: str,
    image: Image.Image,
    angle: int
) -> float:

    persian_chars = _count_persian(text)

    english_chars = _count_english(text)

    digits = _count_digits(text)

    garbage = _count_garbage(text)

    valid_words = _count_valid_words(text)

    bad_lines = _count_bad_lines(text)

    newline_count = text.count("\n")

    weird_patterns = len(
        re.findall(
            r'(?:[A-Za-z]{1,2}\s){4,}',
            text
        )
    )

    score = (
        persian_chars * 5 +
        english_chars * 1 +
        digits * 2 +
        valid_words * 4 +
        newline_count * 1 -
        garbage * 7 -
        bad_lines * 35 -
        weird_patterns * 25
    )

    # orientation prior
    score += _layout_bonus(
            image,
            angle,
            text
        )

    # متن خیلی کم
    if len(text.strip()) < 10:
        score -= 50

    return float(score)


# =====================================================
# Fine skew detection
# =====================================================

def _detect_skew_angle(cv_image) -> float:
    """
    تشخیص زاویه‌ی واقعی متن
    فقط برای skew کم مثل 1-2 درجه
    """

    gray = cv2.cvtColor(
        cv_image,
        cv2.COLOR_BGR2GRAY
    )

    # threshold
    thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    coords = np.column_stack(
        np.where(thresh > 0)
    )

    if len(coords) < 100:
        return 0.0

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = 90 + angle

    angle = -angle

    # فقط skew واقعی
    if abs(angle) > 8:
        return 0.0

    return float(angle)


# =====================================================
# Apply skew correction
# =====================================================

def _rotate_cv_image(
    image,
    angle
):

    h, w = image.shape[:2]

    center = (w // 2, h // 2)

    matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0
    )

    rotated = cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return rotated


# =====================================================
# Main rotation detector
# =====================================================
def detect_best_rotation(cv_image):

    pil_image = Image.fromarray(
        cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2RGB
        )
    )

    best_score = -999999
    best_angle = 0
    best_image = pil_image

    for angle in [0, 90, 180, 270]:

        rotated = pil_image.rotate(
            angle,
            expand=True
        )

        try:

            psm = detect_psm(rotated)

            text = pytesseract.image_to_string(
                rotated,
                lang="fas+eng",
                config=f"--oem 3 --psm {psm}"
            )

            persian = len(
                re.findall(
                    r'[\u0600-\u06FF]',
                    text
                )
            )

            digits = len(
                re.findall(r'\d', text)
            )

            garbage = len(
                re.findall(
                    r'[@#$%^&*_=+<>\\/|]',
                    text
                )
            )

            english_noise = len(
                re.findall(
                    r'[A-Za-z]{1,2}',
                    text
                )
            )

            lines = [
                x.strip()
                for x in text.splitlines()
                if x.strip()
            ]

            score = (
                persian * 5 +
                digits * 2 -
                garbage * 4 -
                english_noise * 2
            )

            # ---------------------------------
            # اگر متن فارسی زیاد داریم
            # portrait را ترجیح بده
            # ---------------------------------

            w, h = rotated.size

            if h > w and persian > 15:

                if angle in (90, 270):
                    score += 35

            print(
                f"[INFO] angle={angle} "
                f"score={score:.2f}"
            )

            if score > best_score:

                best_score = score
                best_angle = angle
                best_image = rotated

        except Exception as e:
            print(e)

    corrected_cv = cv2.cvtColor(
        np.array(best_image),
        cv2.COLOR_RGB2BGR
    )

    print(
        f"[INFO] Final rotation: "
        f"{best_angle}°"
    )

    return {
        "image": corrected_cv,
        "angle": best_angle,
        "score": best_score
    }