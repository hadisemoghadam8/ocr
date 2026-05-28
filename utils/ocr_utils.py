def detect_psm(img):
    """
    Select Tesseract PSM based on image aspect ratio.
    PSM 6: single uniform block (portrait).
    PSM 11: sparse text (landscape/wide).
    """
    width, height = img.size
    ratio = width / height

    if ratio < 0.8:
        return 6  # Portrait layout

    return 11  # Landscape or wide layout