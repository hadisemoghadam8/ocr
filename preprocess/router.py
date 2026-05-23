# preprocess/router.py

from preprocess.pipelines.document_pipeline import process_document_image
from preprocess.pipelines.screenshot_pipeline import ScreenshotBooster
from preprocess.pipelines.scene_text_pipeline import process_scene_text_image
from preprocess.pipelines.default_pipeline import process_default_image
from preprocess.pipelines.dark_pipeline import process_dark_image

class PipelineRouter:

    @staticmethod
    def route(image, info):
        # مقداردهی اولیه امتیازات
        scores = {
            "dark": 0,
            "screenshot": 0,
            "scene": 0,
            "document": 0
        }

        brightness, contrast = info["brightness"], info["contrast"]
        edge_density, noise = info["edge_density"], info["noise"]
        blur_score, ui_score = info["blur_score"], info["ui_score"]

        # --- محاسبه امتیازها ---
        if brightness < 70 and ui_score >= 0.10:
            scores["dark"] += 10

        if ui_score > 0.12 and noise < 80 and edge_density < 0.15:
            scores["screenshot"] += 10

        if edge_density > 0.09 and noise > 50 and contrast > 45:
            scores["scene"] += 5

        if 0.03 < edge_density < 0.10 and blur_score > 180 and noise < 40 and ui_score < 0.5 and contrast > 35:
            scores["document"] += 10

        if edge_density > 0.10 and noise > 45 and ui_score < 0.85 and contrast > 40:
            scores["scene"] += 10 

        # --- انتخاب برنده ---
        best_choice = max(scores, key=scores.get)
        
        if scores[best_choice] > 0:
            if best_choice == "dark":
                print("[INFO] Selected: Dark UI pipeline")
                return {"image": process_dark_image(image), "scene_text": False, "screenshot": True, "dark_mode": False}
            
            elif best_choice == "screenshot":
                print("[INFO] Selected: Screenshot pipeline")
                return {"image": ScreenshotBooster.process(image), "scene_text": False, "screenshot": True}
            
            elif best_choice == "scene":
                print("[INFO] Selected: Scene text pipeline")
                return {"image": process_scene_text_image(image), "scene_text": True}
            
            elif best_choice == "document":
                print("[INFO] Selected: Document pipeline")
                return {"image": process_document_image(image), "scene_text": False}

        # پیش‌فرض
        print("[INFO] Selected: Default pipeline")
        return {
            "image": process_default_image(image),
            "scene_text": False,
            "screenshot": False,
            "dark_mode": False
        }
