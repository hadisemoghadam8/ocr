# C:\Users\ASUS\ocr_project\preprocess\pipelines\screenshot_pipeline.py

import cv2
import numpy as np


class ScreenshotBooster:

    @staticmethod
    def process(image):

        # ---------------------------------
        # load image
        # ---------------------------------
        if isinstance(image, str):
            image = cv2.imread(image)

        if image is None:
            raise ValueError("Could not load image")

        # ---------------------------------
        # remove screenshot UI areas
        # top status bar / bottom nav
        # ---------------------------------
        h, w = image.shape[:2]

        top_crop = int(h * 0.08)
        bottom_crop = int(h * 0.10)

        image = image[top_crop:h - bottom_crop, :]

        # ---------------------------------
        # grayscale
        # ---------------------------------
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # ---------------------------------
        # upscale
        # preserve Persian glyph details
        # ---------------------------------
        gray = cv2.resize(
            gray,
            None,
            fx=2.5,
            fy=2.5,
            interpolation=cv2.INTER_CUBIC
        )

        # ---------------------------------
        # local contrast enhancement
        # better for UI screenshots
        # ---------------------------------
        clahe = cv2.createCLAHE(
            clipLimit=2.5,
            tileGridSize=(8, 8)
        )

        gray = clahe.apply(gray)

        # ---------------------------------
        # edge-preserving denoise
        # keeps Persian characters connected
        # ---------------------------------
        gray = cv2.bilateralFilter(
            gray,
            d=9,
            sigmaColor=75,
            sigmaSpace=75
        )

        # ---------------------------------
        # adaptive threshold
        # better than OTSU for screenshots
        # ---------------------------------
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            7
        )

        # ---------------------------------
        # morphology cleanup
        # reconnect broken Persian glyphs
        # ---------------------------------
        kernel = np.ones((2, 2), np.uint8)

        binary = cv2.morphologyEx(
            binary,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=1
        )

        # ---------------------------------
        # remove tiny noisy regions
        # ---------------------------------
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            255 - binary,
            connectivity=8
        )

        cleaned = np.ones_like(binary) * 255

        for i in range(1, num_labels):

            area = stats[i, cv2.CC_STAT_AREA]

            # remove tiny garbage
            if area < 12:
                continue

            cleaned[labels == i] = 0

        # ---------------------------------
        # mild sharpening
        # ---------------------------------
        blur = cv2.GaussianBlur(cleaned, (0, 0), 1.0)

        sharpened = cv2.addWeighted(
            cleaned,
            1.5,
            blur,
            -0.5,
            0
        )

        return sharpened