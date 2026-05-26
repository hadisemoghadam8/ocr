# preprocess/pipelines/scene_text_pipeline.py

import cv2
import numpy as np


def process_scene_text_image(image):
    h, w = image.shape[:2]

    # 1) upscale stronger for tiny text
    if max(h, w) < 1800:
        image = cv2.resize(
            image,
            None,
            fx=3,
            fy=3,
            interpolation=cv2.INTER_LANCZOS4
        )

    # 2) edge-preserving denoise
    image = cv2.bilateralFilter(image, 7, 35, 35)

    # 3) mild contrast on luminance only
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=1.4,
        tileGridSize=(4, 4)
    )
    l = clahe.apply(l)

    image = cv2.cvtColor(
        cv2.merge([l, a, b]),
        cv2.COLOR_LAB2BGR
    )

    # 4) very light sharpening or remove it completely
    blur = cv2.GaussianBlur(image, (0, 0), 0.8)
    image = cv2.addWeighted(image, 1.04, blur, -0.04, 0)

    return image