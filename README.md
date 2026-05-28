# Persian & English OCR Pipeline

A modular OCR pipeline for extracting and post-processing Persian (Farsi) and English text from images and PDF files.

The project combines multiple OCR engines, preprocessing pipelines, text correction modules, and RTL handling to improve OCR quality for mixed Persian-English documents.

---

# Features

* OCR support for:

  * Persian (Farsi)
  * English
  * Mixed Persian-English text

* Multiple OCR engines:

  * EasyOCR
  * Tesseract OCR

* Automatic preprocessing pipeline selection

* Image preprocessing for:

  * Documents
  * Screenshots
  * Dark UI images
  * Scene text

* Persian text post-processing:

  * RTL correction
  * Character normalization
  * Persian OCR cleanup

* English text cleanup and normalization

* PDF support

* Rotation and text-region utilities

---

# Project Structure

```text
ocr_project/
│
├── engines/                 # OCR engine wrappers
│   ├── easyocr_engine.py
│   ├── tesseract_engine.py
│   └── manager.py
│
├── pipelines/               # Main OCR pipelines
│   ├── image_pipeline.py
│   └── pdf_pipeline.py
│
├── preprocess/
│   ├── analyzer.py          # Image analysis
│   ├── router.py            # Pipeline selection
│   └── pipelines/
│       ├── dark_pipeline.py
│       ├── default_pipeline.py
│       ├── document_pipeline.py
│       ├── scene_text_pipeline.py
│       └── screenshot_pipeline.py
│
├── postprocess/
│   ├── clean_text.py
│   ├── english_fix.py
│   ├── normalize_numbers.py
│   ├── persian_fix.py
│   ├── rtl.py
│   └── scoring.py
│
├── utils/
│   ├── ocr_utils.py
│   ├── rotation.py
│   └── text_region.py
│
├── samples/                 # Sample input files
├── output/                  # OCR output files
│
├── Tesseract/               # Local Tesseract binaries
├── poppler-26.02.0/         # Poppler for PDF processing
│
├── main.py
├── requirements.txt
└── README.md
```

---

# Requirements

* Python 3.10.11

Main libraries:

* easyocr
* pytesseract
* opencv-python
* torch
* pdf2image
* pillow
* scikit-image

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Usage

Run OCR on an image or PDF:

```bash
python main.py
```

Input samples can be placed inside the `samples/` directory.

OCR results will be saved in the `output/` directory.

---

# OCR Engines

## EasyOCR

Used for flexible multilingual OCR and scene text detection.

## Tesseract OCR

Used for additional OCR accuracy and Persian language support.

Included trained data:

* `fas`
* `eng`

---

# Supported Inputs

* JPG
* PNG
* PDF

---

# Notes

* The project includes local Tesseract binaries.
* Poppler is included for PDF rendering.
* Designed and tested on Windows with Python 3.10.

---

# License

This project is for educational and research purposes.
