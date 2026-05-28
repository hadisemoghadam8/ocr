
import cv2
import numpy as np


def detect_text_region(image):
    """
    Detect and enhance the main text region in real-world images.
    
    Targets images with white labels or banners where text appears
    in a distinct horizontal region, typically in the lower portion.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Light blur to reduce noise before thresholding
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # High threshold to isolate bright regions (likely text labels)
    _, th = cv2.threshold(
        blur, 180, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Morphological closing to merge fragmented text regions
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
    morph = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(
        morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    h, w = image.shape[:2]
    best = None
    best_score = 0

    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch

        # Skip small regions
        if area < 5000:
            continue

        # Text labels are typically wide and short
        ratio = cw / max(ch, 1)
        if ratio < 2:
            continue

        # Prefer regions in the lower part of the image
        vertical_bonus = y / h
        score = area * 0.7 + vertical_bonus * 10000

        if score > best_score:
            best_score = score
            best = (x, y, cw, ch)

    # No suitable text region found
    if best is None:
        return image

    x, y, cw, ch = best

    # Extract region with padding
    pad = 20
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(w, x + cw + pad)
    y2 = min(h, y + ch + pad)

    roi = image[y1:y2, x1:x2]

    # Mild sharpening to enhance text clarity in the ROI
    blurred = cv2.GaussianBlur(roi, (0, 0), 1.0)
    roi = cv2.addWeighted(roi, 1.5, blurred, -0.5, 0)

    # Replace original region with enhanced version
    image[y1:y2, x1:x2] = roi

    return image
