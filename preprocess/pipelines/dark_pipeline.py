#C:\Users\ASUS\ocr_project\preprocess\pipelines\dark_pipeline.py

import cv2
import numpy as np


def process_dark_image(image):

    # ---------------------------------
    # upscale
    # ---------------------------------

    h, w = image.shape[:2]

    if max(h, w) < 1600:

        image = cv2.resize(
            image,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

    # ---------------------------------
    # grayscale
    # ---------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # ---------------------------------
    # denoise سبک
    # ---------------------------------

    gray = cv2.fastNlMeansDenoising(
        gray,
        None,
        5,
        7,
        21
    )

    # ---------------------------------
    # CLAHE
    # ---------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    contrast = clahe.apply(gray)

    # ---------------------------------
    # sharpen نرم
    # ---------------------------------

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

    # ---------------------------------
    # خیلی مهم:
    # invert نکن
    # threshold نکن
    # ---------------------------------

    return cv2.cvtColor(
        sharp,
        cv2.COLOR_GRAY2BGR
    )