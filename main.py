import os
import sys

from pipelines.image_pipeline import ImagePipeline
from pipelines.pdf_pipeline import PDFPipeline


def main():
    # Validate command-line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("python main.py <file_path>")
        return

    file_path = sys.argv[1]

    # Check if input file exists
    if not os.path.exists(file_path):
        print("[ERROR] File not found")
        return

    # Determine file type by extension
    ext = os.path.splitext(file_path)[1].lower()

    # Process image files
    if ext in [".jpg", ".jpeg", ".png", ".bmp"]:
        print("[INFO] Processing image...")
        text = ImagePipeline.process(file_path)

    # Process PDF files
    elif ext == ".pdf":
        print("[INFO] Processing PDF...")
        text = PDFPipeline.process(file_path)

    else:
        print("[ERROR] Unsupported file type")
        return

    # Save extracted text to output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Print completion message and output path
    print("\n====================")
    print("OCR COMPLETED")
    print("====================")
    print("\n[INFO] Saved to:")
    print(output_path)


if __name__ == "__main__":
    main()