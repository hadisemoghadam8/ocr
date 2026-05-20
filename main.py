#C:\Users\ASUS\ocr_project\main.py

import os
import sys

from pipelines.image_pipeline import ImagePipeline
from pipelines.pdf_pipeline import PDFPipeline


def main():

    # ---------------------------------
    # Check input
    # ---------------------------------
    if len(sys.argv) < 2:

        print("Usage:")
        print("python main.py <file_path>")

        return

    file_path = sys.argv[1]

    # ---------------------------------
    # Check file exists
    # ---------------------------------
    if not os.path.exists(file_path):

        print("[ERROR] File not found")

        return

    # ---------------------------------
    # File extension
    # ---------------------------------
    ext = os.path.splitext(file_path)[1].lower()

    # ---------------------------------
    # Image OCR
    # ---------------------------------
    if ext in [".jpg", ".jpeg", ".png", ".bmp"]:

        print("[INFO] Processing image...")

        text = ImagePipeline.process(file_path)

    # ---------------------------------
    # PDF OCR
    # ---------------------------------
    elif ext == ".pdf":

        print("[INFO] Processing PDF...")

        text = PDFPipeline.process(file_path)

    else:

        print("[ERROR] Unsupported file type")

        return

    # ---------------------------------
    # Save output
    # ---------------------------------
    output_dir = "output"

    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(
        output_dir,
        "result.txt"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(text)

    # ---------------------------------
    # Done
    # ---------------------------------
    print("\n====================")
    print("OCR COMPLETED")
    print("====================")

    print(text[:1000])

    print("\n[INFO] Saved to:")
    print(output_path)


if __name__ == "__main__":
    main()