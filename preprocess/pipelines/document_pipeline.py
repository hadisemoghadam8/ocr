#C:\Users\ASUS\ocr_project\preprocess\pipelines\document_pipeline.py

import cv2


def process_document_image(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # -----------------------------
    # upscale
    # -----------------------------
    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # -----------------------------
    # denoise
    # -----------------------------
    gray = cv2.fastNlMeansDenoising(
        gray,
        None,
        8,
        7,
        21
    )

    # -----------------------------
    # CLAHE ملایم
    # -----------------------------
    clahe = cv2.createCLAHE(
        clipLimit=1.5,
        tileGridSize=(8, 8)
    )

    contrast = clahe.apply(gray)

    # -----------------------------
    # sharpen سبک
    # -----------------------------
    blur = cv2.GaussianBlur(
        contrast,
        (0, 0),
        1.2
    )

    sharp = cv2.addWeighted(
        contrast,
        1.15,
        blur,
        -0.15,
        0
    )

    # -----------------------------
    # خروجی grayscale
    # بدون binary
    # -----------------------------
    return cv2.cvtColor(
        sharp,
        cv2.COLOR_GRAY2BGR
    )