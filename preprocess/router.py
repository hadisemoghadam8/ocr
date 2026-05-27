# preprocess/router.py

from preprocess.pipelines.document_pipeline import process_document_image
from preprocess.pipelines.screenshot_pipeline import ScreenshotBooster
from preprocess.pipelines.scene_text_pipeline import process_scene_text_image
from preprocess.pipelines.default_pipeline import process_default_image
from preprocess.pipelines.dark_pipeline import process_dark_image


class PipelineRouter:
    """
    Selects the optimal preprocessing pipeline based on image characteristics.
    """

    @staticmethod
    def route(image, info):
        """
        Route an image to the most suitable preprocessing pipeline.

        Args:
            image: Input image array.
            info: Dictionary of image metrics from ImageAnalyzer.

        Returns:
            Dictionary containing the processed image and pipeline flags.
        """
        scores = {
            "dark": 0,
            "screenshot": 0,
            "scene": 0,
            "document": 0
        }

        brightness = info["brightness"]
        contrast = info["contrast"]
        edge_density = info["edge_density"]
        noise = info["noise"]
        blur_score = info["blur_score"]
        ui_score = info["ui_score"]

        # Score for dark UI images: low brightness with UI elements present
        if brightness < 70 and ui_score >= 0.10:
            scores["dark"] += 10

        # Score for screenshots: high UI score, low noise, moderate edge density
        if ui_score > 0.12 and noise < 80 and edge_density < 0.15:
            scores["screenshot"] += 10

        # Score for scene text: high edge density and noise indicate complex backgrounds
        if edge_density > 0.09 and noise > 50 and contrast > 45:
            scores["scene"] += 5

        # Score for clean documents: moderate edges, low noise, high sharpness
        if 0.03 < edge_density < 0.10 and blur_score > 180 and noise < 40 and ui_score < 0.5 and contrast > 35:
            scores["document"] += 10

        # Additional scene text signal: high complexity but not a full UI screenshot
        if edge_density > 0.10 and noise > 45 and ui_score < 0.85 and contrast > 40:
            scores["scene"] += 10

        # Select the pipeline with the highest score
        best_choice = max(scores, key=scores.get)

        if scores[best_choice] > 0:
            if best_choice == "dark":
                print("[INFO] Selected: Dark UI pipeline")
                return {
                    "image": process_dark_image(image),
                    "scene_text": False,
                    "screenshot": True,
                    "dark_mode": False
                }

            elif best_choice == "screenshot":
                print("[INFO] Selected: Screenshot pipeline")
                return {
                    "image": ScreenshotBooster.process(image),
                    "scene_text": False,
                    "screenshot": True
                }

            elif best_choice == "scene":
                print("[INFO] Selected: Scene text pipeline")
                return {
                    "image": process_scene_text_image(image),
                    "scene_text": True
                }

            elif best_choice == "document":
                print("[INFO] Selected: Document pipeline")
                return {
                    "image": process_document_image(image),
                    "scene_text": False
                }

        # Fallback to default preprocessing if no pipeline scored positively
        print("[INFO] Selected: Default pipeline")
        return {
            "image": process_default_image(image),
            "scene_text": False,
            "screenshot": False,
            "dark_mode": False
        }