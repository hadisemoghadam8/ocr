import cv2



def process_document_image(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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
        10,
        7,
        21
    )

    # -----------------------------
    # CLAHE
    # -----------------------------
    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8)
    )

    contrast = clahe.apply(gray)

    # -----------------------------
    # sharpen
    # -----------------------------
    blur = cv2.GaussianBlur(contrast, (0, 0), 1.2)

    sharp = cv2.addWeighted(
        contrast,
        1.6,
        blur,
        -0.6,
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