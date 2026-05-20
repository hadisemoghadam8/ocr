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


# =====================================================
# Orientation prior
# =====================================================

def _orientation_bonus(
    image: Image.Image,
    angle: int
) -> float:

    w, h = image.size

    ratio = w / max(h, 1)

    bonus = 0.0

    # افقی
    if ratio >= 1.15:

        if angle in (0, 180):
            bonus += 25
        else:
            bonus -= 40

    # عمودی
    elif ratio <= 0.85:

        if angle in (90, 270):
            bonus += 25
        else:
            bonus -= 40

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
        valid_words * 8 +
        newline_count * 1 -
        garbage * 7 -
        bad_lines * 22 -
        weird_patterns * 25
    )

    # orientation prior
    score += _orientation_bonus(
        image,
        angle
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

    # ---------------------------------
    # 1) skew correction کوچک
    # ---------------------------------

    skew_angle = _detect_skew_angle(
        cv_image
    )

    print(
        f"[INFO] Detected skew angle: "
        f"{skew_angle:.2f}"
    )

    corrected = _rotate_cv_image(
        cv_image,
        skew_angle
    )

    pil_image = Image.fromarray(
        cv2.cvtColor(
            corrected,
            cv2.COLOR_BGR2RGB
        )
    )

    # ---------------------------------
    # 2) orientation detection
    # ---------------------------------

    results = []

    for angle in ROTATIONS:

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

            score = score_ocr_text(
                text,
                rotated,
                angle
            )

            print(
                f"[INFO] angle={angle} "
                f"score={score:.2f}"
            )

            results.append({
                "angle": angle,
                "score": score,
                "image": rotated
            })

        except Exception as e:
            print(e)

    # ---------------------------------
    # مرتب‌سازی
    # ---------------------------------

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    best = results[0]

    best_angle = best["angle"]

    best_score = best["score"]

    best_image = best["image"]

    # ---------------------------------
    # جلوگیری از 180 اشتباه
    # ---------------------------------

    zero_result = next(
        x for x in results
        if x["angle"] == 0
    )

    if best_angle == 180:

        diff = (
            best_score -
            zero_result["score"]
        )

        # اگر اختلاف کم بود
        # 180 نزن
        if diff < 60:

            print(
                "[INFO] 180° rejected "
                "(difference too small)"
            )

            best_angle = 0

            best_image = zero_result["image"]

            best_score = zero_result["score"]

    # ---------------------------------
    # جلوگیری از چرخش اشتباه کلی
    # ---------------------------------

    if best_angle != 0:

        diff = (
            best_score -
            zero_result["score"]
        )

        if diff < 35:

            print(
                "[INFO] Rotation difference small "
                "-> keeping original orientation"
            )

            best_angle = 0

            best_image = zero_result["image"]

            best_score = zero_result["score"]

    corrected_cv = cv2.cvtColor(
        np.array(best_image),
        cv2.COLOR_RGB2BGR
    )

    final_angle = (
        skew_angle + best_angle
    )

    print(
        f"[INFO] Final rotation: "
        f"{final_angle:.2f}°"
    )

    return {
        "image": corrected_cv,
        "angle": final_angle,
        "score": best_score
    }