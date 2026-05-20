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
            ui_score > 0.7 and
            noise < 35 and
            contrast < 60 and
            edge_density < 0.12
        )

        if is_real_screenshot:
            print("[INFO] Using screenshot pipeline")
            return ScreenshotBooster.process(image)

        # ---------------------------------
        # Document detection
        # ---------------------------------
        is_document = (
            edge_density > 0.08 and
            blur_score > 100 and
            contrast > 25
        )

        if is_document:
            print("[INFO] Using document pipeline")
            return process_document_image(image)

        # ---------------------------------
        # Default
        # ---------------------------------
        print("[INFO] Using default pipeline")
        return process_default_image(image)