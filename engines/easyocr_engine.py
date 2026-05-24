# C:\Users\ASUS\ocr_project\engines\easyocr_engine.py
import easyocr
import numpy as np

reader = easyocr.Reader(['fa', 'en'], gpu=False, verbose=False)

def run_easyocr(img, paragraph=True, text_threshold=0.5, low_text=0.25, min_size=8, **kwargs):
    kwargs.pop('lang', None)
    
    results = reader.readtext(
        np.array(img),
        detail=1,  
        paragraph=paragraph,
        text_threshold=text_threshold,
        low_text=low_text,
        min_size=min_size,
        **kwargs
    )
    
    # 🔍 لاگ‌گیری ایمن (سازگار با paragraph=True و False)
    handle_found = False
    for item in results:
        # در حالت paragraph=False: 3 آیتم (bbox, text, conf)
        # در حالت paragraph=True:  2 آیتم (bbox, text)
        text = item[1]
        conf = item[2] if len(item) > 2 else 1.0
        
        if '@' in text or 'fateme' in text.lower() or 'daniyali' in text.lower():
            print(f"[DEBUG] 🔍 Handle detected -> Text: '{text}' | Confidence: {conf:.3f}")
            handle_found = True
            
    if not handle_found:
        print("[DEBUG] ⚠️ Engine did NOT detect '@fatemedaniyali' in raw output.")
        print("[DEBUG] 📦 First 3 raw items:", results[:3])
    
    # 🔄 تبدیل به فرمت استاندارد برای manager.py
    return [item[1] for item in results]