# preprocess/router.py

from preprocess.pipelines.dark_pipeline import process_dark_image
from preprocess.pipelines.document_pipeline import process_document_image
from preprocess.pipelines.screenshot_pipeline import ScreenshotBooster
from preprocess.pipelines.default_pipeline import process_default_image


class PipelineRouter:

    @staticmethod
    def route(image, info):

        print("[INFO] Router analysis:")
        print(info)

        brightness = info["brightness"]
        contrast = info["contrast"]
        edge_density = info["edge_density"]
        noise = info["noise"]
        blur_score = info["blur_score"]
        ui_score = info["ui_score"]

        # ---------------------------------
        # Dark image
        # ---------------------------------
        if brightness < 70:
            print("[INFO] Using dark pipeline")
            return process_dark_image(image)

        # ---------------------------------
        # REAL screenshot detection
        # ---------------------------------
        is_real_screenshot = (
            ui_score >= 65 and
            noise < 35 and
            contrast < 60 and
            edge_density < 0.12
        )

        if is_real_screenshot:
            print("[INFO] Using screenshot pipeline")
            return ScreenshotBooster.process(image)




        text_heavy_scene = (
            edge_density > 0.09 and
            noise > 50 and
            contrast > 45
        )

        if text_heavy_scene:
            print("[INFO] Real-world text scene detected")
            return process_default_image(image)

        # ---------------------------------
        # REAL document detection
        # ---------------------------------

        is_document = (

            # لبه مناسب متن
            0.03 < edge_density < 0.10

            and

            # blur پایین
            blur_score > 180

            and

            # نویز کم
            noise < 40

            and

            # UI واقعی نباشد
            ui_score < 0.5

            and

            # کنتراست سند
            contrast > 35
        )
        # ---------------------------------
        # complex real-world scenes
        # ---------------------------------

        is_complex_scene = (

            # لبه‌های زیاد
            edge_density > 0.10

            and

            # نویز/جزئیات زیاد
            noise > 45

            and

            # UI خالص نیست
            ui_score < 0.85

            and

            # کنتراست طبیعی عکس
            contrast > 40
        )
        if is_complex_scene:
            print("[INFO] Complex scene detected")
            return process_default_image(image)

        if is_document:
            print("[INFO] Using document pipeline")
            return process_document_image(image)
        # ---------------------------------
        # Default
        # ---------------------------------
        print("[INFO] Using default pipeline")
        return process_default_image(image)