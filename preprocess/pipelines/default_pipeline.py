#C:\Users\ASUS\ocr_project\preprocess\pipelines\default_pipeline.py

import cv2
import numpy as np


def process_default_image(image):

    # ---------------------------------
    # upscale سبک
    # ---------------------------------

    h, w = image.shape[:2]

    if max(h, w) < 1600:

        image = cv2.resize(
            image,
            None,
            fx=1.5,
            fy=1.5,
            interpolation=cv2.INTER_CUBIC
        )

    # ---------------------------------
    # denoise ملایم رنگی
    # ---------------------------------

    image = cv2.fastNlMeansDenoisingColored(
        image,
        None,
        3,
        3,
        7,
        21
    )

    # ---------------------------------
    # sharpen سبک
    # ---------------------------------

    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    image = cv2.filter2D(
        image,
        -1,
        kernel
    )

    # ---------------------------------
    # contrast enhancement سبک
    # ---------------------------------

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=1.5,
        tileGridSize=(8, 8)
    )

    l = clahe.apply(l)

    lab = cv2.merge([l, a, b])

    image = cv2.cvtColor(
        lab,
        cv2.COLOR_LAB2BGR
    )

    # ---------------------------------
    # مهم:
    # threshold نکن
    # grayscale نکن
    # ---------------------------------

    return image