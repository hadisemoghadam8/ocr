# preprocess/pipelines/scene_text_pipeline.py
#پس زمینه شلوغ
import cv2
import numpy as np


def process_scene_text_image(image):

    # ---------------------------------
    # upscale
    # ---------------------------------

    h, w = image.shape[:2]

    if max(h, w) < 1400:

        image = cv2.resize(
            image,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

    # ---------------------------------
    # denoise light
    # ---------------------------------

    image = cv2.fastNlMeansDenoisingColored(
        image,
        None,
        2,
        2,
        5,
        15
    )

    # ---------------------------------
    # LAB contrast
    # ---------------------------------

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    l = clahe.apply(l)

    lab = cv2.merge([l, a, b])

    image = cv2.cvtColor(
        lab,
        cv2.COLOR_LAB2BGR
    )

    # ---------------------------------
    # text sharpening
    # ---------------------------------

    blur = cv2.GaussianBlur(
        image,
        (0, 0),
        1.0
    )

    image = cv2.addWeighted(
        image,
        1.12,
        blur,
        -0.12,
        0
    )

    return image