import cv2
import numpy as np



def process_dark_image(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # -----------------------------
    # invert
    # متن سفید روی پس‌زمینه سیاه
    # -----------------------------
    inverted = cv2.bitwise_not(gray)

    # -----------------------------
    # contrast boost
    # -----------------------------
    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )

    contrast = clahe.apply(inverted)

    # -----------------------------
    # sharpen
    # -----------------------------
    blur = cv2.GaussianBlur(contrast, (0, 0), 1.5)

    sharp = cv2.addWeighted(
        contrast,
        1.8,
        blur,
        -0.8,
        0
    )

    # -----------------------------
    # threshold
    # -----------------------------
    binary = cv2.adaptiveThreshold(
        sharp,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        5
    )

    return binary