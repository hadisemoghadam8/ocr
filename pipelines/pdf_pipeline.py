
# C:\Users\ASUS\ocr_project\pipelines\pdf_pipeline.py

from pdf2image import convert_from_path
import numpy as np

from pipelines.image_pipeline import ImagePipeline


class PDFPipeline:

    @staticmethod
    def process(pdf_path):
        from pdf2image import convert_from_path
        import numpy as np
        import cv2

        pages = convert_from_path(pdf_path, dpi=300)

        results = []

        for i, page in enumerate(pages):
            print(f"[INFO] Page {i+1}")

            image = np.array(page)

            temp_path = f"output/temp_page_{i}.jpg"
            page.save(temp_path)

            from pipelines.image_pipeline import ImagePipeline

            text = ImagePipeline.process(temp_path)

            results.append(text)

        return "\n\n".join(results)