#C:\Users\ASUS\ocr_project\engines\easyocr_engine.py

easyocr_reader = easyocr.Reader(
    ['fa', 'en'],
    gpu=True
)
    results = easyocr_reader.readtext(
        np.array(img),
        detail=0,
        paragraph=True
    )
