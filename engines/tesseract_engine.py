#C:\Users\ASUS\ocr_project\engines\tesseract_engine.py

tesseract_text = pytesseract.image_to_string(
                img,
                lang="fas+eng",
                config=f"--oem 3 --psm {psm}"
            )