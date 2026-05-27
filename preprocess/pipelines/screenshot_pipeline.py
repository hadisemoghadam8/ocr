# # C:\Users\ASUS\ocr_project\preprocess\pipelines\screenshot_pipeline.py

# import cv2
# import numpy as np


# class ScreenshotBooster:

#     @staticmethod
#     def process(image):

#         h, w = image.shape[:2]

#         # فقط اگر تصویر کوچک است upscale کن
#         if max(h, w) < 1400:
#             image = cv2.resize(
#                 image,
#                 None,
#                 fx=2,
#                 fy=2,
#                 interpolation=cv2.INTER_CUBIC
#             )

#         # denoise خیلی سبک
#         image = cv2.fastNlMeansDenoisingColored(
#             image,
#             None,
#             2,
#             2,
#             5,
#             15
#         )

#         # contrast خیلی ملایم
#         lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
#         l, a, b = cv2.split(lab)

#         clahe = cv2.createCLAHE(
#             clipLimit=1.2,
#             tileGridSize=(8, 8)
#         )
#         l = clahe.apply(l)

#         lab = cv2.merge([l, a, b])
#         image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

#         # sharpen خیلی ملایم یا حتی حذف آن
#         blur = cv2.GaussianBlur(image, (0, 0), 0.8)
#         image = cv2.addWeighted(image, 1.08, blur, -0.08, 0)

#         return image

# C:\Users\ASUS\ocr_project\preprocess\pipelines\screenshot_pipeline.py

import cv2
import numpy as np


class ScreenshotBooster:

    @staticmethod
    def process(image):

        h, w = image.shape[:2]

        # فقط اگر تصویر کوچک است upscale کن
        if max(h, w) < 1400:
            image = cv2.resize(
                image,
                None,
                fx=2,
                fy=2,
                interpolation=cv2.INTER_CUBIC
            )

        # ✅ حذف فیزیکی نویزهای ریز و خطوط نازک کاذب (مثل _ اشتباهی)
        # این عملیات المان‌های خیلی کوچک را قبل از پردازش‌های بعدی پاک می‌کند
        kernel = np.ones((3, 3), np.uint8)
        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)

        # denoise خیلی سبک
        image = cv2.fastNlMeansDenoisingColored(
            image,
            None,
            2,
            2,
            5,
            15
        )

        # contrast خیلی ملایم
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(
            clipLimit=1.2,
            tileGridSize=(8, 8)
        )
        l = clahe.apply(l)

        lab = cv2.merge([l, a, b])
        image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # sharpen خیلی ملایم یا حتی حذف آن
        blur = cv2.GaussianBlur(image, (0, 0), 0.8)
        image = cv2.addWeighted(image, 1.08, blur, -0.08, 0)

        return image