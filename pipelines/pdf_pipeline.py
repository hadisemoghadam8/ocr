#C:\Users\ASUS\ocr_project\pipelines\pdf_pipeline.py
def preprocess_pdf_page(img):

    img_np = np.array(img)

    gray = cv2.cvtColor(
        img_np,
        cv2.COLOR_RGB2GRAY
    )

    # -----------------------------
    # auto upscale
    # -----------------------------
    h, w = gray.shape

    if w < 1800:
        scale = 2.2
    else:
        scale = 1.4

    gray = cv2.resize(
        gray,
        None,
        fx=scale,
        fy=scale,
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
    # local contrast
    # -----------------------------
    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(gray)

    # -----------------------------
    # sharpen
    # -----------------------------
    blur = cv2.GaussianBlur(
        gray,
        (0, 0),
        1.2
    )

    sharp = cv2.addWeighted(
        gray,
        1.6,
        blur,
        -0.6,
        0
    )

    # -----------------------------
    # adaptive threshold
    # -----------------------------
    th = cv2.adaptiveThreshold(
    sharp,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    31,
    5
)

    # -----------------------------
    # morphology cleanup
    # حذف نویز ریز
    # -----------------------------
    kernel = np.ones((2, 2), np.uint8)

    th = cv2.morphologyEx(
        th,
        cv2.MORPH_OPEN,
        kernel
    )

    return gray, th


