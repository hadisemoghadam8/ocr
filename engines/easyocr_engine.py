#C:\Users\ASUS\ocr_project\engines\easyocr_engine.py
import easyocr  
import numpy as np 

reader = easyocr.Reader(['fa', 'en'], gpu=True)

def run_easyocr(img):
    results = reader.readtext(
        np.array(img),
        detail=0,
        paragraph=True
    )
    return results
