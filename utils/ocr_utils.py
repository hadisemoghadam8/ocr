# utils/ocr_utils.py
def detect_psm(img):
    width, height = img.size

    ratio = width / height

    if ratio < 0.8:
        return 6

    return 11
